import dspy
import pickle
import time

from dspy.adapters.baml_adapter import BAMLAdapter

from signatures_mapp import ExtractAll
from struct_mapp import MAPPExtractResults
from utils import return_json_files


# TODO: Make this argparse/CLI
_PAIRED_DATA = 2

if _PAIRED_DATA == 1:
    JSON_DIR = ''
    OUTPUT_DIR = ''
elif _PAIRED_DATA == 2:
    JSON_DIR = ''
    OUTPUT_DIR = ''


def main():

    paired_cases = return_json_files(directory=JSON_DIR)
    all_cases = [item for sublist in paired_cases for item in sublist]

    ## LM models ##
    model = "openai/QuantTrio/Qwen3-30B-A3B-Instruct-2507-GPTQ-Int8"

    ## LM configs ##
    TEMP = 0.7
    TOP_P = 0.8
    TOP_K = 20
    MIN_P = 0.0
    MAX_TOKENS = 8096  # output tokens to generate
    
    ## Init LM
    lm = dspy.LM(
        model,
        api_base="http://localhost:8000/v1",  # ensure this points to your port
        api_key="local", 
        model_type="chat",
        temperature=TEMP,
        max_tokens=MAX_TOKENS,
        # Pass the arguments that your provider/server (in this case vLLM) recognizes, in the constructor to dspy.LM
        top_p=TOP_P,
        top_k=TOP_K,
        min_p=MIN_P
        )
    dspy.configure(lm=lm, adapter=BAMLAdapter())
    field_extractor = ExtractAll()

    start_t = time.time()
    counter = 0
    print(f"NUMBER OF CASES: {len(all_cases)} ({len(paired_cases)} paired cases)")
    for i, c in enumerate(all_cases):
        counter += 1
        if len(all_cases) % 100 == 0:
                print(f"Current report number {counter+1}. Time elapsed so far: {time.time() - start_t} seconds")

        collection_date = c['Collection Date and Time']
        specimen_source = c['Specimen Type']
        
        ngs_report = c['ngs_report']

        case_results = field_extractor(ngs_report=ngs_report)

        structured_output = MAPPExtractResults(
            mrn=case_results['mrn'],
            date=collection_date,
            mdl_num=case_results['mdl'],
            assay=specimen_source,
            cancer_type=case_results['ct'],
            primary_met=case_results['met'],
            nccn_category=case_results['cc'],
            tumor_purity=case_results['tp'],
            tmb=case_results['tmb'],
            msi=case_results['msi'],
            copy_number=case_results['cnv'],
            fusions=case_results['fusion'],
            somatic_muts=case_results['sm'],
        )
        
        filename = f"{OUTPUT_DIR}/Report-{i}_MRN-{case_results['mrn']}_{case_results['mdl']}_{specimen_source}.pkl"

        final_results = {
             'report': ngs_report,
             'extracts': structured_output
        }

        with open(filename, 'wb') as f:
            pickle.dump(final_results, f)

    print(f"Time elapsed for {len(all_cases)} cases: {time.time() - start_t} s")
    
    dspy.inspect_history(n=10)


if __name__=='__main__':
     main()
