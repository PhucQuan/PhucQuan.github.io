# 🔐 PhucQuan Security Writeups

A professional, dark-themed Jekyll blog for security writeups, CTF solutions, and offensive security learning logs.

```
████████████████████████████████████████████████████████████
  Security Research & CTF Writeups - Educational Purpose
████████████████████████████████████████████████████████████
```

## 🎯 What Is This?

A personal security blog documenting:
- **CTF Challenges** (web, crypto, misc)
- **Penetration Testing** exercises
- **Cloud Security** labs
- **Cryptography** deep-dives
- **Malware Analysis** basics
- **Bug Bounty** findings

Everything is educational material based on public CTF challenges and authorized lab environments.

🌐 **Live site:** https://phucquan.github.io

---

## 🚀 Quick Start

### Prerequisites

- Ruby 2.5+
- Jekyll 4.0+
- Git

### Setup Locally

```bash
# Clone the repository
git clone https://github.com/PhucQuan/PhucQuan.github.io.git
cd PhucQuan.github.io

# Install dependencies
bundle install

# Run locally
bundle exec jekyll serve

# Visit http://localhost:4000
```

### Deploy to GitHub Pages

1. Push to `main` branch:
   ```bash
   git add .
   git commit -m "Add new writeup"
   git push origin main
   ```

2. GitHub Actions automatically builds and deploys
3. Site available at: `https://phucquan.github.io`

---

## 📝 Writing a New Writeup

### Step 1: Create File

Create a new markdown file in `_posts/` with format:
```
_posts/YYYY-MM-DD-challenge-name.md
```

Example:
```
_posts/2025-01-15-nite-ctf-single-sign-off.md
```

### Step 2: Add Front Matter

Every writeup needs YAML front matter at the top:

```yaml
---
layout: post
title: "Challenge Name - Brief Description"
categories: ctf
tags: [web, sqli, auth, logic-flaw]
date: 2025-01-15
---
```

### Front Matter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `layout` | ✅ | Always `post` |
| `title` | ✅ | Challenge name + brief desc |
| `categories` | ✅ | One of: `ctf`, `pentest`, `lab`, `research`, `cloud` |
| `tags` | ✅ | Relevant tags (web, crypto, auth, etc.) |
| `date` | ✅ | Publication date (YYYY-MM-DD) |

### Step 3: Use Template

Follow the structure in [_posts/TEMPLATE-writeup-format.md](_posts/TEMPLATE-writeup-format.md):

```markdown
## Challenge Info
## Initial Reconnaissance
## Enumeration & Analysis
## Exploitation
## Post-Exploitation (if applicable)
## Key Lessons Learned
## References
```

**Don't skip sections.** Even if not all apply, include the headers.

### Step 4: Write Practically

✅ **DO:**
- Include actual commands you ran
- Show real output and errors
- Explain your reasoning
- Document what didn't work
- Cite sources
- Use code blocks for commands/payloads

❌ **DON'T:**
- Fake exploits or make up output
- Use AI-generated text
- Skip technical details
- Plagiarize without attribution

---

## 📁 Project Structure

```
PhucQuan.github.io/
├── _config.yml                 # Jekyll configuration
├── _layouts/
│   ├── default.html           # Main layout
│   └── post.html              # Post layout
├── _posts/
│   ├── YYYY-MM-DD-title.md   # Individual writeups
│   └── TEMPLATE-writeup-format.md
├── assets/
│   ├── css/
│   │   └── style.css          # Dark hacker theme
│   ├── js/
│   │   └── terminal.js        # Optional animations
│   └── images/
│       └── exploit/           # Screenshots
├── index.md                   # Home page
├── about.md                   # About page
├── writeups.md               # Writeups listing
└── README.md                 # This file
```

---

## 🎨 Customization

### Change Colors

Edit `assets/css/style.css` (top of file):
```css
:root {
  --bg-primary: #0a0e27;        /* Main background */
  --text-primary: #00ff00;      /* Terminal green */
  --accent-cyan: #00ffff;       /* Link color */
}
```

### Add Custom Pages

Create `.md` file in root with frontmatter:
```markdown
---
layout: default
title: Page Title
permalink: /page-slug/
---

Content here.
```

---

## 🔧 Best Practices

### Title Format

✅ Good:
- `NiteCTF 2025 - Single Sign Off: Authentication Logic Flaw`
- `HackTheBox - Previse: PHP RCE via Dependency Injection`

❌ Bad:
- `CTF Writeup`
- `Web Challenge`

### Tags Convention

- **Web:** `web`, `sqli`, `xss`, `auth`, `logic-flaw`, `rce`
- **Crypto:** `crypto`, `rsa`, `aes`, `hash`
- **Misc:** `misc`, `osint`, `steganography`
- **Reverse:** `reverse`, `binary`, `assembly`

---

## 🔒 Security Guidelines

### ✅ Include

- Public CTF challenges (solutions expected)
- HackTheBox/TryHackMe walkthroughs
- Published CVEs with public exploits
- Educational vulnerability explanations

### ❌ Exclude

- Real company vulnerabilities (without permission)
- Private CTF challenge details
- Personal credentials or API keys
- Unpatched zero-days

---

## 🐛 Troubleshooting

### Posts Not Showing

- Check filename: `YYYY-MM-DD-slug.md`
- Check YAML frontmatter is valid
- Posts with future dates won't display
- Use `bundle exec jekyll serve --future` to see them

### Site Not Building

```bash
bundle exec jekyll clean
bundle exec jekyll build
```

### Styling Issues

- Hard refresh: `Ctrl+Shift+R`
- Check `assets/css/style.css`

---

## 📚 Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [PortSwigger Academy](https://portswigger.net/web-security)
- [HackTheBox](https://www.hackthebox.com/)
- [TryHackMe](https://www.tryhackme.com/)
- [Jekyll Docs](https://jekyllrb.com/)

---

## 👤 Author

**Phuc Quan**
- GitHub: [@PhucQuan](https://github.com/PhucQuan)
- Focus: CTF, Web Security, Cloud Security

---

**Last Updated:** December 16, 2025

🔐 Happy hacking!
