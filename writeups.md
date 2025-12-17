---
layout: single
title: Writeups
permalink: /writeups/
---

<div class="terminal-header">
  <span class="terminal-prompt">root@phucquan</span><span class="terminal-path">:~$ find . -name "*.writeup"</span>
</div>

# Security Writeups

```
 ___       ___ ___      ___  ___  ___  ___  ___    ___  ___  ___  ___ 
|"  \     /"  |"  \    |"  \/"  |/"  |("  \"  \  /"  |("  \"  \ ("  \
 \__/    // __ \__/    (  T_T  )(  ( |_  T  T) (  /  |_  T  T) )_  T
|"  \   /  \ |"  \    |: / |  :|: (_/  |: (_ : |: /    |: / |  |"  \
 \__/  (: ( \/  \__/   |__/|__/|_/\___ |_|  |_||_/     |___|_|_|_/\_|
                                                                      
```

---

## $ ls -la /writeups

{% assign writeups_by_category = site.posts | group_by: "categories" | sort: "name" %}

{% for category_group in writeups_by_category %}
  {% assign category = category_group.name %}
  {% if category != "" %}

### 📂 {{ category | capitalize }}

<ul class="writeup-grid">
    {% for post in category_group.items %}
    <li>
      <div class="writeup-card">
        <div class="writeup-date">[{{ post.date | date: "%Y-%m-%d" }}]</div>
        <div class="writeup-title">
          <a href="{{ post.url }}">{{ post.title }}</a>
        </div>
        {% if post.tags %}
          <div class="writeup-tags">
            {% for tag in post.tags %}
              <span class="tag">#{{ tag }}</span>
            {% endfor %}
          </div>
        {% endif %}
        {% if post.excerpt %}
          <div class="writeup-excerpt">
            {{ post.excerpt | strip_html }}
          </div>
        {% endif %}
      </div>
    </li>
    {% endfor %}
</ul>

  {% endif %}
{% endfor %}

---

## $ grep -r "tags" .

<div class="tag-filter">
  <strong>Popular Tags:</strong>
  {% assign tags = site.posts | map: 'tags' | join: ',' | split: ',' | uniq | sort %}
  {% for tag in tags %}
    {% if tag != "" %}
      <a href="/tags/#{{ tag }}" class="tag-link">#{{ tag }}</a>
    {% endif %}
  {% endfor %}
</div>

---

## 📋 Writeup Categories Explained

| Category | Description |
|----------|-------------|
| **CTF** | Competitive hacking challenges (web, crypto, misc) |
| **Pentest** | Web application penetration testing |
| **Lab** | TryHackMe, HackTheBox, and similar lab writeups |
| **Research** | Security research and technical deep-dives |
| **Cloud** | Cloud security (AWS, Azure, GCP) assessments |

---

## 🎯 Getting Started

New to security writeups? Start here:
- Read [How to use this blog](https://github.com/PhucQuan/PhucQuan.github.io#readme)
- Check out writeups marked as **beginner-friendly**
- Review the writeup template format
- Join communities: HackTheBox, TryHackMe, CTFtime

---

## $ wc -l *.md

**Stats:**
- Total writeups: **{{ site.posts | size }}**
- Most active category: 
  {% assign category_counts = site.posts | group_by: "categories" | map: "size" | max %}
  {% for category_group in writeups_by_category %}
    {% if category_group.size == category_counts %}{{ category_group.name | capitalize }}{% endif %}
  {% endfor %}

---

<div class="terminal-footer">
  <span class="blink">▌</span> Last updated: {{ site.time | date: "%Y-%m-%d %H:%M" }}
</div>
