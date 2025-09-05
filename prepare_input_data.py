import polars as pl
from datetime import timedelta


_PAIRED_DATA = 2

if _PAIRED_DATA == 1:
    EPIC_SPLICED_DATA = ''
    PAIRED_OUT_PATH = ''
elif _PAIRED_DATA == 2:
    EPIC_SPLICED_DATA = ''
    PAIRED_OUT_PATH = ''


def filter_within_num_days(df: pl.DataFrame, col_name: str, num_days: int):
    # 1) Robust, dtype-agnostic coercion to Date
    #    - First: try direct cast (works for datetime[ms] → date)
    #    - Fallbacks: parse common string formats after casting to Utf8
    df2 = (
        df.with_columns(
            pl.coalesce([
                pl.col(col_name).cast(pl.Date, strict=False),  # handles datetime-like input
                pl.col(col_name).cast(pl.Utf8).str.strptime(pl.Date, "%m/%d/%Y", strict=False),
                # Optional extra fallback if you sometimes have time in the string:
                pl.col(col_name).cast(pl.Utf8).str.strptime(pl.Date, "%m/%d/%Y %H:%M:%S", strict=False),
            ]).alias(col_name)
        )
        .drop_nulls([col_name])  # drop rows that still failed to parse
        .sort(col_name)
    )

    # 2) Two-pointer to find the largest subset within a 60-day span
    dates = df2[col_name].to_list()
    i = best_i = best_j = 0
    for j in range(len(dates)):
        while dates[j] - dates[i] > timedelta(days=num_days):
            i += 1
        if j - i > best_j - best_i:
            best_i, best_j = i, j

    start, end = dates[best_i], dates[best_j]

    # 3) Subset rows in the winning window (inclusive)
    subset = df2.filter(pl.col(col_name).is_between(start, end, closed="both"))
    
    return subset


def filter_by_specimen_date(df: pl.DataFrame):
    # Separate the DataFrame into 'Blood' and 'Tissue' subsets
    df_blood = df.filter(pl.col('Specimen Type') == 'Blood').select(['Specimen Name', 'Collection Date and Time'])
    df_tissue = df.filter(pl.col('Specimen Type') == 'Tissue').select(['Specimen Name', 'Collection Date and Time'])

    # Perform a cross-join to get all possible pairs
    pairs_df = df_blood.join(df_tissue, how='cross')

    # Calculate the absolute time difference between the collection dates for each pair
    pairs_df = pairs_df.with_columns(
        time_diff = (pl.col('Collection Date and Time_right') - pl.col('Collection Date and Time')).abs()
    )

    # Rename columns for clarity
    pairs_df = pairs_df.rename({'Specimen Name': 'Blood Specimen Name', 'Collection Date and Time': 'Blood Collection Date',
                                'Specimen Name_right': 'Tissue Specimen Name', 'Collection Date and Time_right': 'Tissue Collection Date'})

    # Find the pair with the closest collection dates
    closest_pair = pairs_df.sort('time_diff').head(1)

    # Find the pair with the farthest collection dates
    farthest_pair = pairs_df.sort('time_diff', descending=True).head(1)

    return {
        'closest_pair': closest_pair,
        'farthest_pair': farthest_pair
    }


if __name__=='__main__':
    df = pl.read_excel(EPIC_SPLICED_DATA, engine='calamine')

    MARKER_2024 = "GUIDE TO STANDARDIZED NOMENCLATURE AND EXPLANATION OF CHANGES:"
    MARKER_2025 = 'D.  CLINICAL INTERPRETATION'

    df = pl.read_excel(EPIC_SPLICED_DATA)
    check_col = '__UNNAMED__14'
    if check_col in df.columns:
        df = df.drop(check_col)

    df = df.with_columns(
        ngs_report=pl.when(pl.col('Value').str.contains(MARKER_2024))
        .then(pl.col('Value').str.split(MARKER_2024))
        .otherwise(pl.col('Value').str.split(MARKER_2025))
        .list.get(0)
        .cast(pl.String)
    ).drop('Value')
    df = df.drop_nulls(subset=["ngs_report", "First Final Verify Date and Time"])

    grouped_df = df.group_by(pl.col('MRN'))

    count = 0
    for name, sub_df in grouped_df:
        if sub_df.shape[0] > 1:
            st = sub_df.select('Specimen Type').unique()
            if len(st) == 2:
                # print(f'{name}: {sub_df['Collection Date and Time']} / {sub_df['Specimen Type']}\n\n')
                save_fp = f'{PAIRED_OUT_PATH}/MRN_{name[0]}.json'
                if len(sub_df) > 2:
                    # print(sub_df.glimpse())
                    # Filter the DataFrame to get the closest pair
                    pairs = filter_by_specimen_date(sub_df)
                    closest_pair = pairs['closest_pair']
                    lb_case_num = closest_pair.select('Blood Specimen Name').item()
                    st_case_num = closest_pair.select('Tissue Specimen Name').item()
                    # print(st_case_num, lb_case_num)
                    sub_df = df.filter(pl.col('Specimen Name').is_in([st_case_num, lb_case_num]))
                    # print(sub_df)
                    
                sub_df.write_json(save_fp)
                count += 1
                    
    print(f'number of paired (==2) data: {count}')
