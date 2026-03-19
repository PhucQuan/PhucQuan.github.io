---
layout: single
title: Penetration Testing
permalink: /penetration-testing/
author_profile: false
classes: wide
---

Kiến thức về Penetration Testing, các lỗ hổng bảo mật web phổ biến trong OWASP Top 10 và kỹ thuật khai thác.

---

{% assign category_posts = "" | split: "" %}
{% for post in site.posts %}
{% if post.categories contains "Penetration Testing" %}
{% assign category_posts = category_posts | push: post %}
{% endif %}
{% endfor %}

<div class="entries-list">
{% for post in category_posts %}
<article class="entry-item">
<div class="entry-header">
<span class="entry-date">{{ post.date | date: "%B %d, %Y" }}</span>
<h3 class="entry-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
</div>
<div class="entry-excerpt">{{ post.excerpt | strip_html | truncatewords: 30 }}</div>
<div class="entry-tags">
{% for tag in post.tags %}
<span class="tag-badge">#{{ tag }}</span>
{% endfor %}
</div>
</article>
{% endfor %}
</div>
