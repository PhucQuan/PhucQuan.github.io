import re

input_file = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\Myblog\Web Cache Poisoning\Web cache poisoning 348baeb02171802ab2efefc70c0afed0.md"
output_file = r"c:\Users\DELL\codecuaquan\PhucQuan_Blog\PhucQuan.github.io\_posts\2026-04-30-web-cache-poisoning.md"

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'^# Web cache poisoning\n*', '', content, count=1)

def replace_img(match):
    alt = match.group(1)
    url = match.group(2)
    if not url.startswith('http') and not url.startswith('/'):
        url = f"/assets/images/web-cache-poisoning/{url}"
    return f"![{alt}]({url})"

content = re.sub(r'\!\[([^\]]*)\]\(([^)]+)\)', replace_img, content)

front_matter = """---
layout: single
title: "Web Cache Poisoning"
date: 2026-04-30
classes: wide
categories: [Web-Security]
tags: [web, cache-poisoning, portswigger]
permalink: /writeups/web-cache-poisoning/
---

"""

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(front_matter + content)

print('Done')
