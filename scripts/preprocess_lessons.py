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
            "explanation": "待加入說明"
        }
    except Exception as e:
        print(f"Translation Error for '{phrase}': {e}")
        return {
            "translation": "Error",
            "explanation": f"Translation failed: {e}"
        }

def extract_keywords_from_markdown(content):
    """Simple parser to extract items from the # Keywords: section."""
    keywords = []
    # Match the section starting with # Keywords: or # Keywords: (with emoji)
    match = re.search(r'# Keywords:\s*(.*?)(?=\s*# Questions:|\s*---|$)', content, re.DOTALL | re.IGNORECASE)
    if match:
        section = match.group(1)
        # Look for lines like "word - translation" or "word: translation"
        # or just "word" at the start of a line
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'): continue
            
            # Pattern: "word - translation" or "word – translation" or "word — translation"
            parts = re.split(r'\s*[-–—]\s*', line)
            if len(parts) >= 2:
                word = parts[0].strip().rstrip(':').strip('*_')
                translation = parts[1].strip()
                if word:
                    keywords.append({
                        "original": word,
                        "display": word,
                        "type": "vocabulary",
                        "translation": translation,
                        "sentence": "" # We'll try to find a sentence later or leave blank
                    })
            elif ':' in line:
                parts = line.split(':', 1)
                word = parts[0].strip().strip('*_')
                translation = parts[1].strip()
                if word:
                    keywords.append({
                        "original": word,
                        "display": word,
                        "type": "vocabulary",
                        "translation": translation,
                        "sentence": ""
                    })
    return keywords

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
    
    # Also extract manual keywords
    keywords = extract_keywords_from_markdown(content)
    for kw in keywords:
        # Try to find a sentence for the keyword
        for sent in doc.sents:
            if kw['original'].lower() in sent.text.lower():
                kw['sentence'] = sent.text.strip()
                break
        vocab_items.append(kw)
    
    # De-duplicate identical phrases in the same lesson 
    # (to avoid excessive API calls for the same verb in the same context)
    unique_items = {}
    for item in vocab_items:
        key = (item['original'], item['sentence'])
        if key not in unique_items:
            unique_items[key] = item
            
    # Define paths
    filename = os.path.basename(filepath).replace(".md", "").lower().replace(" ", "-").replace("’", "").replace("'", "")
    output_dir = r"c:\Users\Admin\code\eleventy\src\_data\vocab"
    os.makedirs(output_dir, exist_ok=True)

    # Load existing results to preserve ALL manual edits
    # We use a dict with (original, sentence) as key
    combined_items = {}
    output_path = os.path.join(output_dir, f"{filename}.json")
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
                items_list = old_data.get("vocab_items", old_data.get("items", []))
                for it in items_list:
                    key = (it['original'], it['sentence'])
                    combined_items[key] = it
        except Exception as e:
            print(f"  Warning: Could not load existing JSON: {e}")

    # Add/Update with newly detected items
    total = len(unique_items)
    for i, (key, new_item) in enumerate(unique_items.items(), 1):
        if key in combined_items:
            # If it already exists, only update if the existing one is a TODO or missing explanation
            if combined_items[key].get('explanation') in ["TODO: Add explanation", "", None]:
                 print(f"  [{i}/{total}] Updating TODO for: {new_item['display']}")
                 translation_data = get_automatic_translation(new_item['original'], new_item['sentence'])
                 # Keep the translation from the markdown if it was already there
                 if new_item.get('translation') and combined_items[key].get('translation') == "Error":
                      combined_items[key]['translation'] = new_item['translation']
                 combined_items[key]['explanation'] = translation_data['explanation']
            else:
                 print(f"  [{i}/{total}] Preserving manual edit for: {new_item['display']}")
        else:
            # brand new item
            print(f"  [{i}/{total}] Adding new item: {new_item['display']}")
            # If it's a keyword from markdown, it might already have a translation
            if new_item.get('translation') and new_item['translation'] != "Error":
                new_item['explanation'] = "TODO: Add explanation"
            else:
                translation_data = get_automatic_translation(new_item['original'], new_item['sentence'])
                new_item.update(translation_data)
            combined_items[key] = new_item
    
    # Save the combined results
    final_results = list(combined_items.values())
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"vocab_items": final_results}, f, ensure_ascii=False, indent=2)
    
    print(f"  Saved to: {output_path}")

if __name__ == "__main__":
    lessons_dir = r"c:\Users\Admin\code\eleventy\src\lessons"
    lesson_files = glob.glob(os.path.join(lessons_dir, "*.md"))
    
    for lesson in lesson_files:
        process_lesson(lesson)
    
    print("\nAll lessons processed successfully!")
