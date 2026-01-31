---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - Shamir's Secret Sharing (Crypto)"
date: 2026-01-31
classes: wide
categories: [ctf, crypto]
tags: [hcmute, shamir, secret-sharing, rsa, aes, crypto, steganography]
permalink: /writeups/hcmute-ctf-shamir-secret-sharing/
mathjax: true
---

Hôm nay mình sẽ đi sâu phân tích một thử thách thú vị từ **HCMUTE CTF 2026**: **Shamir's Secret Sharing**. Bài viết này sẽ không chỉ đưa ra đáp án mà còn phân tích từng dòng code, từng file đề bài để hiểu rõ cơ chế hoạt động, từ đó tìm ra lỗ hổng và cách giải quyết vấn đề.

Mục tiêu là để bất kỳ ai, dù mới bắt đầu tìm hiểu về Crypto, cũng có thể hiểu được tư duy giải đề. Nào, chúng ta cùng bắt đầu!

## 1. Phân tích Bài toán (Challenge Overview)

Đầu tiên, chúng ta xem xét file `chall.py` ở thư mục gốc để nắm được bức tranh toàn cảnh.

### Phân tích Code `chall.py`

```python
# chall.py (Mô phỏng)
flag = b"UTECTF{...}"
key = b"REDACTED" # Key bị ẩn
secret = bytes_to_long(xor(flag, key)) # 1. Secret được tạo từ Flag XOR Key
shares = generate_shares(secret, k=5, n=7, P=...) # 2. Secret được chia thành 7 phần
```

**Cơ chế hoạt động:**
1.  **Secret Creation**: Bí mật (`secret`) không phải là Flag, mà là kết quả của phép XOR giữa Flag và một Key.
    $$ Secret = Flag \oplus Key $$
2.  **Shamir's Secret Sharing**: Secret này được chia nhỏ thành 7 mảnh (shares) khác nhau. Để khôi phục lại secret, ta cần thu thập đủ **5 shares** ($k=5$).

**Mục tiêu của chúng ta:**
1.  Thu thập đủ 5 shares từ các thư mục con.
2.  Dùng thuật toán Shamir để tái tạo lại `secret`.
3.  Tìm ra `key` để giải mã Flag: $Flag = Secret \oplus Key$.

---

## 2. Phân tích & Giải mã từng Share

Chúng ta sẽ đi qua từng thư mục share để thu thập mảnh ghép.

### Share 1: Khởi động

*   **File:** `share1/share1.txt`
*   **Phân tích:** Khi mở file này, chúng ta thấy ngay một tuple dữ liệu:
    ```
    (1, 10831306643861854320...)
    ```
*   **Kết luận:** Share này được tác giả "tặng" miễn phí dưới dạng Plaintext (văn bản rõ). Không cần giải mã gì thêm.

### Share 2: Layered Encoding (Bóc tách lớp mã hóa)

*   **File:** `share2/chall.py`, `share2/output.txt`

**Phân tích Code:**

Trong `share2/chall.py`, ta thấy quy trình mã hóa như sau:

```python
encoders = [encode_base64, encode_xor, encode_vigenere, encode_rot13]
for i in range(10):
    # Chọn ngẫu nhiên 1 encoder để mã hóa
    # Thêm prefix "layer{i}_" vào trước kết quả
```

Dữ liệu ban đầu bị bọc qua **10 lớp mã hóa ngẫu nhiên**. Mỗi lớp đều có một "chữ ký" nhận diện là chuỗi `layerX_` đứng đầu.

**Giải pháp:**
Chúng ta không thể đoán thủ công từng lớp. Thay vào đó, ta viết một script **đệ quy**. Tại mỗi bước, script sẽ:
1.  Đọc prefix `layerX_` để biết đang ở lớp nào.
2.  Thử giải mã bằng cả 4 phương pháp (Base64, ROT13, XOR, Vigenere).
3.  Nếu kết quả sau khi giải mã bắt đầu bằng `layer{X-1}_` (lớp kề sau), thì đó là hướng đi đúng.

**Code giải (Solver):**

```python
import base64
import codecs

def solve_share2():
    with open('share2/output.txt', 'r') as f:
        hex_data = f.read().strip()
    
    def recursive_solve(current_hex, layer_idx):
        if layer_idx == -1: return bytes.fromhex(current_hex) # Đã gỡ hết các lớp
        
        # Bóc tách phần payload
        try:
            curr_str = bytes.fromhex(current_hex).decode()
            prefix = f"layer{layer_idx}_"
            if not curr_str.startswith(prefix): return None
            payload = bytes.fromhex(curr_str[len(prefix):])
        except: return None
        
        candidates = []
        # Thử decode Base64
        try: candidates.append(base64.b64decode(payload).hex())
        except: pass
        # Thử decode ROT13
        try: candidates.append(codecs.decode(payload.decode('latin1'), 'rot_13').encode('latin1').hex())
        except: pass
        # Thử XOR & Vigenere (với key thường gặp)
        for key in [b"secretkey", b"REDACTED"]:
            candidates.append(bytes(b ^ key[i % len(key)] for i, b in enumerate(payload)).hex())
            candidates.append(bytes((b - key[i % len(key)]) % 256 for i, b in enumerate(payload)).hex())
            
        for cand in candidates:
            res = recursive_solve(cand, layer_idx - 1)
            if res: return res
        return None
        
    return recursive_solve(hex_data, 9)
```

### Share 3: RSA - Fermat Factorization

*   **File:** `share3/chall.py`, `share3/output.txt`

**Phân tích Code:**

```python
p = getPrime(1024)
q = nextPrime(p) # <--- LỖ HỔNG NGHIÊM TRỌNG
N = p * q
```

Hàm `nextPrime(p)` sẽ tạo ra số nguyên tố $q$ nằm ngay liền sau $p$. Điều này có nghĩa là khoảng cách giữa $p$ và $q$ cực kỳ nhỏ, và cả hai đều xấp xỉ $\sqrt{N}$.

**Lỗ hổng:**
Đây là điều kiện lý tưởng cho tấn công **Fermat Factorization**. Khi hai thừa số nguyên tố quá gần nhau, ta có thể tìm ra chúng nhanh chóng bằng cách bắt đầu dò từ $\sqrt{N}$.

$$ p \approx q \approx \sqrt{N} $$

**Code giải:**

```python
import math

def solve_share3():
    # Load N, c từ file output.txt
    N = 1013... 
    c = 899... 
    e = 65537
    
    # Fermat Factorization
    a = math.isqrt(N)
    b2 = a*a - N
    # Tăng a cho đến khi b2 là số chính phương
    while b2 < 0 or math.isqrt(b2)**2 != b2:
        a += 1
        b2 = a*a - N
    
    p = a - math.isqrt(b2)
    q = a + math.isqrt(b2)
    
    # Decrypt RSA như bình thường
    d = pow(e, -1, (p-1)*(q-1))
    m = pow(c, d, N)
    return m.to_bytes((m.bit_length() + 7) // 8, 'big')
```

### Share 4: AES-CTR Nonce Reuse

*   **File:** `share4/chall.py`, `cipher1.bin` (lời bài hát), `cipher_share.bin` (share)

**Phân tích Code:**

```python
KEY = get_random_bytes(16)
NONCE = b'\x00' * 8 # Nonce cố định?
# Mã hóa lyrics
c1 = AES.new(KEY, MODE_CTR, nonce=NONCE).encrypt(lyrics)
# Mã hóa share
c_share = AES.new(KEY, MODE_CTR, nonce=NONCE).encrypt(share)
```

**Lỗ hổng:**
Tác giả đã phạm một sai lầm chết người trong mode AES-CTR: **Tái sử dụng Key và Nonce** cho hai dữ liệu khác nhau (Lyrics và Share).
Trong chế độ Counter (CTR), việc mã hóa thực chất là XOR bản rõ với một dòng khóa (Keystream) được sinh ra từ Key+Nonce.

$$ C_1 = P_{lyrics} \oplus Keystream $$
$$ C_{share} = P_{share} \oplus Keystream $$

Vì ta đã biết nội dung bài hát ($P_{lyrics}$), ta có thể tính ngược ra Keystream và dùng nó để giải mã Share.

**Code giải:**

```python
def solve_share4():
    with open('share4/cipher1.bin', 'rb') as f: c1 = f.read()
    with open('share4/cipher_share.bin', 'rb') as f: c_share = f.read()
    
    # Lời bài hát (được cung cấp hoặc search Google)
    lyrics = b"\nWhen you were here before\nCouldn't look you in the eye..."
    
    # Tính Keystream
    keystream = bytes(x ^ y for x, y in zip(c1, lyrics * 5))
    
    # Giải mã Share
    share_bytes = bytes(x ^ y for x, y in zip(c_share, keystream))
    return share_bytes
```

### Share 5: Steganography (Giấu tin)

*   **File:** `share5/chall.py`

**Phân tích Code:**
Khi mở file `chall.py` bằng trình soạn thảo code, nó trông như một đoạn code Python bình thường in ra chữ "Hello".
Tuy nhiên, nếu kiểm tra kỹ các **dòng trống** (hoặc dùng Hex Editor), ta sẽ thấy chúng chứa đầy các ký tự **Space** và **Tab**.

**Nhận định:**
Đây là kỹ thuật giấu tin (Steganography). Quy ước phổ biến trong các bài CTF dạng này là:
*   Tab (`\t`) = bit 1
*   Space (` `) = bit 0

**Code giải:**

```python
def solve_share5():
    with open('share5/chall.py', 'r') as f:
        lines = f.readlines()
    
    binary = ""
    for line in lines:
        stripped = line.strip('\r\n')
        if not stripped.strip(): # Chỉ xét các dòng trông có vẻ "trống"
            for char in stripped:
                if char == '\t': binary += '1'
                elif char == ' ': binary += '0'
    
    # Convert binary string to ASCII text
    chars = []
    for i in range(0, len(binary), 8):
        chars.append(chr(int(binary[i:i+8], 2)))
    return "".join(chars)
```

---

## 3. Tổng hợp và Lấy Flag

### Bước 1: Tái tạo Secret (Lagrange Interpolation)

Sau khi có đủ 5 shares từ các bước trên, ta quay lại bài toán chính. Chúng ta cần dùng công thức **Nội suy Lagrange** để tìm lại đa thức gốc $f(x)$, từ đó tính $f(0)$ chính là `secret`.

```python
def lagrange_interpolate(shares, p):
    x = 0 # Ta cần tìm f(0)
    k = len(shares)
    secret = 0
    for i in range(k):
        xi, yi = shares[i]
        num, den = 1, 1
        for j in range(k):
            if i == j: continue
            xj, yj = shares[j]
            num = (num * (x - xj)) % p
            den = (den * (xi - xj)) % p
        term = (yi * num * pow(den, -1, p)) % p
        secret = (secret + term) % p
    return secret
```

Kết quả trả về là một số nguyên rất lớn (`secret`).

### Bước 2: Tìm Key và "Cú lừa" cuối cùng

File `secret_key.txt` do đề cung cấp có nội dung là `secretkey`.
Theo logic thông thường: `Flag = Secret XOR key`.
Tuy nhiên, khi thử XOR `secret` vừa tìm được với `b"secretkey"`, kết quả lại ra một chuỗi rác `\x1d...`.

**Phân tích lại:**
*   Secret ta đính toán ra con số toán học chính xác từ 5 phương trình, khả năng sai là rất thấp.
*   Vậy khả năng cao là **Key bị sai**.

Ta biết format của Flag luôn bắt đầu bằng `UTECTF{`. Ta có thể lợi dụng điều này để tìm ra Key thực sự:

$$ Key_{real} = Secret \oplus \text{"UTECTF{"} $$

Khi thực hiện phép tính này với 7 byte đầu tiên, ta nhận được chuỗi `secret_`.
$\rightarrow$ **Kết luận:** Key đúng phải là `secret_key` (có thêm dấu gạch dưới `_`), file text đề bài đã bị thiếu mất dấu này!

### Bước 3: Final Code

```python
def get_flag(secret_int):
    secret_bytes = secret_int.to_bytes((secret_int.bit_length() + 7) // 8, 'big')
    
    # Key chuẩn tìm được qua phân tích
    real_key = b"secret_key" 
    
    flag = bytes(b ^ real_key[i % len(real_key)] for i, b in enumerate(secret_bytes))
    return flag.decode()
```

**Kết quả Flag:**
```
UTECTF{c0ngr4_0n_u51ng_5h4m1r5_53cr3t_5h4r1ng_5ucc355fully}
```

Chúc mừng các bạn đã kiên trì đi đến cuối cùng! Hy vọng bài viết này giúp các bạn hiểu rõ hơn về cách tiếp cận một bài CTF tổng hợp nhiều kỹ thuật như thế nào. hẹn gặp lại ở các bài writeup sau!
