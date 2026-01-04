---
layout: home
title: Home
author_profile: true
---

# Security Writeups & Learning Notes

Welcome to my personal documentation of security research, CTF challenges, and pentesting exercises.

## Featured Areas

- **CTF** — Web challenges, cryptography, and more [[Read Latest Writeups]({{ '/writeups/' | relative_url }})]
- **Pentesting** — Web application assessments and security research [[View CTF Notes]({{ '/categories/#ctf' | relative_url }})]
- **Cloud Security** — AWS/Azure hardening and IAM exploitation
- **Bug Bounty** — Active hunter on HackerOne & Bugcrowd [[Bug Bounty Findings]({{ '/tags/#bug-bounty' | relative_url }})]


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
- **CTF competitions**
- **Bug bounty programs** (HackerOne, Bugcrowd)
- **Hands-on labs** (HackTheBox, TryHackMe, PortSwigger Web Security Academy)
- **Security research**

**All content is educational material** based on public challenges and authorized systems.

---

*Last updated: {{ site.time | date: "%B %d, %Y" }}*
