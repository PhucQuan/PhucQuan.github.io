---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - Mirror Split Secrets (Crypto)"
date: 2026-01-29
classes: wide
categories: [ctf, crypto]
tags: [hcmute, rsa, lattice, lll, coppersmith, acd]
permalink: /writeups/hcmute-ctf-mirror-split/
mathjax: true
---

Chào mọi người, hôm nay mình sẽ chia sẻ về một bài Crypto rất hay trong giải HCMUTE CTF vừa qua: **Mirror Split Secrets**. Đây không chỉ là một bài toán tìm Flag, mà là cơ hội tuyệt vời để hiểu sâu hơn về **Lattice Attack** (Tấn công mạng tinh thể) trong RSA.

## 1. Tóm tắt thử thách

- **Đề bài:** Một lá cờ đã được mã hóa bằng AES-CBC, khóa AES này lại được bảo vệ bằng RSA. Tuy nhiên, các giá trị RSA công khai (Public Key) đã bị làm "nhiễu".
- **Dữ liệu:** File `chall.py` (Source code) và `output.txt` (Dữ liệu đầu ra).

## 2. Phân tích mã nguồn (Reconnaissance)

Đọc `chall.py`, mình nhận thấy quy trình tạo khóa RSA rất bất thường:

### Vấn đề 1: Shared Prime (Dùng chung số nguyên tố)

Tác giả tạo ra 4 Modulus ($N_0, N_1, N_2, N_3$) khác nhau. Tuy nhiên, tất cả chúng đều **dùng chung một số nguyên tố $p$** (1024-bit).

$$ N_i \approx p \cdot q_i $$

Nếu không có gì thay đổi, đây là lỗi cơ bản **Shared Prime Attack**. Chỉ cần tính $GCD(N_i, N_j)$ là tìm ra ngay $p$.

### Vấn đề 2: Noise (Nhiễu)

Nhưng đời không như mơ, tác giả đã cộng thêm một lượng "nhiễu" ngẫu nhiên 256-bit vào mỗi modulus:

$$ N'_i = (p \cdot q_i) + \text{noise}_i $$

Chính vì cái $\text{noise}_i$ này mà phép tính GCD thông thường sẽ vô dụng, vì $N'_i$ không còn chia hết cho $p$ nữa.

$\rightarrow$ Đây chính là bài toán **Approximate Common Divisor (ACD)** - Ước chung gần đúng.

## 3. Lý thuyết tấn công (Lattice Attack)

Để giải quyết bài toán ACD, chúng ta cần dùng đến **Lattice Reduction (LLL)**.

Hãy tưởng tượng $p$ là một "nhịp điệu" chính, và các $N'_i$ là các nốt nhạc bị lệch nhịp một chút. LLL giúp ta tìm lại nhịp điệu gốc bằng cách xây dựng một ma trận biểu diễn mối quan hệ giữa các số này.

Chúng ta sẽ dựng một ma trận $B$ (Basis Matrix) như sau:

$$
B = \begin{bmatrix}
M & N'_1 & N'_2 & N'_3 \\
0 & -N'_0 & 0 & 0 \\
0 & 0 & -N'_0 & 0 \\
0 & 0 & 0 & -N'_0
\end{bmatrix}
$$

*Trong đó $M = 2^{256}$ là trọng số (weight) tương ứng với độ lớn của nhiễu mà ta muốn khử.*

Khi chạy thuật toán **LLL** trên ma trận này, nó sẽ tìm cho ta một vector ngắn nhất. Vector này chứa thông tin về các số $q_i$ (thừa số còn lại). Từ đó ta có thể tính ngược lại ra $p$:

$$ q_0 \approx \frac{\text{vector}[0]}{M} \rightarrow p \approx \frac{N'_0}{q_0} $$

## 4. Các bước giải quyết (Solution)

### Bước 1: Trích xuất dữ liệu

Đầu tiên, mình viết script Python để parse file `output.txt` và lấy các giá trị $N'_i$ cũng như chuỗi Hex bị mã hóa.

### Bước 2: Khôi phục $p$ bằng LLL

Mình sử dụng thư viện `decimal` của Python để tính toán với độ chính xác cao, cài đặt thuật toán LLL trên ma trận $4 \times 4$.

Sau khi chạy LLL, mình tìm được vector ngắn nhất $v$. Lấy phần tử đầu tiên chia cho $M$, mình thu được $q_0$. Lấy $N'_0$ chia nguyên cho $q_0$, mình tìm được **$p$**.

### Bước 3: Khôi phục Modulus chuẩn và Private Key

Khi đã có $p$ xịn, mình dễ dàng loại bỏ nhiễu để tìm lại $N_i$ gốc:

$$ N_i = \left\lfloor \frac{N'_i}{p} \right\rfloor \cdot p $$

Từ đó tính lại $q_i = N_i / p$, tính $\phi(N_i)$ và suy ra private key $d$.

### Bước 4: Giải mã AES

Có $d$, mình giải mã đoạn text RSA để lấy lại **AES Key**. Cuối cùng, dùng AES Key để giải mã Flag.

## 5. Kết luận

- **Flag:** `UTECTF{W3_l0v3_A35_4nd_R54}`
- **Bài học:** 
    1. Không bao giờ tái sử dụng số nguyên tố trong RSA.
    2. Việc thêm nhiễu (Noise) nhỏ không đủ để che giấu cấu trúc toán học bên dưới; LLL là công cụ cực mạnh để "lọc nhiễu" này.

Hy vọng bài viết giúp bạn hình dung rõ hơn về sức mạnh của Toán học trong Cryptography!
