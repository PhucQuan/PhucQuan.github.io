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


### Full Solve Script

Dưới đây là đoạn code Python đầy đủ để giải quyết bài toán này:

```python
from Crypto.Util import number
from Crypto.Cipher import AES
from math import gcd

# Thông số bài toán
n = 107502945843251244337535082460697583639357473016005252008262865481138355040617
primes = [p for p in range(100) if number.isPrime(p)]

# 1. Phân tích n (dựa trên kết quả factordb và tính toán trước đó)
# n = 127 * p1 * p2
p1 = 841705194007
p2 = 1005672644717572752052474808610481144121914956393489966622615553
factors_n = [127, p1, p2]

# 2. Xây dựng chuỗi module lambda(n)
# Hàm tính LCM
def lcm(a, b):
    if a == 0 or b == 0: return 0
    return abs(a * b) // gcd(a, b)

# Hàm hỗ trợ thêm các thừa số nguyên tố của p-1 vào tập hợp (để tính bước tiếp theo)
def add_p_minus_1_factors(p, target_set):
    val = p - 1
    # Xử lý các trường hợp đặc biệt (các số lớn đã biết phân tích từ factordb)
    # q4 = 998...
    if p == 998813938056801811539097:
        target_set.update([2, 3, 67, 621152946552737444987])
        return
    # q3 = 616...
    if p == 616095937974917:
        target_set.update([2, 7, 937, 3354692233])
        return
    # q2 = 457...
    if p == 4579960207:
        target_set.update([2, 3, 139, 5491559])
        return
    # q1 = 195...
    if p == 1957681487:
        target_set.update([2, 1433, 683071])
        return
    
    # Phân tích thường (cho số nhỏ)
    d = 2
    temp = val
    while d * d <= temp and d < 1000000:
        if temp % d == 0:
            target_set.add(d)
            while temp % d == 0: temp //= d
        d += 1
    if temp > 1:
        target_set.add(temp)

# Bắt đầu xây dựng chuỗi
moduli = [n]

# Bước 1: m_1 = lambda(n)
# lambda(n) = lcm(p-1 for p in factors_n)
# p1-1 factors: 2, 3, 197, 4139, 57349
# p2-1 factors: 2^11, 89, q1, q2, q3, q4
# 127-1 factors: 2, 3^2, 7
# Tập hợp các nguyên tố cấu thành m_1
m1_primes = set([2, 3, 7, 89, 197, 4139, 57349, 
                 1957681487, 4579960207, 616095937974917, 998813938056801811539097])

m_1 = 1
# Tính m_1 dựa trên lũy thừa lớn nhất của từng nguyên tố trong các p_i-1
# Ở đây ta biết chính xác các lũy thừa đặc biệt từ phân tích trước:
# 2^11 (từ p2-1), 3^2 (từ 127-1)
# Các số còn lại là mũ 1
for p in m1_primes:
    if p == 2: m_1 = lcm(m_1, 2**11)
    elif p == 3: m_1 = lcm(m_1, 3**2)
    else: m_1 = lcm(m_1, p)
moduli.append(m_1)

# Bước 2: m_2 = lambda(m_1)
# Cần tính lambda(p^k) cho các p^k || m_1
# lambda(p^k) = p^(k-1)*(p-1)
# lambda(2^11) = 2^10
# lambda(3^2) = 3*2
# lambda(p) = p-1
m2_primes = set()
m_2 = 1

# Xử lý phần lũy thừa
m_2 = lcm(m_2, 2**10) # từ 2^11
m_2 = lcm(m_2, 3*2)   # từ 3^2
# Thêm các thừa số nguyên tố sinh ra từ lũy thừa này vào tập m2_primes (2 và 3 đã có)

# Xử lý phần p-1 cho các nguyên tố khác
for p in m1_primes:
    add_p_minus_1_factors(p, m2_primes)
    # Nếu không phải 2, 3 thì đóng góp là p-1
    if p != 2 and p != 3:
        m_2 = lcm(m_2, p-1)

moduli.append(m_2)

# Bước 3 trở đi: Tổng quát hóa
# Tuy nhiên m_2 đã khá nhỏ (chứa các thừa số từ q_i - 1).
# Ta dùng vòng lặp để automate các bước tiếp theo
curr_primes = m2_primes
curr_mod = m_2

while curr_mod > 1:
    next_primes = set()
    next_mod = 1
    
    # Tính lambda(curr_mod) dựa trên curr_primes
    temp_mod = curr_mod
    
    # Sắp xếp primes để xử lý từ nhỏ đến lớn (optional, cho đẹp)
    sorted_primes = sorted(list(curr_primes))
    
    for p in sorted_primes:
        if temp_mod % p == 0:
            k = 0
            while temp_mod % p == 0:
                k += 1
                temp_mod //= p
            
            # lambda(p^k) = p^(k-1)*(p-1)
            term = (p**(k-1)) * (p-1)
            next_mod = lcm(next_mod, term)
            
            # Cập nhật next_primes: các ước của p-1 và p (nếu k>1)
            add_p_minus_1_factors(p, next_primes)
            if k > 1:
                next_primes.add(p)

    if temp_mod > 1:
        # Trường hợp này không nên xảy ra nếu m1_primes ban đầu đủ
        # Nhưng nếu có, ta coi nó là thừa số nguyên tố mới (hoặc hợp số chưa phân tích)
        # Rủi ro: nếu là hợp số thì lambda sai.
        # Ở đây ta print warning
        print(f"Warning: leftover factor {temp_mod} in chain generation")
        # add_p_minus_1_factors(temp_mod, next_primes) # Giả sử là nguyên tố?
        # next_mod = lcm(next_mod, temp_mod - 1)

    moduli.append(next_mod)
    curr_mod = next_mod
    curr_primes = next_primes
    
    if len(moduli) > 20: break

print(f"Moduli chain: {moduli}")

# 3. Hàm tính tháp lũy thừa
# Tính chính xác giá trị đỉnh tháp (để tránh sai số khi số nhỏ)
def get_exact_val(p_idx):
    if p_idx < 0: return 1
    # Chỉ tính nếu số nhỏ
    if p_idx > 4: return None
    sub = get_exact_val(p_idx - 1)
    if sub is None: return None
    try:
        val = primes[p_idx] ** sub
        if val > 10**18: return None # Giới hạn 64-bit integer
        return val
    except:
        return None

def solve_tower(p_idx, m_idx):
    if p_idx < 0: return 1
    if m_idx >= len(moduli): return 0 # Modulus = 1 -> 0
    
    curr = moduli[m_idx]
    if curr == 1: return 0
    
    # Kiểm tra đỉnh tháp (số nhỏ)
    exact = get_exact_val(p_idx)
    if exact is not None:
        return exact % curr
    
    # Đệ quy
    # Công thức: a^b % m = a^(b % lambda + lambda) % m 
    # (với b >= lambda, đảm bảo tính đúng cho a, m không nguyên tố cùng nhau)
    next_mod = moduli[m_idx+1] if m_idx+1 < len(moduli) else 1
    
    exp = solve_tower(p_idx - 1, m_idx + 1)
    
    # Luôn cộng thêm next_mod để đảm bảo số mũ "đủ lớn" theo định lý Euler mở rộng
    # Trừ khi next_mod = 1 (khi đó exp = 0, nhưng ta cần số mũ > log_a(m))
    # Nhưng ở tầng sâu này, giá trị thực tế của tháp là vô cùng lớn, nên + next_mod là an toàn.
    return pow(primes[p_idx], exp + next_mod, curr)

# Tính Key
print("Computing key...")
# primes[0]=2, [1]=3...
# Bài toán: 97^(89^(...)) -> tính từ index cuối về
target_idx = len(primes) - 1
key_int = solve_tower(target_idx, 0)
print(f"Key Found: {key_int}")

# 4. Decrypt
key_bytes = int.to_bytes(key_int, 32, 'big')
try:
    with open('cipher.txt', 'r') as f:
        cipher_hex = f.read().strip()
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    decrypted = cipher.decrypt(bytes.fromhex(cipher_hex))
    print(f"Flag Decrypted: {decrypted}")
except Exception as e:
    print(f"Error decrypting: {e}")
```

## 4. Kết quả

Sau khi chạy script, ta tính được `int_key % n` một cách nhanh chóng (chưa đến 1 giây).
Dùng key này giải mã file `cipher.txt` (AES) là ra Flag.

- **Flag:** `UTECTF{p0w3r_t0w3r_1s_s3cur1ty_r1ght?}`

Qua bài này, các bạn hãy nhớ: **Trong thế giới Modular Arithmetic, số mũ không cần quá lớn, chỉ cần tính đúng theo chu kỳ $\phi(n)$ là đủ!**
