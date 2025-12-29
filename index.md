---
layout: home
title: Home
author_profile: true
header:
  overlay_color: "#0a0e27"
  overlay_filter: "0.5"
classes: wide
---

<div style="text-align: center; padding: 3rem 0 2rem 0;">
  <h1 style="font-size: 3rem; font-weight: 800; margin-bottom: 1rem; background: linear-gradient(135deg, #00d9ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
    Security Writeups & Research
  </h1>
  <p style="font-size: 1.2rem; color: #9aa0a6; max-width: 800px; margin: 0 auto;">
    Welcome to my personal documentation of security research, CTF challenges, and pentesting exercises. 
    Dive into detailed writeups covering web exploitation, cryptography, cloud security, and more.
  </p>
</div>

---

## 🎯 Featured Areas

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
  <div style="background: #1a1f3a; padding: 1.5rem; border-radius: 12px; border: 1px solid #2d3548; transition: all 0.3s ease;">
    <h3 style="color: #00d9ff; margin-bottom: 0.5rem;">
      <i class="fas fa-flag"></i> CTF Challenges
    </h3>
    <p style="color: #9aa0a6; font-size: 0.95rem;">
      Web challenges, cryptography, miscellaneous, and more from various CTF platforms
    </p>
  </div>
  
  <div style="background: #1a1f3a; padding: 1.5rem; border-radius: 12px; border: 1px solid #2d3548;">
    <h3 style="color: #00ff88; margin-bottom: 0.5rem;">
      <i class="fas fa-shield-alt"></i> Pentesting
    </h3>
    <p style="color: #9aa0a6; font-size: 0.95rem;">
      Web application security, reconnaissance, and exploitation techniques
    </p>
  </div>
  
  <div style="background: #1a1f3a; padding: 1.5rem; border-radius: 12px; border: 1px solid #2d3548;">
    <h3 style="color: #ff0080; margin-bottom: 0.5rem;">
      <i class="fas fa-cloud"></i> Cloud Security
    </h3>
    <p style="color: #9aa0a6; font-size: 0.95rem;">
      AWS security, cloud configurations, IAM policies, and infrastructure testing
    </p>
  </div>
  
  <div style="background: #1a1f3a; padding: 1.5rem; border-radius: 12px; border: 1px solid #2d3548;">
    <h3 style="color: #ffaa00; margin-bottom: 0.5rem;">
      <i class="fas fa-key"></i> Cryptography
    </h3>
    <p style="color: #9aa0a6; font-size: 0.95rem;">
      Algorithm analysis, key exchange, padding attacks, and implementation flaws
    </p>
  </div>
</div>

---

## 📝 Latest Writeups

{% assign post_count = site.posts | size %}
{% if post_count > 0 %}
<div class="writeups-list">
  {% for post in site.posts limit:5 %}
  <div class="writeup-card" style="background: #1a1f3a; border: 1px solid #2d3548; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; transition: all 0.3s ease;">
    <h3 style="margin-top: 0;">
      <a href="{{ post.url }}" style="color: #e8eaed; text-decoration: none;">
        {{ post.title }}
      </a>
    </h3>
    
    <div style="margin: 0.5rem 0;">
      <small style="color: #9aa0a6;">
        <i class="far fa-calendar"></i> {{ post.date | date: "%B %d, %Y" }}
        {% if post.categories %}
          {% for category in post.categories %}
            <span style="background: linear-gradient(135deg, #00d9ff, #00ff88); color: #0a0e27; padding: 0.2rem 0.6rem; border-radius: 12px; margin-left: 0.5rem; font-weight: 600; font-size: 0.8rem;">
              {{ category }}
            </span>
          {% endfor %}
        {% endif %}
      </small>
    </div>
    
    {% if post.excerpt %}
    <p style="color: #9aa0a6; margin-top: 1rem; margin-bottom: 0;">
      {{ post.excerpt | strip_html | truncate: 200 }}
    </p>
    {% endif %}
  </div>
  {% endfor %}
</div>

<div style="text-align: center; margin: 2rem 0;">
  <a href="/writeups/" class="btn btn--primary" style="background: linear-gradient(135deg, #00d9ff, #00ff88); color: #0a0e27; padding: 0.75rem 2rem; border-radius: 8px; text-decoration: none; font-weight: 600; display: inline-block;">
    View All Writeups →
  </a>
</div>
{% else %}
<div style="text-align: center; padding: 3rem; background: #1a1f3a; border-radius: 12px; border: 1px solid #2d3548;">
  <p style="color: #9aa0a6; font-size: 1.1rem;">
    <i class="fas fa-file-alt" style="font-size: 3rem; display: block; margin-bottom: 1rem; color: #00d9ff;"></i>
    No writeups yet. New content coming soon!
  </p>
</div>
{% endif %}

---

## 🎓 About This Blog

<div style="background: #1a1f3a; padding: 2rem; border-radius: 12px; border-left: 4px solid #00d9ff;">
  <p style="color: #e8eaed; margin: 0;">
    This is a technical blog documenting my security learning journey through:
  </p>
  <ul style="color: #9aa0a6; margin-top: 1rem;">
    <li>🏆 CTF competitions (TryHackMe, HackTheBox, CTFtime)</li>
    <li>🐛 Bug bounty programs and responsible disclosure</li>
    <li>🧪 Hands-on security labs and challenges</li>
    <li>🔬 Security research and vulnerability analysis</li>
  </ul>
  <p style="color: #9aa0a6; margin-bottom: 0; font-style: italic; border-top: 1px solid #2d3548; padding-top: 1rem; margin-top: 1rem;">
    <strong style="color: #ffaa00;">⚠️ Disclaimer:</strong> All content is educational material based on public challenges and authorized systems.
  </p>
</div>

---

<div style="text-align: center; color: #9aa0a6; font-size: 0.9rem; margin-top: 3rem;">
  <p>
    <em>Last updated: {{ site.time | date: "%B %d, %Y" }}</em>
  </p>
</div>

<style>
.writeup-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 217, 255, 0.2);
  border-color: #00d9ff !important;
}

.writeup-card a:hover {
  color: #00d9ff !important;
}
</style>
