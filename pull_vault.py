import os

source_dir = r"D:\Obsidian Vault\Viettel Digital Talent - Cybersecurity\Đề tài leo thang đặc quyền K8S"
dest_dir = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\_posts"

orig_name = "Tuần 2 - Hacking Kubernetes (Part 1).md"
new_name = "2026-05-24-hacking-kubernetes-part-1.md"
title = "Hacking Kubernetes (Part 1)"
tags = '["Kubernetes", "Security"]'

source_path = os.path.join(source_dir, orig_name)
dest_path = os.path.join(dest_dir, new_name)

# Read directly from the original Vault to preserve formatting
with open(source_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add frontmatter
fm = f"---\ntitle: \"{title}\"\ndate: 2026-05-24 00:00:00 +0700\ncategories: [\"Security Research\"]\ntags: {tags}\n---\n\n"

# Overwrite the post
with open(dest_path, 'w', encoding='utf-8') as f:
    f.write(fm + content)

print("Successfully pulled from Vault with pristine formatting.")
