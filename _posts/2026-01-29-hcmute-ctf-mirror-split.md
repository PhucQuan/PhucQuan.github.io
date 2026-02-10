---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - Mirror Split Secrets (Crypto)"
date: 2026-01-29
classes: wide
categories: [HCMUTE CTF 2026, crypto]
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

### Full Solve Script

Dưới đây là toàn bộ source code để giải bài này:

```python
import sys
import re
from decimal import Decimal, getcontext
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    from Crypto.Util.number import long_to_bytes, inverse
except ImportError:
    print("Please install pycryptodome: pip install pycryptodome")
    sys.exit(1)

# Set high precision for large number calculations
getcontext().prec = 6000

# --- LLL Algorithm Implementation ---

def decimal_dot(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

def vector_sub(v1, v2):
    return [x - y for x, y in zip(v1, v2)]

def vector_scale(v, s):
    return [x * s for x in v]

def vector_scale_int(v, s):
    return [x * int(s) for x in v]

def lll_reduction(basis, delta=Decimal("0.75")):
    """
    LLL lattice reduction algorithm using Decimal for Gram-Schmidt coefficients.
    Used to find short vectors in a lattice.
    """
    n = len(basis)
    if n == 0: return basis
    
    # Work with a copy of the basis
    b = [list(row) for row in basis]
    
    def compute_all_gs(current_basis):
        """Recompute Gram-Schmidt orthogonalization."""
        b_s = [] 
        mu = [[Decimal(0)] * n for _ in range(n)]
        sq_norms = [Decimal(0)] * n
        
        for i in range(n):
            vec = [Decimal(x) for x in current_basis[i]]
            for j in range(i):
                dot_val = decimal_dot(current_basis[i], b_s[j])
                if sq_norms[j] == 0:
                    mu[i][j] = Decimal(0)
                else:
                    mu[i][j] = dot_val / sq_norms[j]
                
                vec = vector_sub(vec, vector_scale(b_s[j], mu[i][j]))
            
            b_s.append(vec)
            sq_norms[i] = decimal_dot(vec, vec)
            mu[i][i] = Decimal(1)
            
        return b_s, mu, sq_norms

    b_star, mu, sq_norms = compute_all_gs(b)
    
    k = 1
    loop_count = 0
    while k < n:
        loop_count += 1
        if loop_count % 500 == 0:
            print(f"[*] LLL Iteration {loop_count}, k={k}")
        
        # Size reduction condition
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Decimal("0.5"):
                q = int(round(mu[k][j]))
                b[k] = vector_sub(b[k], vector_scale_int(b[j], q))
                b_star, mu, sq_norms = compute_all_gs(b)

        # Lovasz condition check
        if sq_norms[k] >= (delta - mu[k][k-1]**2) * sq_norms[k-1]:
            k += 1
        else:
            b[k], b[k-1] = b[k-1], b[k]
            b_star, mu, sq_norms = compute_all_gs(b)
            k = max(k - 1, 1)
            
    return b

# --- Challenge Logic ---

def parse_output(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: ouput.txt not found.")
        return None

    patterns = {
        'Ciphertext': r'Ciphertext = ([0-9a-fA-F]+)',
        'IV': r'IV = ([0-9a-fA-F]+)',
        'Scrambled_keys': r'Scrambled_keys = (\[.*?\])',
        'Number': r'Number=\s*(\[.*?\])',
        'e': r'e = (\d+)'
    }

    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            value = match.group(1)
            if key in ['Scrambled_keys', 'Number']:
                data[key] = eval(value)
            elif key == 'e':
                data[key] = int(value)
            else:
                data[key] = value
    return data

def solve():
    print("[*] Parsing ouput.txt...")
    data = parse_output("ouput.txt")
    if not data: return

    Numbers = data['Number']
    scrambled_keys = data['Scrambled_keys']
    e = data['e']
    
    print(f"[*] Found {len(Numbers)} approximate moduli.")
    
    # Attack Strategy:
    # We have moduli N'_i = p * q_i + r_i (where r_i is small noise).
    # This is the "Approximate Common Divisor" problem.
    # We construct a lattice to recover the common factor p.
    # We use a large weight M to force the lattice reduction to find the structure.
    
    N0 = Numbers[0]
    others = Numbers[1:]
    
    # Weight M should be ~ size of noise (2^256)
    M = 1 << 256
    
    basis = []
    # Row 0: [M, N1, N2, N3]
    row0 = [M] + others
    basis.append(row0)
    
    # Subsequent rows: [0, -N0, 0, 0], [0, 0, -N0, 0], etc.
    # This effectively searches for linear combinations like:
    # A*N0 - B*N1 approx small
    for i in range(len(others)):
        row = [0] * (len(others) + 1)
        row[i+1] = -N0
        basis.append(row)
        
    print("[*] Running LLL reduction (this may take a minute)...")
    reduced_basis = lll_reduction(basis)
    
    p_candidate = None
    
    print("[*] Analyzing reduced basis...")
    for row in reduced_basis:
        # The first element is M * q0_candidate.
        val = abs(row[0])
        if val > 0 and val % M == 0:
            q0_candidate = val // M
            # Determine p from N0 = p*q0 + r0 approximately
            if q0_candidate > 0:
                p_approx = N0 // q0_candidate
                # To be precise: p = (N0 - (N0 % q0)) / q0
                r0 = N0 % q0_candidate
                p = (N0 - r0) // q0_candidate
                
                # Check if p looks like a 1024-bit prime
                if p.bit_length() > 1000:
                    p_candidate = p
                    break
    
    if not p_candidate:
        print("[-] Failed to recover p.")
        return

    print(f"[+] Recovered common prime p: {p_candidate}")
    
    # Decrypt AES Key using recovered p
    print("[*] Attempting to decrypt AES key...")
    
    aes_key = None
    key_found = False
    
    for i in range(len(Numbers)):
        N_prime = Numbers[i]
        # Recover exact N_i (remove noise)
        r = N_prime % p_candidate
        N_actual = N_prime - r
        q = N_actual // p_candidate
        
        # Calculate standard RSA private key
        phi = (p_candidate - 1) * (q - 1)
        try:
            d = inverse(e, phi)
            enc_key_int = scrambled_keys[i]
            dec_key_int = pow(enc_key_int, d, N_actual)
            dec_key_bytes = long_to_bytes(dec_key_int)
            
            # The challenge pads the key with a splitter string
            if b'<--- this key' in dec_key_bytes:
                parts = dec_key_bytes.split(b'<--- this key')
                # The first part is the start of the key
                # The second part is the end of the key (due to the loop structure in chall.py)
                # Combined, they form the full key.
                full_key = parts[0] + parts[1]
                aes_key = full_key[:16] # AES key is 16 bytes
                print(f"[+] Decrypted AES Key: {aes_key.hex()}")
                key_found = True
                break
        except Exception:
            continue

    if key_found:
        ciphertext_hex = data['Ciphertext']
        iv_hex = data['IV']
        
        ciphertext = bytes.fromhex(ciphertext_hex)
        iv = bytes.fromhex(iv_hex)
        
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        try:
            plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
            print("-" * 30)
            print(f"FLAG: {plaintext.decode()}")
            print("-" * 30)
        except Exception as ex:
            print(f"[-] Decryption failed: {ex}")
    else:
        print("[-] Could not decrypt AES key.")

if __name__ == "__main__":
    solve()
```

## 5. Kết luận

- **Flag:** `UTECTF{W3_l0v3_A35_4nd_R54}`
- **Bài học:** 
    1. Không bao giờ tái sử dụng số nguyên tố trong RSA.
    2. Việc thêm nhiễu (Noise) nhỏ không đủ để che giấu cấu trúc toán học bên dưới; LLL là công cụ cực mạnh để "lọc nhiễu" này.

Hy vọng bài viết giúp bạn hình dung rõ hơn về sức mạnh của Toán học trong Cryptography!
