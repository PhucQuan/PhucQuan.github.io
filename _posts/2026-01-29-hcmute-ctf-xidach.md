---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - XiDach (Reverse Engineering)"
date: 2026-01-29
classes: wide
categories: [HCMUTE CTF 2026, reverse-engineering]
tags: [hcmute, reverse, python, pyinstaller, decomplie]
permalink: /writeups/hcmute-ctf-xidach/
---

Tiếp tục với chủ đề CTF, bài này là **XiDachCTF** thuộc mảng Reverse Engineering.

**Mô tả:** *"Ở đây chúng tôi không phải đương, gấp đôi tới chết."*

## 1. Phân tích file thực thi (Initial Analysis)

File được cung cấp là `XiDachCTF.exe`.
Sử dụng command `file` hoặc các công cụ như `PEID`, chúng ta nhận diện được đây là file **PE32+ executable for MS Windows (GUI)**.

Đặc biệt, khi soi các chuỗi string bên trong, có nhiều dấu hiệu của **PyInstaller**. Điều này có nghĩa là tác giả đã viết code bằng Python, sau đó đóng gói thành file `.exe` để chạy trên Windows.

## 2. Bóc tách mã nguồn (Unpacking & Decompiling)

Vì file gốc là Python đã đóng gói, mình cần thực hiện quy trình "ngược" để lấy lại source code:

1.  **Extract:** Sử dụng công cụ `pyinstxtractor.py` để bóc tách file `.exe`. Kết quả quan trọng nhất nhận được là file **`xidach_ctf.pyc`** (Bytecode của Python).
2.  **Decompile:** Sử dụng các công cụ như **PyLingual** hoặc `uncompyle6` để dịch ngược từ `.pyc` về `.py`.

## 3. Phân tích Logic (Code Analysis)

Sau khi có source code, mình thấy đây là một game Xì Dách viết bằng thư viện `tkinter`. Tuy nhiên, tác giả đã gài rất nhiều bẫy:

### a. Flag giả (Fake Flags)

Trong code có rất nhiều chuỗi nằm trong dấu ngoặc nhọn `{}` tại các mốc kiểm tra tiền cược (50, 100, 200...).
Ví dụ: `{Dealer_luon_thang_ban_oi}`, `{Choi_nhieu_la_thang_nhieu}`.
Đây chỉ là "Honeypot" để đánh lạc hướng. Nộp mấy cái này là sai ngay.

### b. Điều kiện kích hoạt Flag thật

Flag thật sự được tính toán động trong hàm `bai_hoc_cuoc_song`. Để kích hoạt nó, mình phải đưa nhân vật vào tình thế **"Lâm vào đường cùng"**:

1.  Số tiền (`player_money`) phải về đúng bằng **0**.
2.  Phải chơi ít nhất **3 ván**.
3.  **Bí thuật:** Phải đặt cược theo đúng trình tự ma thuật: **13, 37, 42** ở 3 ván cuối. Khi đó, biến `da_mo_khoa_triet_ly` sẽ được bật.

## 4. Giải mã Flag

Flag được ghép từ 3 phần, xử lý qua phép XOR:

1.  **Phần đầu:** Giải mã từ mảng `thanh_phan` XOR với `[13, 37, 42]`. -> `UTECTF{Nguoi_khong_choi_la_nguoi_`
2.  **Phần giữa:** Giải mã từ mảng `du_lieu_nang_cao` XOR với số **100** (tổng của 3 số cược + offset). -> `khong_bao_gio_`
3.  **Phần cuối:** Chuỗi tĩnh `thang}`.

## 5. Script Giải mã (Solver)

Thay vì ngồi chơi bài cho đến khi hết tiền, mình viết script Python để giải mã luôn:

```python
# Trích xuất dữ liệu từ code
key = [13, 37, 42]
thieu = [88, 113, 111, 78, 113, 108, 118, 107, 77, 120, 74, 67, 82, 78, 66]
ca_biet = [98, 75, 77, 82, 70, 66, 98, 76, 117, 97, 68, 117, 99, 66]
secret = [15, 12, 11, 10, 3, 59, 6, 5, 11, 59, 3, 13, 11, 59]

# Giải mã XOR tuần hoàn cho phần đầu
part1 = "".join([chr(v ^ key[i % 3]) for i, v in enumerate(thieu + ca_biet)])

# Giải mã XOR với 100 cho phần bí mật
part2 = "".join([chr(x ^ 100) for x in secret])

# Ghép kết quả
flag = f"{part1.split('thang}')[0]}{part2}thang}}"
print(f"Flag: {flag}")
```

## 6. Kết quả

> Flag: `UTECTF{Nguoi_khong_choi_la_nguoi_khong_bao_gio_thang}`

Bài học rút ra là đừng tin vào những gì mình thấy ngay (strings), mà hãy đi sâu vào logic xử lý của chương trình.
