import json
import os
import glob

def check_vocab_files():
    vocab_dir = r"src\_data\vocab"
    json_files = glob.glob(os.path.join(vocab_dir, "*.json"))
    
    all_good = True
    for json_file in json_files:
        print(f"Checking: {os.path.basename(json_file)}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            items = data.get("vocab_items", [])
            for i, item in enumerate(items):
                translation = item.get("translation")
                explanation = item.get("explanation")
                original = item.get("original")
                
                # Check for missing or TODO values
                if not translation or "TODO" in translation or translation == "undefined":
                    print(f"  [!] Missing translation for '{original}' (Item {i+1})")
                    all_good = False
                if not explanation or "TODO" in explanation or explanation == "undefined":
                    print(f"  [!] Missing explanation for '{original}' (Item {i+1})")
                    all_good = False
                    
    if all_good:
        print("\nAll vocabulary items have translations and explanations!")
    else:
        print("\nFound issues in the vocabulary files.")

if __name__ == "__main__":
    check_vocab_files()
