import os
import spacy
import json
import re
import glob
from deep_translator import GoogleTranslator

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")

def identify_phrasal_verbs(doc):
    """Identifies phrasal verbs, avoiding duplicates and cleaning overlaps."""
    items = []
    seen_indices = set()
    
    for token in doc:
        if token.dep_ == "prt" and token.head.pos_ == "VERB":
            verb = token.head
            particle = token
            
            # Start and End indices in the token stream
            start_i = min(verb.i, particle.i)
            end_i = max(verb.i, particle.i) + 1
            
            # Key to avoid processing the same occurrence twice
            occ_key = (verb.i, particle.i)
            if occ_key in seen_indices:
                continue
            seen_indices.add(occ_key)
            
            full_span = doc[start_i:end_i]
            
            items.append({
                "original": f"{verb.lemma_} {particle.lemma_}",
                "display": full_span.text.strip(),
                "type": "phrasal_verb",
                "sentence": verb.sent.text.strip()
            })
    return items

def get_automatic_translation(phrase, sentence):
    """Provides automatic translation using deep-translator."""
    try:
        # Use GoogleTranslator for zh-TW
        translation = GoogleTranslator(source='auto', target='zh-TW').translate(phrase)
        return {
            "translation": translation,
            "explanation": "TODO: Add explanation"
        }
    except Exception as e:
        print(f"Translation Error for '{phrase}': {e}")
        return {
            "translation": "Error",
            "explanation": f"Translation failed: {e}"
        }

def process_lesson(filepath):
    """Processes a single lesson file and saves JSON."""
    print(f"--- Processing: {os.path.basename(filepath)} ---")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Strip front matter
    text_content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
    
    # Also strip code blocks and common Eleventy shortcodes
    text_content = re.sub(r'\{%.*?%\}', '', text_content)
    
    doc = nlp(text_content)
    vocab_items = identify_phrasal_verbs(doc)
    
    # De-duplicate identical phrases in the same lesson 
    # (to avoid excessive API calls for the same verb in the same context)
    unique_items = {}
    for item in vocab_items:
        key = (item['original'], item['sentence'])
        if key not in unique_items:
            unique_items[key] = item
            
    # Load existing results to preserve manual edits
    existing_items = {}
    output_path = os.path.join(output_dir, f"{filename}.json")
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                items_list = old_data.get("vocab_items", old_data.get("items", []))
                for it in items_list:
                    # Use (original, sentence) as key to match context
                    key = (it['original'], it['sentence'])
                    existing_items[key] = it
        except Exception as e:
            print(f"  Warning: Could not load existing JSON: {e}")

    results = []
    total = len(unique_items)
    for i, (key, item) in enumerate(unique_items.items(), 1):
        # If we have an existing item with the same key and it has a real explanation, use it
        if key in existing_items and existing_items[key].get('explanation') != "TODO: Add explanation":
            print(f"  [{i}/{total}] Preserving manual edit for: {item['display']}")
            item.update({
                "translation": existing_items[key].get('translation', item.get('translation', '')),
                "explanation": existing_items[key]['explanation']
            })
        else:
            print(f"  [{i}/{total}] Translating automatically: {item['display']}")
            translation_data = get_automatic_translation(item['original'], item['sentence'])
            item.update(translation_data)
        
        results.append(item)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"vocab_items": results}, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved to: {output_path}")

if __name__ == "__main__":
    lessons_dir = r"c:\Users\Admin\code\eleventy\src\lessons"
    lesson_files = glob.glob(os.path.join(lessons_dir, "*.md"))
    
    for lesson in lesson_files:
        process_lesson(lesson)
    
    print("\nAll lessons processed successfully!")
