import os
import glob

source_dir = r"D:\Obsidian Vault\Viettel Digital Talent - Cybersecurity\Đề tài leo thang đặc quyền K8S"
dest_dir = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\_posts"

# Find the file in source_dir that contains "Tuần 3" and "Dựng"
files = os.listdir(source_dir)
target_file = None
for f in files:
    if "Tuần 3" in f and "Dựng" in f and f.endswith(".md"):
        target_file = f
        break

if not target_file:
    print("Could not find the Week 3 file!")
    exit(1)

source_path = os.path.join(source_dir, target_file)
new_name = "2026-05-31-dung-lab-mo-phong-k8s-va-demo-ki-thuat-leo-thang-dac-quyen.md"
dest_path = os.path.join(dest_dir, new_name)

title = "Dựng lab mô phỏng K8s và Demo kĩ thuật leo thang đặc quyền"
tags = '["Kubernetes", "Security", "Lab", "Privilege Escalation"]'

with open(source_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add frontmatter
fm = f"---\ntitle: \"{title}\"\ndate: 2026-05-31 00:00:00 +0700\ncategories: [\"Security-Research\"]\ntags: {tags}\n---\n\n"

with open(dest_path, 'w', encoding='utf-8') as f:
    f.write(fm + content)

print(f"Successfully copied {target_file} to {new_name}")
