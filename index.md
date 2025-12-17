---
layout: home
title: Home
---

<div class="terminal-header">
  <span class="terminal-prompt">root@phucquan</span><span class="terminal-path">:~$</span>
</div>

# PhucQuan | Security Writeups

```
 _____  _     _   _       ____  _   _          _   _ 
|  __ \| |   | | | |     / __ \| | | |   /\   | \ | |
| |__) | |_  | | | |    | |  | | | | |  /  \  |  \| |
|  ___/| __|  \_/ \_/    | |  | | | | | / /\ \ | . ` |
| |    | |_    ___  ___  | |__| | |_| |/ ____ \| |\  |
|_|     \__|  |___||___/  \___\_\\___//_/    \_\_| \_|

      Security Research & CTF Writeups
```

---

## $ whoami

Security student exploring offensive security through competitive hacking and hands-on labs.

**Focus areas:**
- **CTF** — Web challenges, cryptography, misc
- **Pentesting** — Web application security, reconnaissance
- **Cloud Security** — AWS, cloud misconfigurations
- **Cryptography** — Algorithms, key exchange, padding attacks
- **Malware Analysis** — Reverse engineering basics

---

## $ find . -name writeups -type f

### Latest Writeups

<ul class="writeup-list">
{% for post in site.posts limit:3 %}
  <li>
    <span class="writeup-date">[{{ post.date | date: "%Y-%m-%d" }}]</span>
    <a href="{{ post.url }}">{{ post.title }}</a>
    {% if post.categories %}
      <span class="writeup-category">{{ post.categories | join: ", " }}</span>
    {% endif %}
  </li>
{% endfor %}
</ul>

[View all writeups →](writeups.md)

---

## $ ls -la /skills

- **Languages:** Bash, Python, JavaScript, SQL
- **Tools:** Burp Suite, Wireshark, Nmap, Metasploit
- **Concepts:** Web vulns (OWASP Top 10), authentication flows, cryptography, networking
- **Platforms:** TryHackMe, HackTheBox, CTF competitions

---

## $ cat README.md

This blog documents my security learning journey. Each writeup contains:
- Challenge description and reconnaissance
- Step-by-step exploitation
- Key lessons and takeaways
- References and resources

**All writeups are educational material based on public CTF challenges and lab environments.**

---

## $ navigate --to

| Command | Destination |
|---------|-------------|
| [`about`](about.md) | Background & learning goals |
| [`writeups`](writeups.md) | All security writeups |
| [`github`](https://github.com/PhucQuan) | Source code & projects |
| [`twitter`](https://twitter.com/phucquan) | Security updates |

---

<div class="terminal-footer">
  <span class="blink">▌</span> Last updated: {{ site.time | date: "%Y-%m-%d %H:%M" }}
</div>

## 📂 Repository
Exploit scripts & PoC được lưu tại:
assets/exploit/

yaml
Sao chép mã

---

## ⚠️ Disclaimer
Tất cả nội dung chỉ phục vụ **mục đích học tập**.  
Các mục tiêu được test là **CTF, lab, hoặc môi trường có sự cho phép**.

---

## 🔗 Links
- GitHub: https://github.com/PhucQuan
