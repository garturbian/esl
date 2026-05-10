import re
import sys

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    for i, line in enumerate(lines):
        orig = line.strip()
        if not orig or orig.startswith('---') or orig.startswith('layout:') or orig.startswith('title:') or orig.startswith('eleventyExcludeFromCollections:'):
            continue
        if orig == '—':
            continue
        if re.search(r'[\u4e00-\u9fff]', orig):
            continue # Chinese
        if re.search(r'[āáǎàōóǒòēéěèīíǐìūúǔùǖǘǚǜü]', orig):
            continue # Pinyin
        if re.search(r'[，。！？]', orig):
            continue # Chinese Punctuation
        
        # It's an English line
        # Remove trailing spaces/newlines and append 2 spaces + newline
        new_line = line.rstrip() + '  \n'
        if lines[i] != new_line:
            lines[i] = new_line
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("File updated.")
    else:
        print("No changes needed.")

if __name__ == '__main__':
    fix_file('src/pages/fastest-chinese-learners.md')
