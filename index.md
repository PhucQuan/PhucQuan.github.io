---
layout: home
title: Home
author_profile: false
---

# Security Writeups & Learning Notes

Welcome to my personal documentation of security research, CTF challenges, and pentesting exercises.

## Featured Areas

- **CTF** — Web challenges, cryptography, miscellaneous
- **Pentesting** — Web application security, reconnaissance, exploitation
- **Cloud Security** — AWS, cloud configurations, IAM
- **Cryptography** — Algorithms, key exchange, padding attacks
- **Malware Analysis** — Reverse engineering basics

## Latest Writeups

{% for post in site.posts limit:5 %}
  {% if forloop.first %}<ul>{% endif %}
  <li>
    <strong><a href="{{ post.url }}">{{ post.title }}</a></strong>
    <br>
    <small>{{ post.date | date: "%B %d, %Y" }} • {% if post.categories %}{{ post.categories | join: ", " }}{% endif %}</small>
  </li>
  {% if forloop.last %}</ul>{% endif %}
{% endfor %}

[View all writeups →](/writeups/)

---

## About This Blog

This is a technical blog documenting my security learning journey through:
- CTF competitions
- Bug bounty programs  
- Hands-on labs (TryHackMe, HackTheBox)
- Security research

**All content is educational material** based on public challenges and authorized systems.

---

*Last updated: {{ site.time | date: "%B %d, %Y" }}"*
