import re
import os

file_path = r'C:\Users\Admin\code\eleventy\src\pages\secret-lesson.md'

def is_pinyin(line):
    # Pinyin with tone marks
    if any(c in 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ' for c in line):
        return True
    # Sometimes pinyin might not have tone marks but it's usually just a few words
    # However, English lines are longer and have normal punctuation.
    return False

def is_hanzi(line):
    return any('\u4e00' <= c <= '\u9fff' for c in line)

def is_english(line):
    stripped = line.strip()
    if not stripped: return False
    if is_hanzi(line): return False
    if is_pinyin(line): return False
    # Check if it has many latin characters and no tone marks
    latin_chars = sum(1 for c in stripped if 'a' <= c.lower() <= 'z')
    if latin_chars > 0:
        return True
    return False

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_tag = '<div class="lesson-text">'
end_tag = '</div>'
start_idx = content.find(start_tag) + len(start_tag)
end_idx = content.find(end_tag, start_idx)

prefix = content[:start_idx]
lesson_text = content[start_idx:end_idx]
suffix = content[end_idx:]

# We need to preserve empty lines and separators
# Split by lines and group into non-empty blocks
lines = lesson_text.split('\n')
new_lines = []
current_block = []

def process_block(block):
    # block is a list of lines
    if len(block) == 3:
        # Check for [Hanzi, English, Pinyin]
        # Line 0 should be Hanzi
        # Line 1 could be English or Pinyin
        # Line 2 could be English or Pinyin
        
        l0, l1, l2 = block
        
        if is_hanzi(l0):
            if is_english(l1) and is_pinyin(l2):
                print(f"Swapping: {l0.strip()}")
                return [l0, l2, l1]
            elif is_pinyin(l1) and is_english(l2):
                # Already correct
                return block
            elif is_pinyin(l2): # If l2 is pinyin and l1 is not pinyin, swap
                 print(f"Swapping (fallback): {l0.strip()}")
                 return [l0, l2, l1]
    return block

for line in lines:
    if line.strip() == '' or line.strip() == '—':
        if current_block:
            new_lines.extend(process_block(current_block))
            current_block = []
        new_lines.append(line)
    else:
        current_block.append(line)

if current_block:
    new_lines.extend(process_block(current_block))

new_lesson_text = '\n'.join(new_lines)
final_content = prefix + new_lesson_text + suffix

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(final_content)

print("Done.")
