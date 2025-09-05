import json
import os


def find_files_with_extension(directory: str, extension: str) -> list[str]:
    """
    Retrieve all files with the specified extension in the given directory.

    Parameters:
    - directory (str): The path to the directory to search.
    - extension (str): The file extension (e.g., 'txt', 'py') without the leading dot.

    Returns:
    - list: A list of full file paths that match the extension.
    """
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.endswith(extension):
            files.append(file_path)
    return files


def return_json_files(directory):
    """
    Extracts and parses all valid JSON files from the given directory.

    Args:
        directory (str): Path to the directory containing JSON files.

    Returns:
        list: A list of parsed JSON data (dicts, lists, etc.) from each JSON file.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The directory '{directory}' does not exist.")

    json_data = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Ensure the item is a file and has a .json extension
        if os.path.isfile(file_path) and filename.endswith('.json'):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    json_data.append(data)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error reading '{filename}': {e}")

    return json_data
