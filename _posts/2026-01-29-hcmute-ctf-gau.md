---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - Gau (Socket Automation)"
date: 2026-01-29
classes: wide
categories: [HCMUTE CTF 2026, pwn]
tags: [hcmute, pwn, socket, python, pwntools]
permalink: /writeups/hcmute-ctf-gau/
---

Tiếp theo là một bài Pwn (khai thác lỗ hổng) nhưng thiên về lập trình automation: **Gau**.

## 1. Phân tích thử thách

Khi chúng ta kết nối tới server qua lệnh `nc 103.130.211.150 19069`, server đưa ra yêu cầu:

- **Nhiệm vụ:** Sủa "gau gau gau" đúng 100 lần liên tục.
- **Ràng buộc:** Sai một lần là phải đếm lại từ đầu.
- **Vấn đề:** Việc nhập tay 100 lần là không khả thi vì:
    - Dễ sai sót (typo).
    - Server thường có **timeout** (nếu bạn nhập quá chậm, nó sẽ ngắt kết nối).
    - Server yêu cầu phản hồi theo đúng trình tự (Request-Response).

## 2. Ý tưởng giải quyết

Chúng ta cần một đoạn mã (Script) để tự động hóa quá trình này. Quy trình của script sẽ là:

1. Kết nối tới Server.
2. Đọc dữ liệu mồi (như "Sua di:").
3. Dùng vòng lặp `for` chạy 100 lần.
4. Trong mỗi vòng lặp: Gửi chuỗi "gau gau gau" và **quan trọng nhất** là đợi server xác nhận đã nhận xong rồi mới gửi tiếp lần sau.

## 3. Giải thích mã nguồn (Sử dụng thư viện `pwntools`)

`pwntools` là thư viện mạnh mẽ nhất dành cho các bài CTF. Dưới đây là code hoàn chỉnh mình đã dùng để giải bài này:

```python
from pwn import *

# 1. Thiết lập thông số kết nối
host = '103.130.211.150'
port = 19069

# 2. Khởi tạo kết nối đến server
io = remote(host, port)

# 3. Đọc dữ liệu ban đầu cho đến khi gặp chữ "Sua di:"
# Điều này giúp dọn dẹp buffer để bắt đầu vòng lặp gửi tin
print(io.recvuntil(b"Sua di:").decode())

# 4. Thực hiện vòng lặp 100 lần
for i in range(1, 101):
    # Gửi chuỗi "gau gau gau" kèm ký tự xuống dòng (\n)
    io.sendline(b"gau gau gau")
    
    # 5. Đợi server phản hồi
    # Nếu chưa đến lần cuối (100), server sẽ gửi tiếp "Sua di:"
    if i < 100:
        # Nhận dữ liệu cho đến khi thấy "Sua di:", chuẩn bị cho lần gửi tới
        io.recvuntil(b"Sua di:")
        if i % 10 == 0:
            print(f"Đã sủa được {i}/100 lần...")

# 6. Sau khi hoàn thành 100 lần, chuyển sang chế độ tương tác
# Lúc này server sẽ trả về FLAG, io.interactive() cho phép ta xem kết quả cuối cùng
print("Hoàn thành! Đang lấy Flag...")
io.interactive()
```

## 4. Các lưu ý quan trọng

- **EOFError:** Lỗi này thường xảy ra khi script cố gắng đọc dữ liệu (`recv`) từ một kết nối đã bị server đóng. Ở lần thứ 100, server gửi Flag xong có thể đóng kết nối ngay, nên logic code cần xử lý khéo léo để không `recv` thừa.
- **Trạng thái đồng bộ (Synchronization):** Không nên gửi 100 dòng cùng một lúc bằng một vòng lặp siêu tốc (flood). Server cần thời gian xử lý từng dòng. Việc dùng `recvuntil` giúp script "nhịp nhàng" với server.
- **Ký tự Byte:** Trong Python 3, khi giao tiếp qua socket, chúng ta dùng định dạng byte (có chữ `b` phía trước chuỗi: `b"text"`).

Hy vọng bài này giúp các bạn làm quen với `pwntools`!
