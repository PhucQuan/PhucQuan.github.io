import os

source_dir = r"D:\Obsidian Vault\Viettel Digital Talent - Cybersecurity\Đề tài leo thang đặc quyền K8S"
dest_dir = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\_posts"

files_to_process = [
    ("Tuần 2 - Hacking Kubernetes (Part 1).md", "2026-05-24-hacking-kubernetes-part-1.md", "Hacking Kubernetes (Part 1)", '["Kubernetes", "Security"]'),
    ("Tuần 2 - Lab THM HTB về Kubernetes.md", "2026-05-24-lab-thm-htb-ve-kubernetes.md", "Lab THM HTB về Kubernetes", '["Kubernetes", "Security", "HTB", "THM"]'),
    ("Tuần 2 - Thực hành và nghiên cứu các kĩ thuật tấn công.md", "2026-05-24-thuc-hanh-va-nghien-cuu-cac-ki-thuat-tan-cong.md", "Thực hành và nghiên cứu các kĩ thuật tấn công Kubernetes", '["Kubernetes", "Security"]')
]

old_files = [
    "2026-05-24-tuan-2-hacking-kubernetes-part-1.md",
    "2026-05-24-tuan-2-lab-thm-htb-ve-kubernetes.md",
    "2026-05-24-tuan-2-thuc-hanh-va-nghien-cuu-cac-ki-thuat-tan-cong.md"
]
for old_f in old_files:
    path = os.path.join(dest_dir, old_f)
    if os.path.exists(path):
        os.remove(path)
        print(f"Removed old file {old_f}")

for orig_name, new_name, title, tags in files_to_process:
    source_path = os.path.join(source_dir, orig_name)
    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fm = f"---\ntitle: \"{title}\"\ndate: 2026-05-24 00:00:00 +0700\ncategories: [\"Security Research\"]\ntags: {tags}\n---\n\n"
    
    dest_path = os.path.join(dest_dir, new_name)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(fm + content)
    print(f"Restored and created {new_name}")

print("Done")
