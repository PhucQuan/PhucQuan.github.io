---
layout: single
title: "[Writeup] UofTCTF 2026 - NoQuotes & The SUID Escape"
date: 2026-01-29
classes: wide
categories: [ctf, web]
tags: [sqli, ssti, suid, privesc, f-string]
permalink: /writeups/uoftctf-noquotes/
---

Đây là bài thứ 2 mình muốn chia sẻ trong chuỗi writeup UofTCTF 2026. Bài này kết hợp cả SQL Injection và SSTI khá hay.

## 1. Phân tích mã nguồn (Source Code Analysis)

Bước đầu tiên của mọi bài CTF là đọc kỹ mã nguồn để tìm các điểm yếu tiềm tàng.

### Lỗ hổng 1: SQL Injection (SQLi)

Trong hàm `login()`, ứng dụng nhận dữ liệu từ người dùng và chèn trực tiếp vào chuỗi truy vấn bằng F-string:

```python
query = (
    "SELECT id, username FROM users "
    f"WHERE username = ('{username}') AND password = ('{password}')"
)
```

Dù có hàm `waf()` chặn dấu nháy đơn `'` và nháy kép `"`, nhưng cấu trúc này vẫn cực kỳ nguy hiểm nếu có cách thoát khỏi dấu nháy mà không dùng chính nó.

### Lỗ hổng 2: Server-Side Template Injection (SSTI)

Sau khi đăng nhập thành công, giá trị `username` từ Database được lưu vào `session["user"]`. Tại hàm `home()`, giá trị này được đưa vào `render_template_string()`:

```python
return render_template_string(open("templates/home.html").read() % session["user"])
```

Đây là lỗi SSTI kinh điển trong Flask/Jinja2, cho phép thực thi mã từ phía máy chủ.

### Lỗ hổng 3: Leo thang đặc quyền (Privilege Escalation)

Dựa vào file `readflag.c`, ta thấy một chương trình C được thiết lập để chạy với quyền Root (`setuid(0)`) và thực hiện lệnh `cat /root/flag.txt`. File `entrypoint.sh` cũng cho thấy web app chạy dưới quyền user `www-data`. Mục tiêu là thực thi file binary biên dịch từ `readflag.c` để đọc flag.

---

## 2. Tư duy khai thác (Exploitation Mindset)

Chúng mình không thể tấn công trực tiếp vào SSTI vì WAF chặn dấu nháy. Do đó, phải đi theo con đường vòng:

1. Dùng **SQL Injection** để vượt qua đăng nhập.
2. Dùng kỹ thuật `UNION SELECT` để trả về một chuỗi chứa payload **SSTI**.
3. Vì WAF chặn nháy ở đầu vào, mình sẽ mã hóa payload SSTI sang **Hex** (ví dụ: `0x7b...`). Database sẽ tự động giải mã Hex này, giúp payload "sống sót" đi vào `session["user"]`.

---

## 3. Các bước thực hiện chi tiết (Step-by-step)

### Bước 1: Bypass WAF bằng kỹ thuật Backslash

WAF chặn nháy đơn, nhưng không chặn dấu gạch chéo ngược `\`.

- Nếu nhập `username = \`, câu truy vấn trở thành: `WHERE username = ('\') AND password = ('{password}')`.
- Dấu `\` sẽ escape dấu nháy đơn đóng của username, làm cho toàn bộ đoạn `) AND password = (` bị coi là một phần của chuỗi username.
- Lúc này, dấu nháy mở của password sẽ đóng chuỗi cho username. Phần sau đó hoàn toàn thuộc quyền kiểm soát của chúng mình.

### Bước 2: Chèn Payload SSTI qua SQL Injection

Mình muốn `session["user"]` chứa payload để thực thi lệnh hệ thống. Lệnh cần chạy là thực thi file binary `readflag`.
Payload SSTI dự kiến: `{% raw %}{{config.__init__.__globals__['os'].popen('/readflag').read()}}{% endraw %}`.

Để bypass WAF, mình chuyển nó sang Hex:
`0x7b7b636f6e6669672e5f5f696e69745f5f2e5f5f676c6f62616c735f5f5b276f73275d2e706f70656e28272f72656164666c616727292e7265616428297d7d`

**Thông tin nhập vào form:**

- **Username:** `\`
- **Password:** `) UNION SELECT 1, 0x7b7b636f...7d7d -- -` (Có khoảng trắng sau `-`)

### Bước 3: Thu thập Flag

Khi nhấn Login:

1. Hệ thống thực hiện `UNION SELECT`, cột thứ 2 (username) sẽ trả về chuỗi SSTI đã giải mã từ Hex.
2. Ứng dụng lưu chuỗi này vào session và chuyển hướng sang `/home`.
3. Tại `/home`, Flask render chuỗi này, thực thi lệnh chạy `/readflag`.
4. File `/readflag` chạy với quyền Root, đọc `/root/flag.txt` và trả về nội dung trên trình duyệt.

---

## 4. Tổng kết

- **Lỗ hổng chính:** SQL Injection do F-string, SSTI do `render_template_string`, và SUID Binary.
- **Kỹ thuật quan trọng:** Dùng `\` để bypass SQL quotes và dùng **Hex encoding** để "luồn lách" qua WAF đưa payload SSTI vào hệ thống.

**Flag:** `uoftctf{w0w_y0u_5UcC355FU1Ly_Esc4p3d_7h3_57R1nG!}`

![NoQuotes Flag](/assets/images/uoftctf/noquotes_flag.png)

Cảm ơn các bạn đã theo dõi!
