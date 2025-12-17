---
layout: single
title: All Writeups
permalink: /writeups/
---

## Security Writeups

Below is a collection of my security writeups, organized by category. Each writeup documents my approach to solving CTF challenges, lab exercises, and security research.

### Filter by Category

{% assign categories = site.posts | map: 'categories' | join: ',' | split: ',' | uniq | sort %}

{% for category in categories %}
  {% if category != "" %}
- [{{ category | capitalize }}](#{{ category }})
  {% endif %}
{% endfor %}

---

{% assign posts_by_category = site.posts | group_by: "categories" %}

{% for category_group in posts_by_category %}
  {% assign category = category_group.name | first %}
  {% if category != "" %}

### {{ category | capitalize }}

| Title | Date | Tags |
|-------|------|------|
{% for post in category_group.items %}
| [{{ post.title }}]({{ post.url }}) | {{ post.date | date: "%B %d, %Y" }} | {% for tag in post.tags %}`{{ tag }}`{% unless forloop.last %} {% endunless %}{% endfor %} |
{% endfor %}

  {% endif %}
{% endfor %}

---

## Statistics

- **Total Writeups:** {{ site.posts | size }}
- **Most Recent:** {{ site.posts.first.date | date: "%B %d, %Y" }}

---

## Getting Started

New to my blog? Consider starting with:
1. Read the [About](/about/) page to understand my focus areas
2. Browse writeups by category above
3. Check the latest posts for recent challenges

Each writeup includes step-by-step explanations, actual commands used, and lessons learned.
