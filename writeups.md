---
layout: single
title: "Archive"
permalink: /writeups/
author_profile: false
classes: wide
---

<div class="hero-section">
  <h1 class="hero-title">Knowledge Base & Writeups</h1>
  <p class="hero-description">
    Góc nhỏ lưu lại hành trình học tập và những kinh nghiệm mình đúc kết được. Nơi đây tập hợp các bài write-up giải CTF và nhật ký khai thác trên các nền tảng như HackTheBox, TryHackMe, Proving Grounds.
  </p>
  <div class="hero-stats">
    <div class="stat-item">
      <i class="fas fa-file-alt"></i>
      <span>{{ site.posts | size }} Bài viết</span>
    </div>
    <div class="stat-item">
      <i class="fas fa-clock"></i>
      <span>Cập nhật: {{ site.posts.first.date | date: "%m/%Y" }}</span>
    </div>
  </div>
</div>

<div class="filter-section">
  <div class="filter-group">
    <h3 class="filter-label"><i class="fas fa-flag"></i> CTF Categories</h3>
    <div class="chip-container">
      {% assign existing_categories = site.posts | map: 'categories' | join: ',' | split: ',' | uniq %}
      {% assign planned_categories = "Web,Crypto,Pwn,Reverse Engineering,Pentest,Cloud,BugBounty,Malware" | split: "," %}
      {% for cat in planned_categories %}
        {% assign slug = cat | slugify %}
        {% assign has_posts = false %}
        {% if existing_categories contains slug or existing_categories contains cat %}
          {% assign has_posts = true %}
        {% endif %}
        <a href="#{{ slug }}" class="chip {% if has_posts %}chip-active{% else %}chip-disabled{% endif %}">
          {{ cat }}
        </a>
      {% endfor %}
    </div>
  </div>

  <div class="filter-group">
    <h3 class="filter-label"><i class="fas fa-server"></i> Platforms</h3>
    <div class="chip-container">
      {% assign platform_categories = "machine HTB,TryHackMe,Portswigger" | split: "," %}
      {% for cat in platform_categories %}
        {% assign slug = cat | slugify %}
        {% assign has_posts = false %}
        {% if existing_categories contains slug or existing_categories contains cat %}
          {% assign has_posts = true %}
        {% endif %}
        {% assign display_name = cat | replace: "machine HTB", "HackTheBox" | replace: "Portswigger", "PortSwigger" %}
        <a href="#{{ slug }}" class="chip {% if has_posts %}chip-platform{% else %}chip-disabled{% endif %}">
          {{ display_name }}
        </a>
      {% endfor %}
    </div>
  </div>
</div>

<div class="content-section">
  <div class="section-header">
    <h2><i class="fas fa-trophy"></i> CTF Writeups</h2>
    <div class="section-divider"></div>
  </div>

  {% assign ctf_cats = "Web,Crypto,Pwn,Reverse Engineering,Pentest,Cloud,BugBounty,Malware,Meta,Advent-of-ctf" | split: "," %}
  {% for cat_name in ctf_cats %}
    {% assign slug = cat_name | slugify %}
    {% assign category_posts = "" | split: "" %}
    {% for post in site.posts %}
      {% if post.categories contains cat_name or post.categories contains slug %}
        {% assign category_posts = category_posts | push: post %}
      {% endif %}
    {% endfor %}
    
    {% if category_posts.size > 0 %}
      <div class="category-block" id="{{ slug }}">
        <h3 class="category-title">{{ cat_name | replace: "-", " " | capitalize }}</h3>
        <div class="timeline">
          {% for post in category_posts %}
            <article class="timeline-item">
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <span class="timeline-date">{{ post.date | date: "%B %d, %Y" }}</span>
                <h4 class="timeline-title"><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h4>
                <div class="tag-group">
                  {% for tag in post.tags %}
                    <span class="tag">#{{ tag }}</span>
                  {% endfor %}
                </div>
              </div>
            </article>
          {% endfor %}
        </div>
      </div>
    {% endif %}
  {% endfor %}
</div>

<div class="content-section">
  <div class="section-header">
    <h2><i class="fas fa-laptop-code"></i> Machines & Platforms</h2>
    <div class="section-divider"></div>
  </div>

  {% assign machine_cats = "machine HTB,TryHackMe,Portswigger" | split: "," %}
  {% for cat_name in machine_cats %}
    {% assign slug = cat_name | slugify %}
    {% assign category_posts = "" | split: "" %}
    {% for post in site.posts %}
      {% if post.categories contains cat_name or post.categories contains slug %}
        {% assign category_posts = category_posts | push: post %}
      {% endif %}
    {% endfor %}
    
    {% if category_posts.size > 0 %}
      {% assign display_name = cat_name | replace: "machine HTB", "HackTheBox Machines" | replace: "Portswigger", "PortSwigger" %}
      <div class="category-block" id="{{ slug }}">
        <h3 class="category-title">{{ display_name }}</h3>
        <div class="card-grid">
          {% for post in category_posts %}
            <a href="{{ post.url | relative_url }}" class="card-link-wrapper">
              <article class="premium-card">
                <div class="card-image-wrapper">
                  {% if post.image %}
                    <img src="{{ post.image | relative_url }}" alt="{{ post.title }}" class="card-image" loading="lazy">
                  {% else %}
                    <div class="card-placeholder">
                      <i class="fas fa-terminal"></i>
                    </div>
                  {% endif %}
                  <div class="card-overlay"></div>
                </div>
                <div class="card-body">
                  <div class="card-meta">
                    <span class="card-date"><i class="far fa-calendar-alt"></i> {{ post.date | date: "%b %d, %Y" }}</span>
                  </div>
                  <h4 class="card-title">{{ post.title }}</h4>
                  <div class="tag-group">
                    {% for tag in post.tags %}
                      <span class="tag">#{{ tag }}</span>
                    {% endfor %}
                  </div>
                </div>
              </article>
            </a>
          {% endfor %}
        </div>
      </div>
    {% endif %}
  {% endfor %}
</div>

<style>
/* Base Variables & Typography adjustments to ensure cleanliness */
:root {
  --primary-color: #0366d6;
  --text-main: #24292e;
  --text-muted: #586069;
  --border-color: #e1e4e8;
  --bg-light: #f6f8fa;
  --bg-white: #ffffff;
  --accent-green: #2ea043;
  --hover-shadow: 0 12px 28px rgba(0,0,0,0.08);
  --transition-fast: 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* Remove default page title if we have hero */
.page__title { display: none; }

/* Hero Section */
.hero-section {
  background: linear-gradient(145deg, #ffffff 0%, #f6f8fa 100%);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 25px 30px;
  margin-bottom: 30px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.02);
}
.hero-title {
  font-size: 1.8em;
  font-weight: 700;
  color: var(--text-main);
  margin-top: 0;
  margin-bottom: 10px;
  letter-spacing: -0.5px;
}
.hero-description {
  font-size: 1em;
  color: var(--text-muted);
  max-width: 700px;
  margin: 0 auto 20px auto;
  line-height: 1.6;
}
.hero-stats {
  display: flex;
  justify-content: center;
  gap: 20px;
  color: var(--text-muted);
  font-size: 0.95em;
  font-weight: 500;
}
.stat-item i {
  margin-right: 6px;
  color: var(--primary-color);
}

/* Filter Section */
.filter-section {
  display: flex;
  flex-direction: column;
  gap: 25px;
  margin-bottom: 50px;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.filter-label {
  font-size: 1.1em;
  font-weight: 600;
  color: var(--text-main);
  margin: 0;
  border-bottom: none;
  padding-bottom: 0;
}
.filter-label i {
  color: var(--text-muted);
  margin-right: 8px;
}
.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.chip {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.9em;
  font-weight: 500;
  text-decoration: none !important;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}
.chip-active {
  background-color: #f1f8ff;
  color: var(--primary-color);
  border-color: #c8e1ff;
}
.chip-active:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(3, 102, 214, 0.2);
}
.chip-platform {
  background-color: #e6ffed;
  color: var(--accent-green);
  border-color: #b4f1b4;
}
.chip-platform:hover {
  background-color: var(--accent-green);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(46, 160, 67, 0.2);
}
.chip-disabled {
  background-color: var(--bg-white);
  color: #959da5;
  border-color: var(--border-color);
  opacity: 0.6;
  pointer-events: none;
}

/* Section Header */
.content-section {
  margin-bottom: 60px;
}
.section-header {
  margin-bottom: 30px;
}
.section-header h2 {
  font-size: 1.8em;
  margin: 0 0 10px 0;
  color: var(--text-main);
  border-bottom: none;
}
.section-header h2 i {
  color: var(--primary-color);
  margin-right: 10px;
}
.section-divider {
  height: 3px;
  width: 60px;
  background: var(--primary-color);
  border-radius: 3px;
}

/* Category Blocks */
.category-block {
  margin-bottom: 40px;
}
.category-title {
  font-size: 1.4em;
  color: var(--text-main);
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 20px;
}
.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 6px;
  width: 2px;
  background: var(--border-color);
}
.timeline-item {
  position: relative;
  padding-left: 25px;
  margin-bottom: 25px;
}
.timeline-marker {
  position: absolute;
  top: 6px;
  left: -20px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--bg-white);
  border: 2px solid #c8e1ff;
  transition: all var(--transition-fast);
}
.timeline-item:hover .timeline-marker {
  background: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: 0 0 0 4px rgba(3, 102, 214, 0.1);
}
.timeline-content {
  background: var(--bg-white);
  border: 1px solid transparent;
  padding: 15px 20px;
  border-radius: 12px;
  transition: all var(--transition-fast);
}
.timeline-item:hover .timeline-content {
  border-color: var(--border-color);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  transform: translateX(5px);
}
.timeline-date {
  font-size: 0.85em;
  color: var(--text-muted);
  font-weight: 500;
  display: block;
  margin-bottom: 6px;
}
.timeline-title {
  margin: 0 0 12px 0 !important;
  font-size: 1.25em !important;
  line-height: 1.4;
}
.timeline-title a {
  text-decoration: none;
  color: var(--text-main);
  transition: color var(--transition-fast);
}
.timeline-item:hover .timeline-title a {
  color: var(--primary-color);
}

/* Tag System */
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag {
  font-size: 0.75em;
  background: var(--bg-light);
  color: var(--text-muted);
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 500;
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}
.tag:hover {
  background: #e1e4e8;
  color: var(--text-main);
}

/* Premium Card Grid */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
}
.card-link-wrapper {
  text-decoration: none !important;
  color: inherit !important;
  display: block;
}
.premium-card {
  background: var(--bg-white);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all var(--transition-fast);
}
.premium-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--hover-shadow);
  border-color: #d1d5da;
}
.card-image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 Aspect Ratio */
  overflow: hidden;
  background: var(--bg-light);
  border-bottom: 1px solid var(--border-color);
}
.card-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}
.premium-card:hover .card-image {
  transform: scale(1.05);
}
.card-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3em;
  color: #d1d5da;
}
.card-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.card-meta {
  font-size: 0.85em;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.card-title {
  margin: 0 0 15px 0 !important;
  font-size: 1.2em !important;
  line-height: 1.4;
  color: var(--text-main);
  transition: color var(--transition-fast);
}
.premium-card:hover .card-title {
  color: var(--primary-color);
}
.premium-card .tag-group {
  margin-top: auto;
}
</style>

