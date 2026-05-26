import os
import codecs

dest_dir = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\_posts"
user_file = os.path.join(dest_dir, "Tuần 2 - Hacking Kubernetes (Part 1).md")
target_file = os.path.join(dest_dir, "2026-05-24-hacking-kubernetes-part-1.md")

title = "Hacking Kubernetes (Part 1)"
tags = '["Kubernetes", "Security"]'

try:
    with codecs.open(user_file, 'r', encoding='utf-16le') as f:
        content = f.read()
except Exception as e:
    # Fallback to utf-8 if it somehow wasn't utf-16
    with codecs.open(user_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

if not content.startswith('---'):
    fm = f"---\ntitle: \"{title}\"\ndate: 2026-05-24 00:00:00 +0700\ncategories: [\"Security Research\"]\ntags: {tags}\n---\n\n"
    content = fm + content

with codecs.open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

os.remove(user_file)
print("Successfully fixed and converted user file to UTF-8")
