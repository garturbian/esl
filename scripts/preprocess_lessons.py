import os
import spacy
import json
import re
import glob
from spacy.matcher import Matcher

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("Downloading spaCy model...")
    os.system("python -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")

def get_matcher(nlp):
    matcher = Matcher(nlp.vocab)
    
    # Common non-idiomatic prepositions to filter out for basic verbs
    basic_verbs = ["go", "come", "sit", "run", "look", "see", "want", "need", "like"]
    common_adps = ["to", "at", "on", "in", "next", "behind", "from", "with", "for"]

    # Phrasal Verb Patterns
    patterns = [
        # Verb + Particle (usually idiomatic, e.g., "hang up", "pick up", "jump out")
        [{"POS": "VERB"}, {"POS": "PART"}],
        # Verb + ADP (Filtering out very basic ones like "sit next to", "run to")
        [{"POS": "VERB", "LOWER": {"NOT_IN": basic_verbs}}, {"POS": "ADP", "LOWER": {"NOT_IN": common_adps}}],
        # Specific interesting combinations even with basic verbs
        [{"LOWER": "look"}, {"LOWER": "for"}],
        [{"LOWER": "look"}, {"LOWER": "after"}],
        [{"LOWER": "get"}, {"LOWER": "by"}],
        [{"LOWER": "get"}, {"LOWER": "along"}],
        # Split Phrasal Verbs
        [{"POS": "VERB"}, {"POS": "PRON"}, {"POS": "PART"}],
        [{"POS": "VERB"}, {"POS": "DET", "OP": "?"}, {"POS": "NOUN", "OP": "+"}, {"POS": "PART"}],
    ]
    matcher.add("PHRASAL_VERB", patterns)
    
    # Idiom Patterns
    idiom_patterns = [
        [{"LOWER": "get"}, {"LOWER": "up"}, {"LOWER": "close"}],
        [{"LOWER": "once"}, {"LOWER": "upon"}, {"LOWER": "a"}, {"LOWER": "time"}],
        [{"LOWER": "wrong"}, {"LOWER": "number"}],
        [{"LOWER": "hang"}, {"LOWER": "out"}],
    ]
    matcher.add("IDIOM", idiom_patterns)
    
    return matcher

def identify_items(doc, matcher):
    matches = matcher(doc)
    items = []
    seen_spans = set()
    
    for match_id, start, end in matches:
        span = doc[start:end]
        label = nlp.vocab.strings[match_id]
        
        span_key = (start, end) # Ignore label for overlap check
        if any(start >= s and end <= e for s, e in seen_spans):
            continue
        seen_spans.add(span_key)
        
        if label == "PHRASAL_VERB":
            verb = next((t for t in span if t.pos_ == "VERB"), span[0])
            particle = next((t for t in span if t.pos_ in ["PART", "ADP"]), span[-1])
            original = f"{verb.lemma_} {particle.lemma_}"
        else:
            original = span.text.lower()

        items.append({
            "original": original,
            "display": span.text.strip(),
            "type": label.lower(),
            "sentence": span.sent.text.strip()
        })
    return items

def extract_keywords_from_markdown(content):
    keywords = []
    match = re.search(r'# Keywords:\s*(.*?)(?=\s*#|$)', content, re.DOTALL | re.IGNORECASE)
    if not match:
        return keywords
        
    section = match.group(1)
    lines = section.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'): continue
        
        m = re.match(r'^(?:[-\*\+]\s*)?(?:\*\*)?([^\-\:]+?)(?:\*\*)?\s*[\-\:]\s*(.+)$', line)
        if m:
            word = m.group(1).strip()
            translation = m.group(2).strip().rstrip('\\').strip()
            if word and translation:
                keywords.append({
                    "original": word.lower(),
                    "display": word,
                    "type": "vocabulary",
                    "translation": translation,
                    "sentence": ""
                })
    return keywords

def process_lesson(filepath, matcher):
    print(f"--- Processing: {os.path.basename(filepath)} ---")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    text_content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
    text_content = re.sub(r'\{%.*?%\}', '', text_content)
    text_content = re.sub(r'\[.*?\]\(.*?\)', '', text_content)
    text_content = re.sub(r'\!\[.*?\]\(.*?\)', '', text_content)
    
    doc = nlp(text_content)
    detected_items = identify_items(doc, matcher)
    manual_keywords = extract_keywords_from_markdown(content)
    
    all_items = {}
    
    # Priority 1: Manual Keywords
    for kw in manual_keywords:
        for sent in doc.sents:
            if kw['original'].lower() in sent.text.lower():
                kw['sentence'] = sent.text.strip()
                break
        all_items[kw['original']] = kw # Key by 'original' to prevent duplicates

    # Priority 2: Detected Items
    for item in detected_items:
        if item['original'] not in all_items:
            all_items[item['original']] = item

    filename = os.path.basename(filepath).replace(".md", "").lower().replace(" ", "-").replace("’", "").replace("'", "")
    output_dir = r"src\_data\vocab"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{filename}.json")
    
    existing_items = {}
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                items = data.get("vocab_items", [])
                for it in items:
                    existing_items[it['original']] = it
        except: pass

    final_vocab = []
    for orig, item in all_items.items():
        if orig in existing_items:
            old_item = existing_items[orig]
            if old_item.get('explanation') and "TODO" not in old_item['explanation'] and old_item['explanation'] != "待加入說明":
                # Only update sentence/display if they are missing
                if not old_item.get('sentence'): old_item['sentence'] = item['sentence']
                final_vocab.append(old_item)
                continue
        
        if 'translation' not in item: item['translation'] = "TODO: Translate"
        if 'explanation' not in item: item['explanation'] = "TODO: Explain"
        final_vocab.append(item)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"vocab_items": final_vocab}, f, ensure_ascii=False, indent=2)
    print(f"  Updated: {output_path} ({len(final_vocab)} items)")

if __name__ == "__main__":
    matcher = get_matcher(nlp)
    lessons_dir = r"src\lessons"
    lesson_files = glob.glob(os.path.join(lessons_dir, "*.md"))
    for lesson in lesson_files:
        process_lesson(lesson, matcher)
