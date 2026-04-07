import os
import zipfile
from lxml import etree
import docx

def extract_docx(docx_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    
    # Extract images using zipfile since docx is just a zip archive
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            for info in docx_zip.infolist():
                if info.filename.startswith('word/media/'):
                    img_name = os.path.basename(info.filename)
                    if img_name:
                        extracted_path = docx_zip.extract(info.filename, output_dir)
                        # Move to images folder
                        new_path = os.path.join(output_dir, 'images', img_name)
                        os.replace(extracted_path, new_path)
    except Exception as e:
        print(f"Error extracting images from {docx_path}: {e}")

    # Extract text using python-docx
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + '\n'
    except Exception as e:
        print(f"Error extracting text from {docx_path}: {e}")

    text_path = os.path.join(output_dir, 'extracted_text.txt')
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"Extracted {docx_path} to {output_dir}")

base_dir = r'C:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\CTF_Writeups'
files = [
    'writeup_EvidenceLab.docx',
    'writeup_securenotes.docx',
    'Monitor_Breaker_Writeup.docx',
    'nexus2_writeup.docx'
]

for f in files:
    name = f.replace('.docx', '').replace('writeup_', '').replace('_Writeup', '').lower()
    out_dir = os.path.join(base_dir, f'extracted_{name}')
    extract_docx(os.path.join(base_dir, f), out_dir)

