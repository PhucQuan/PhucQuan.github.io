---
layout: single
title: "[Writeup] UTECTF 2026 - What is a secret (Crypto)"
date: 2026-01-29
classes: wide
categories: [HCMUTE CTF 2026, crypto]
tags: [utectf, rsa, diffie-hellman, aes, multi-prime, gcd-attack]
permalink: /writeups/utectf-what-is-a-secret/
mathjax: true
---

Chào mừng các bạn quay trở lại với series UTECTF. Hôm nay mình sẽ chia sẻ về bài **What is a secret** - một bài Crypto cực hay kết hợp nhiều kỹ thuật mã hóa khác nhau.

Đây là bài challenge cuối cùng mình muốn chia sẻ, và cũng là bài mình tâm đắc nhất vì nó kết hợp một cách "nhuần nhuyễn" nhiều kỹ thuật mã hóa kinh điển: **Multi-prime RSA**, **Diffie-Hellman** và **AES**.


Nhiệm vụ của chúng ta là giải mã cuộc hội thoại này, tìm ra "bí mật" mà nhân vật Khoa để lại cho Huy sau khi chặn block.


**Thông tin Challenge:**
- **Thể loại:** Cryptography
- **Độ khó:** Medium
- **Tác giả:** NotName
- **Flag format:** UTECTF{...}

## 1. Tổng quan

Đây là một bài crypto "hạng nặng" khi kết hợp:
- **RSA với multi-prime** (3 số nguyên tố).
- **Diffie-Hellman Key Exchange**.
- **AES-CBC encryption**.
- **Password-protected RAR archives**.

Nhiệm vụ của chúng ta là khôi phục `private_a` và `private_b` để giải mã được password, từ đó mở các file RAR chứa video có flag.

### Mô tả Challenge

Theo file `Nhật kí hackor lỏ.txt`:

> "Tôi là 1 hackor và đã xâm nhập vào được 1 cuộc trò chuyện riêng tư giữa 2 người đàn ông và đã nghe lén được thông tin cuộc trò chuyện nhưng vì nó đã bị mã hóa tôi không thể xem được liệu bạn có thể giúp tôi không. Thứ tôi biết chỉ là 2 người nhắn với nhau về thông tin của họ nhưng họ mã hóa rồi mới gửi và không hiểu sao Khoa đã chặn Huy và để lại cho Huy 1 thứ bí mật và bạn sẽ cần tìm ra bí mật đó."

**Gợi ý quan trọng:** Flag nằm trong video và mỗi `private_a`, `private_b` đều có nghĩa khi chuyển từ số sang bytes.

## 2. Phân tích

### Files được cung cấp

1.  **`source_code/source_code.py`** - Code mã hóa password sử dụng Diffie-Hellman và AES.
2.  **`source_code/data.txt`** - Chứa public keys A, B và encrypted data.
3.  **`private_a/`** - Chứa dữ liệu RSA để tìm private_a:
    - `private_a.txt` - Chứa $p \cdot r$, $q \cdot r$, $e$, và ciphertext.
    - `source_code_private_a.py` - Source code mã hóa `private_a`.
4.  **`private_b.txt`** - Chứa phương trình để tìm `private_b`.
5.  **`secret1.rar`** - Archive được bảo vệ bằng password (1.4 MB).
6.  **`secret2.rar`** - Archive được bảo vệ bằng password (6.2 MB).
7.  **`Huy(h26v).jpg`** và **`Khoa.jpg`** - Hình ảnh của 2 nhân vật.
8.  **`Nhật kí hackor lỏ.txt`** - Mô tả challenge và hints.

### Điểm yếu 1: Multi-prime RSA với $p \cdot r$ và $q \cdot r$

Trong thư mục `private_a`, chúng ta có:
```
p*r: 926619434090753147...
q*r: 858797427760567410...
e = 65537
ciphertext a: 103578189563527636...
```

**Lỗ hổng: Shared Prime (Chung nhân tử)**

Trong RSA chuẩn, $n = p \cdot q$ với $p, q$ là hai số nguyên tố bí mật. Việc tìm $p, q$ từ $n$ là bài toán khó (factorization).

Tuy nhiên, ở đây tác giả cho chúng ta hai số lớn:
- $X = p \cdot r$
- $Y = q \cdot r$

Điều thú vị là cả hai số này đều có chung một nhân tử là $r$. Trong số học, tìm ước chung lớn nhất (GCD) của hai số là một bài toán cực kỳ dễ giải (thuật toán Euclid chạy trong tích tắc).

Hãy tưởng tượng:
- $X = 15 (3 \cdot 5)$
- $Y = 21 (3 \cdot 7)$
- Chỉ cần tính `gcd(15, 21)` là ta tìm ra ngay số 3 chung!

Áp dụng vào đây, ta tìm được $r$ ngay lập tức, từ đó dễ dàng suy ra $p$ và $q$. Đây là một lỗi implementation kinh điển khi sử dụng lại các số nguyên tố không an toàn.

### Điểm yếu 2: Phương trình tìm private_b

File `private_b.txt` cung cấp phương trình:
```
K * a + 7 = 7065992525133470866235566390332970
với K nằm trong khoảng từ 1 đến 10
private_b có ý nghĩa
```

**Lỗ hổng:** Do $K$ rất nhỏ (1 đến 10), ta chỉ cần **Brute-force** thử từng giá trị $K$ và kiểm tra xem kết quả `private_b` (là $a$) có phải là chuỗi văn bản có nghĩa hay không.

## 3. Khai thác (Exploitation)

Sơ đồ tấn công tổng quát:

```
┌─────────────────┐
│   private_a/    │
│   (RSA data)    │
└────────┬────────┘
         │ GCD Attack
         ▼
┌─────────────────────────┐      ┌──────────────────┐
│ private_a =             │      │  private_b.txt   │
│ "t thich Ly Van Huu Hoa"│      │  (Equation)      │
└──────────┬──────────────┘      └────────┬─────────┘
           │                               │ Brute-force K
           │                               ▼
           │                      ┌────────────────────┐
           │                      │ private_b =        │
           │                      │ "t thich m Khoa"   │
           │                      └──────────┬─────────┘
           │                                 │
           └────────────┬────────────────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │  Diffie-Hellman        │
           │  + AES Decryption      │
           └────────────┬───────────┘
                        │
                        ▼
           ┌────────────────────────┐
           │  Password recovered:   │
           │  "hamburgre7796"       │
           └────────────┬───────────┘
                        │
           ┌────────────┴───────────┐
           │                        │
           ▼                        ▼
    ┌──────────┐            ┌──────────────┐
    │secret1.rar│            │ secret2.rar  │
    │ pwd:898989│            │pwd:hamburgre │
    └─────┬─────┘            └──────┬───────┘
          │                         │
          ▼                         ▼
      secret.mp4                 secret2.mp4
                                    │
                                    ▼
                               FLAG
```

### Bước 1: Phá RSA để lấy private_a

Sử dụng script Python để tính GCD và giải mã RSA 3 số nguyên tố:

```python
from math import gcd

# Lấy từ file private_a.txt
pr = 92661943409075314756161661200275870549661687062672715767255951008156084361905855922274375535484573907678585969334107374238211890556931737535690184256909523220256963889511962921613380751146141447886363342367264400585586939023223965693700467463315430135868372198782561043603914096929577861301360285232282200873
qr = 85879742776056741075513003360292355592400163545590975981282500015454163654490411150605120228468916749146964485625689593527561099692303427882000985215888055491875382286129026090951444905968960070494043462701865341238266854994784771289717636052258752366276973197344397086813798124648453915042791340825173822311

# Tìm r bằng GCD
r = gcd(pr, qr)
p = pr // r
q = qr // r

# Tính modulus và phi
n = p * q * r
phi = (p - 1) * (q - 1) * (r - 1)

# Tính private key
e = 65537
d = pow(e, -1, phi)

# Giải mã ciphertext
ct_a = 1035781895635276368587807537615278757068367775282623158697213855368619256055006539229536704723754062830347162336302237415498891999553808077001364444784610189072856847341294725931304865148356685979687993518095029213272588451761251728872584142770487230707593872256055142082242083421107526461266522188334094781638987283516145241051912171010123308970052327920972969551122794217010157465376555887087833959251356846248820032937782904576198691751997174772657211578009008

private_a_int = pow(ct_a, d, n)
private_a_bytes = private_a_int.to_bytes((private_a_int.bit_length() + 7) // 8, 'big')

print(f"private_a: {private_a_bytes}")
# Output: b't thich Ly Van Huu Hoa'
```

**Kết quả:** `private_a = "t thich Ly Van Huu Hoa"`

### Bước 2: Giải phương trình tìm private_b

```python
target = 7065992525133470866235566390332970

# Thử tất cả giá trị K từ 1 đến 10
for K in range(1, 11):
    if (target - 7) % K == 0:
        private_b_candidate = (target - 7) // K
        private_b_bytes = private_b_candidate.to_bytes(
            (private_b_candidate.bit_length() + 7) // 8, 'big'
        )
        
        try:
            text = private_b_bytes.decode('utf-8', errors='ignore')
            print(f"K={K}: {text}")
        except:
            pass
```

**Kết quả:**
- K=1: `\x01\\a]9<*8aG` (không có ý nghĩa)
- **K=3: `t thich m Khoa`** (có ý nghĩa!)
- K=9: `&\xb5|"\xcd\xcb...` (không có ý nghĩa)

-> **`private_b = "t thich m Khoa"`** (với $K=3$).

### Bước 3: Diffie-Hellman và giải mã AES

Đây là phần mình thấy hay nhất của bài. Làm sao hai người có thể thống nhất một mật khẩu chung để chat (key AES) mà không cần gửi mật khẩu đó qua mạng (nơi hacker đang nghe lén)?

Giao thức Diffie-Hellman giải quyết việc này dựa trên bài toán **Logarit rời rạc**:
1.  Hai bên thống nhất số nguyên tố $P$ và cơ số $g$.
2.  Mỗi người giữ bí mật số riêng (`private_a`, `private_b`).
3.  Họ chỉ gửi cho nhau "Public Key" ($A = g^{priv\_a}, B = g^{priv\_b}$).

**Điều kỳ diệu:**
$$ (g^{priv\_a})^{priv\_b} \equiv (g^{priv\_b})^{priv\_a} \pmod P $$

Cả Huy và Khoa đều tính ra cùng một con số $S$ (Shared Secret) mà hacker (chúng ta) dù có nghe được $A$ và $B$ cũng không thể tính ngược lại $priv\_a$ hay $priv\_b$ để tìm ra $S$.

Tuy nhiên, vì ở các bước trước ta đã chiếm được cả `private_a` và `private_b` của họ, nên ta đóng vai "người thứ 3 toàn năng", tự tính ra được bí mật này!

Sau khi có `private_a` (từ RSA) và `public_B` (từ file data), ta tính Shared Secret và dùng nó để giải mã AES.

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

# Thông số Diffie-Hellman
p_dh = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
g = 2

# Public keys từ data.txt
public_A = 27335268679471141320013033687811874574103282967534392523324611477681842709489
public_B = 11760590316265328134331187072290377010144570043020682579923041681609516248568

# Tính shared secret (dùng private_a)
private_a_int = int.from_bytes(b't thich Ly Van Huu Hoa', 'big')
private_b_int = int.from_bytes(b't thich m Khoa', 'big')

dh_secret = pow(public_B, private_a_int, p_dh)

# Tạo final secret
final_secret = hashlib.sha256(
    str(dh_secret).encode() +
    private_a_int.to_bytes((private_a_int.bit_length() + 7) // 8, 'big') +
    private_b_int.to_bytes((private_b_int.bit_length() + 7) // 8, 'big')
).digest()

# Giải mã AES
iv = bytes.fromhex('6169a30ce641cad26b719063c9c33596')
encrypted_flag = bytes.fromhex('41d3a5ba53e80ec7b192066785c284b86568bc0c2f03108fe81ee01582dd215b')

key = final_secret[:16]
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = unpad(cipher.decrypt(encrypted_flag), 16)

print(f"Decrypted message: {decrypted.decode()}")
# Output: mat khau la: hamburgre7796
```

Chúng ta nhận được password: **`hamburgre7796`**.

### Bước 4: Giải nén các file RAR để tìm flag

Sau khi giải mã, chúng ta có 2 mật khẩu tiềm năng:
1.  `898989` - Password gốc trong `source_code.py` (line 6: `key_secret = b'mat khau la: 898989'`).
2.  `hamburgre7796` - Password đã được mã hóa và giải mã thành công từ AES.

**Quan sát:** Trong source code, hàm `encrypt_flag()` mã hóa biến `key_secret`, không phải flag. Điều này có nghĩa:
- Password ban đầu là `898989`.
- Password này được mã hóa thành `hamburgre7796`.
- Cả hai đều có thể là password cho các RAR files!

Thử giải nén:

```bash
# Thử secret1.rar với password gốc
$ unrar x -p898989 secret1.rar
# -> THÀNH CÔNG! Trích xuất được secret.mp4

# Thử secret2.rar với password đã giải mã
$ unrar x -phamburgre7796 secret2.rar
# -> THÀNH CÔNG! Trích xuất được secret2.mp4
```

**Kết luận:**
- `secret1.rar` dùng password **`898989`** (của Khoa).
- `secret2.rar` dùng password **`hamburgre7796`** (của Huy).

## Flag

Xem video `secret2.mp4` giải nén được, ở khung hình cuối cùng ta nhận được Flag:

![Flag What is a secret](/assets/images/utectf/flag_what_is_secret.png)

> **Flag:** `UTECTF{R1s3_o5_K1ngd0m3}`

---

## Tổng kết: Cái hay của bài toán

Cá nhân mình đánh giá đây là một bài Crypto rất "đẹp". Cái đẹp không nằm ở việc tính toán phức tạp, mà ở sự kết nối logic:

1.  **Sự trừng phạt cho việc lười biếng:** Tác giả dùng lại số nguyên tố $r$ (Shared Prime), dẫn đến sụp đổ toàn bộ lớp bảo mật RSA.
2.  **Sự nguy hiểm của gợi ý:** Phương trình tìm `private_b` quá đơn giản, biến một tham số bí mật thành bài toán Brute-force lớp 2.
3.  **Niềm tin đặt sai chỗ:** Huy và Khoa tin vào thuật toán Diffie-Hellman và AES (vốn rất an toàn), nhưng họ lại xây dựng nó trên nền móng yếu (Private Key bị lộ).

Bài học xương máu: **"Một hệ thống bảo mật chỉ mạnh bằng mắc xích yếu nhất của nó."** Dù bạn có dùng AES-256 hay RSA-4096, nhưng nếu để lộ Private Key qua một lỗi sơ đẳng, tất cả đều trở nên vô nghĩa.

Hy vọng qua bài writeup này, các bạn không chỉ biết cách giải mà còn cảm nhận được vẻ đẹp của toán học đằng sau các con số! Hẹn gặp lại các bạn ở các giải CTF tiếp theo!
