import os

post_dir = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\_posts"
files_to_fix = [
    "2026-05-24-lab-thm-htb-ve-kubernetes.md",
    "2026-05-24-thuc-hanh-va-nghien-cuu-cac-ki-thuat-tan-cong.md",
    "2026-05-26-tuan-2-hacking-kubernetes-part-1.md"
]

for filename in files_to_fix:
    filepath = os.path.join(post_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix category
        content = content.replace('categories: ["Security Research"]', 'categories: ["Security-Research"]')
        
        # If this is the part 1 file, fix the title too
        if filename == "2026-05-26-tuan-2-hacking-kubernetes-part-1.md":
            content = content.replace('title: "Tuần 2 - Hacking Kubernetes (Part 1)"', 'title: "Hacking Kubernetes (Part 1)"')
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
# Rename the part 1 file to remove 'tuan-2'
old_part1 = os.path.join(post_dir, "2026-05-26-tuan-2-hacking-kubernetes-part-1.md")
new_part1 = os.path.join(post_dir, "2026-05-26-hacking-kubernetes-part-1.md")

if os.path.exists(old_part1):
    os.rename(old_part1, new_part1)
    
print("Fixed URLs and titles successfully!")
