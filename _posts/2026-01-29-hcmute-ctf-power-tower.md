---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - Power Tower (Crypto)"
date: 2026-01-29
classes: wide
categories: [ctf, crypto]
tags: [hcmute, rsa, modular-arithmetic, euler, python]
permalink: /writeups/hcmute-ctf-power-tower/
mathjax: true
---

Tiếp tục series Crypto, hôm nay chúng ta sẽ đến với bài **Power Tower** (Tháp Lũy Thừa). Đây là một bài toán kinh điển về Số học module, giúp bạn hiểu sâu sắc về Định lý Euler.

## 1. Phân tích bài toán

Chúng ta được cung cấp:
- `chall.py`: Mã nguồn tạo ra thử thách.
- `n`: Một số module rất lớn (khoảng 256 bit).
- Code tạo key theo kiểu "tháp lũy thừa":

```python
int_key = 1
primes = [2, 3, 5, ..., 97] # 25 số nguyên tố đầu tiên
for p in primes:
    int_key = p ** int_key
key = int_key % n
```

Tức là chúng ta cần tính:

$$ K = 97^{89^{\dots^{3^{2^1}}}} \pmod n $$

Con số này **cực kỳ lớn**, máy tính không thể nào lưu trữ trực tiếp giá trị của tháp lũy thừa này được. Vậy làm sao để tính số dư của nó khi chia cho $n$?

## 2. Cơ sở toán học

Chìa khóa ở đây là **Định lý Euler** và **Hàm Carmichael**.

### Định lý Euler
Nếu $gcd(a, n) = 1$, thì:
$$ a^{\phi(n)} \equiv 1 \pmod n $$
Điều này cho phép ta giảm số mũ:
$$ a^b \equiv a^{b \pmod{\phi(n)}} \pmod n $$

### Vấn đề: Không nguyên tố cùng nhau?
Trong bài này, $n$ có thể chia hết cho các cơ số nhỏ (ví dụ $n$ chia hết cho 2, 3...). Khi đó định lý Euler cơ bản không áp dụng được trực tiếp.
Tuy nhiên, với tháp lũy thừa cao ngất ngưởng thế này, số mũ $b$ chắc chắn **đủ lớn** ($b \ge \phi(n)$). Ta có định lý mở rộng:

$$ a^b \equiv a^{b \pmod{\phi(n)} + \phi(n)} \pmod n $$

Công thức này luôn đúng kể cả khi $a$ và $n$ có ước chung!

## 3. Chiến lược giải quyết (Recursion)

Để tính $a^{b} \pmod m$, ta cần tính số mũ mới là $b' = b \pmod{\phi(m)}$.
Mà $b$ lại là một lũy thừa khác, nên ta lại áp dụng quy tắc trên cho $b'$ với module là $\phi(m)$.

Cứ thế, ta xây dựng một chuỗi các module giảm dần:
1. $m_0 = n$
2. $m_1 = \phi(m_0)$ (hoặc tốt hơn là dùng hàm Carmichael $\lambda(m_0)$ để số nhỏ hơn)
3. $m_2 = \phi(m_1)$
...
cho đến khi $m_k = 1$. (Vì mod 1 luôn bằng 0, ta dừng lại).

### Bước 1: Phân tích n (Factorization)
Số $n$ trong bài không quá lớn, ta có thể factor nó ra thành các thừa số nguyên tố:
$$ n = 127 \cdot p_1 \cdot p_2 $$
Từ đó tính được $\phi(n)$ hoặc $\lambda(n)$.

### Bước 2: Xây dựng chuỗi module
Mình viết script tự động tính $\lambda(m_i)$ liên tiếp để tạo ra danh sách các module cần dùng cho từng tầng của tháp.

### Bước 3: Đệ quy tính ngược
Hàm `solve_tower(tầng, module)` sẽ:
- Nếu ở đỉnh tháp: trả về giá trị cơ sở.
- Nếu chưa đỉnh:
    - Gọi đệ quy để tính số mũ ở tầng trên: `exp = solve_tower(tầng+1, phi(module))`
    - Tính giá trị tầng hiện tại: `pow(cơ_số, exp + phi(module), module)`

## 4. Kết quả

Sau khi chạy script, ta tính được `int_key % n` một cách nhanh chóng (chưa đến 1 giây).
Dùng key này giải mã file `cipher.txt` (AES) là ra Flag.

- **Flag:** `UTECTF{p0w3r_t0w3r_1s_s3cur1ty_r1ght?}`

Qua bài này, các bạn hãy nhớ: **Trong thế giới Modular Arithmetic, số mũ không cần quá lớn, chỉ cần tính đúng theo chu kỳ $\phi(n)$ là đủ!**
