import argparse
import json
import os

def is_json_file(file_path):
    
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return False


    try:
        with open(file_path, 'r') as f:
            json.load(f)
        print(f"'{file_path}' is a valid JSON file.")
        return True
    except json.JSONDecodeError:
        print(f"'{file_path}' is NOT a valid JSON file.")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

if __name__ == "__main__":

    parse = argparse.ArgumentParser(description ="json file validator")

    parse.add_argument("file",help= "json file")
    args= parse.parse.args()

    is_json_file(args.file)
