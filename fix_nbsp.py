import os

filepath = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\_posts\2026-05-31-dung-lab-mo-phong-k8s-va-demo-ki-thuat-leo-thang-dac-quyen.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Non-Breaking Space (\u00A0) with a regular space
content = content.replace('\u00A0', ' ')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Non-Breaking Spaces!")
