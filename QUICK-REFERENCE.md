## ⚡ QUICK REFERENCE CARD

### 🚀 Start Local Development
```bash
cd c:\Users\DELL\codecuaquan\PhucQuan.github.io
bundle install      # One-time setup
bundle exec jekyll serve
# Visit: http://localhost:4000
```

### 📝 Create New Writeup

**1. Create file:**
```bash
_posts/2025-01-20-challenge-name.md
```

**2. Add frontmatter:**
```yaml
---
layout: post
title: "CTF Name - Challenge: Type"
categories: ctf
tags: [web, sqli, auth]
date: 2025-01-20
---
```

**3. Follow template:**
- Challenge Info
- Reconnaissance
- Enumeration & Analysis
- Exploitation
- Lessons Learned
- References

### 🖼️ Adding Images

**1. Store Images:**
Create a folder for your post: `assets/images/writeups/<post-name>/`
Example: `assets/images/writeups/2025-htb-machine/root-flag.png`

**2. Use Markdown:**
```markdown
![Description](/assets/images/writeups/2025-htb-machine/root-flag.png)
```

### 📤 Deploy Changes
```bash
git add .
git commit -m "Add writeup: Challenge Name"
git push origin main
# GitHub auto-deploys!
```

---

## 🏷️ Tags Quick List

**Web:** web sqli xss auth logic-flaw rce lfi ssti csrf  
**Crypto:** crypto rsa aes hash padding-oracle  
**Misc:** misc osint steganography forensics  
**Reverse:** reverse binary assembly ida ghidra  

Example: `tags: [web, sqli, mysql, blind-injection]`

---

## 🎨 Customize Colors

**File:** `assets/css/style.css` (lines 1-25)

```css
:root {
  --bg-primary: #0a0e27;      /* Dark blue-black */
  --text-primary: #00ff00;    /* Bright green */
  --accent-cyan: #00ffff;     /* Neon cyan */
  --accent-red: #ff3333;      /* Bright red */
  --accent-purple: #9d4edd;   /* Purple */
}
```

---

## 📚 Files to Edit Frequently

| File | Purpose | Change Often? |
|------|---------|---------------|
| _posts/*.md | Your writeups | **YES** ✅ |
| about.md | Your bio | Sometimes |
| _config.yml | Site settings | Rarely |
| assets/css/style.css | Colors/styling | Rarely |
| _layouts/ | HTML templates | Never |

---

## ✅ Writing Checklist

- [ ] File named: YYYY-MM-DD-slug.md
- [ ] YAML frontmatter valid
- [ ] Title: "Event - Challenge: Type"
- [ ] Categories: 1 (ctf/pentest/lab/research/cloud)
- [ ] Tags: 2-4 relevant (#web #sqli #auth)
- [ ] All template sections included
- [ ] Actual commands/output (not fake)
- [ ] Code blocks formatted
- [ ] Links work
- [ ] Tested locally
- [ ] Pushed to GitHub

---

## 🎯 Categories

```yaml
categories: ctf        # Capture The Flag
categories: pentest    # Penetration Testing
categories: lab        # HackTheBox/TryHackMe
categories: research   # Security Research
categories: cloud      # Cloud Security
```

Pick **ONE** per post.

---

## 🔗 URL Format

Your writeups get these URLs automatically:

```
/YYYY/MM/DD/slug-from-title/
```

Examples:
```
/2025/01/20/nite-ctf-auth-flaw/
/2025/01/15/hackthebox-previse-rce/
```

Custom URL:
```yaml
permalink: /writeups/my-custom-url/
```

---

## 🎮 Optional: Enable Extra Effects

**File:** `_layouts/default.html` (at bottom, uncomment):

```javascript
// startMatrixRain('element-id', 3000);  // Matrix effect
// enableCRTEffect(true);                 // CRT monitor look
// addScrollToTop();                      // Scroll-to-top button
```

---

## 🐛 Common Fixes

| Problem | Solution |
|---------|----------|
| Posts don't show | Check: filename `YYYY-MM-DD-*.md`, YAML valid, date not future |
| Styling broken | Hard refresh: `Ctrl+Shift+R` |
| Won't build | Run: `bundle install && bundle update` |
| Links 404 | URLs auto-generate. Check post date/slug. |

---

## 📞 Key Commands

```bash
# Start local server
bundle exec jekyll serve

# Show future posts
bundle exec jekyll serve --future

# Show draft posts
bundle exec jekyll serve --draft

# Build static site
bundle exec jekyll build

# Clean cache
bundle exec jekyll clean

# Update gems
bundle update
```

---

## 🔒 Remember!

✅ **Include:**
- Public CTF solutions
- Published CVEs
- Educational content
- Authorized labs (after release)

❌ **Avoid:**
- Real company vulnerabilities
- Unreleased CTF details
- Credentials/API keys
- Zero-days
- Active bug bounty details

**Assume everything is public!**

---

## 📊 Site Structure

```
Home (index.md)
├── Latest 3 posts (auto)
├── Navigation → About
├── Navigation → Writeups
├── Navigation → GitHub

About (about.md)
├── Your bio
├── Skills
├── Learning path
└── Contact info

Writeups (writeups.md)
├── By category
├── Filter by tags
└── Post stats

Posts (_posts/)
└── YYYY-MM-DD-slug.md
    ├── Challenge info
    ├── Reconnaissance
    ├── Enumeration
    ├── Exploitation
    ├── Lessons learned
    └── References
```

---

## 🎨 Theme Palette

**Terminal Green:** #00ff00 (main text)  
**Neon Cyan:** #00ffff (links, accents)  
**Dark Blue:** #0a0e27 (background)  
**Purple:** #9d4edd (highlights)  
**Red:** #ff3333 (important/prompts)  
**Gray:** #888888 (muted text)  

---

## 💡 Pro Tips

1. **Write after solving** - Document while fresh
2. **Include failed attempts** - Readers learn more
3. **Show actual commands** - Copy-paste ready
4. **Explain concepts** - Don't assume knowledge
5. **Link sources** - Give credit
6. **Update regularly** - Shows active learning
7. **Proofread** - Reflects on you

---

## 🆘 Need Help?

- **Jekyll Docs:** https://jekyllrb.com/
- **GitHub Pages:** https://pages.github.com/
- **Markdown:** https://www.markdownguide.org/
- **YAML:** https://yaml.org/

---

**Quick Ref v1.0** | Created: Dec 16, 2025 | Updated: Check COMPLETE.md
