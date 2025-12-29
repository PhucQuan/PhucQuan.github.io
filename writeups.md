---
layout: single
title: All Writeups
permalink: /writeups/
author_profile: true
classes: wide
sidebar:
  nav: "writeups"
---

<div style="text-align: center; margin-bottom: 3rem;">
  <h1 style="font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #00d9ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
    Security Writeups Collection
  </h1>
  <p style="color: #9aa0a6; font-size: 1.1rem;">
    Detailed documentation of CTF challenges, security labs, and penetration testing exercises
  </p>
</div>

---

## 📊 Quick Stats

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0;">
  <div style="background: #1a1f3a; padding: 1.5rem; border-radius: 12px; text-align: center; border: 1px solid #00d9ff;">
    <div style="font-size: 2.5rem; font-weight: 800; color: #00d9ff;">
      {{ site.posts | size }}
    </div>
    <div style="color: #9aa0a6; margin-top: 0.5rem;">Total Writeups</div>
  </div>
  
  {% assign categories = site.posts | map: 'categories' | join: ',' | split: ',' | uniq %}
  <div style="background: #1a1f3a; padding: 1.5rem; border-radius: 12px; text-align: center; border: 1px solid #00ff88;">
    <div style="font-size: 2.5rem; font-weight: 800; color: #00ff88;">
      {{ categories | size }}
    </div>
    <div style="color: #9aa0a6; margin-top: 0.5rem;">Categories</div>
  </div>
  
  {% if site.posts.first %}
  <div style="background: #1a1f3a; padding: 1.5rem; border-radius: 12px; text-align: center; border: 1px solid #ff0080;">
    <div style="font-size: 1.5rem; font-weight: 800; color: #ff0080;">
      {{ site.posts.first.date | date: "%b %d" }}
    </div>
    <div style="color: #9aa0a6; margin-top: 0.5rem;">Last Updated</div>
  </div>
  {% endif %}
</div>

---

## 📑 All Writeups by Category

{% assign posts_by_category = site.posts | group_by: "categories" %}
{% for category_group in posts_by_category %}
  {% assign category = category_group.name | first %}
  {% if category != "" %}

<div id="{{ category | slugify }}" style="margin: 3rem 0;">
  <h2 style="color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 0.5rem;">
    <i class="fas fa-folder-open"></i> {{ category | capitalize }}
  </h2>

  {% for post in category_group.items %}
  <div style="background: #1a1f3a; border: 1px solid #2d3548; border-radius: 12px; padding: 1.5rem; margin: 1rem 0; transition: all 0.3s ease;">
    <h3 style="margin-top: 0;">
      <a href="{{ post.url }}" style="color: #e8eaed; text-decoration: none;">
        {{ post.title }}
      </a>
    </h3>
    
    <div style="margin: 0.8rem 0;">
      <small style="color: #9aa0a6;">
        <i class="far fa-calendar"></i> {{ post.date | date: "%B %d, %Y" }}
      </small>
      
      {% if post.tags %}
      <div style="margin-top: 0.5rem;">
        {% for tag in post.tags %}
        <span style="background: rgba(0, 217, 255, 0.1); color: #00d9ff; padding: 0.2rem 0.6rem; border-radius: 4px; margin-right: 0.3rem; font-size: 0.8rem;">
          {{ tag }}
        </span>
        {% endfor %}
      </div>
      {% endif %}
    </div>
    
    {% if post.excerpt %}
    <p style="color: #9aa0a6; margin: 1rem 0 0 0; font-size: 0.95rem;">
      {{ post.excerpt | strip_html | truncate: 150 }}
    </p>
    {% endif %}
  </div>
  {% endfor %}
</div>

  {% endif %}
{% endfor %}

---

<div style="text-align: center; color: #9aa0a6; margin-top: 3rem;">
  <p>
    <em>All writeups are based on authorized platforms and public challenges.</em>
  </p>
</div>
