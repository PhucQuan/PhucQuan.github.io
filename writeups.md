---
layout: single
title: "All Writeups"
permalink: /writeups/
author_profile: false
classes: wide
---

Nơi mình lưu lại quá trình "vọc vạch", từ những bài luyện tập trên Lab cho đến những chiến tích giải đố CTF thực tế. Hy vọng những ghi chép này sẽ giúp ích cho bạn trong hành trình chinh phục Offensive Security.

---

### Phân loại theo Chuyên môn
<div class="category-chips">
{% assign existing_categories = site.posts | map: 'categories' | join: ',' | split: ',' | uniq %}
{% assign planned_categories = "Web,Pentest,Crypto,Cloud,Reverse,BugBounty,Malware" | split: "," %}
{% for cat in planned_categories %}
{% assign slug = cat | slugify %}
{% assign has_posts = false %}
{% if existing_categories contains slug or existing_categories contains cat %}
{% assign has_posts = true %}
{% endif %}
<a href="#{{ slug }}" class="btn {% if has_posts %}btn--info{% else %}btn--inverse{% endif %} btn--small">{{ cat }} {% unless has_posts %}(Coming Soon){% endunless %}</a>
{% endfor %}
</div>

---

{% assign all_cats = "Web,Pentest,Crypto,Cloud,Reverse,BugBounty,Malware,Meta,Advent-of-ctf" | split: "," %}
{% for cat_name in all_cats %}
{% assign slug = cat_name | slugify %}
{% assign category_posts = "" | split: "" %}
{% for post in site.posts %}
{% if post.categories contains cat_name or post.categories contains slug %}
{% assign category_posts = category_posts | push: post %}
{% endif %}
{% endfor %}
{% if category_posts.size > 0 %}
<h2 id="{{ slug }}" class="archive__subtitle">{{ cat_name | replace: "-", " " | capitalize }}</h2>
<div class="entries-list">
{% for post in category_posts %}
<article class="entry-item">
<div class="entry-header">
<span class="entry-date">{{ post.date | date: "%B %d, %Y" }}</span>
<h3 class="entry-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h3>
</div>
<div class="entry-tags">
{% for tag in post.tags %}
<span class="tag-badge">#{{ tag }}</span>
{% endfor %}
</div>
</article>
{% endfor %}
</div>
<br>
{% endif %}
{% endfor %}

<style>
.category-chips {
margin-bottom: 2em;
display: flex;
flex-wrap: wrap;
gap: 10px;
}
.entries-list {
border-left: 2px solid #3d4144;
padding-left: 20px;
margin-bottom: 30px;
}
.entry-item {
margin-bottom: 20px;
position: relative;
}
.entry-item::before {
content: '';
position: absolute;
left: -26px;
top: 10px;
width: 10px;
height: 10px;
background: #007bff;
border-radius: 50%;
}
.entry-header {
display: flex;
flex-direction: column;
}
.entry-date {
font-size: 0.85em;
color: #8b949e;
font-weight: 500;
}
.entry-title {
margin: 5px 0 !important;
font-size: 1.25em !important;
}
.entry-title a {
text-decoration: none;
color: #58a6ff;
}
.entry-title a:hover {
text-decoration: underline;
}
.tag-badge {
font-size: 0.8em;
background: #21262d;
padding: 2px 8px;
border-radius: 12px;
color: #8b949e;
margin-right: 5px;
border: 1px solid #30363d;
}
.btn--inverse {
opacity: 0.6;
cursor: default;
pointer-events: none;
}
</style>

---

## Thống kê nhanh
- **Tổng số bài viết:** {{ site.posts | size }} bài
- **Bài mới nhất:** {{ site.posts.first.date | date: "%B %d, %Y" }}
