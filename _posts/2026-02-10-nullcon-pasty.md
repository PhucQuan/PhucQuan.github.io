---
layout: single
title: "[Writeup] NullCon 2025 - Pasty (Crypto/Web)"
date: 2026-02-10
classes: wide
categories: [NullCon 2025, crypto, web]
tags: [nullcon, custom-crypto, signature-forgery, bit-flipping, sha256]
---

Chào bạn, hôm nay mình sẽ chia sẻ writeup cho một thử thách khá thú vị từ giải **NullCon** có tên là **Pasty**. Đây là một bài kết hợp giữa Web và Crypto, yêu cầu chúng ta phải phá vỡ một cơ chế chữ ký tự chế (Custom Cryptographic Signature).

## 1. Tổng quan (Overview)

**Thử thách:** Pasty - Custom Crypto Signature Bypass
**Flag:** `ENO{cr3at1v3_cr7pt0_c0nstruct5_cr4sh_c4rd5}`
**Tác giả:** @gehaxelt

![Challenge Pasty](/assets/images/nullcon/pasty/challenge.png)


![Web Interface](/assets/images/nullcon/pasty/interface.png)

Challenge này cung cấp một dịch vụ **Pastebin** bảo mật (hoặc ít nhất là họ nghĩ vậy). Thay vì dùng các thư viện chuẩn, họ tự viết thuật toán ký (signature) để bảo vệ quyền truy cập vào các paste.

Mục tiêu của chúng ta là chứng minh "homebrewed crypto" (crypto tự chế) không an toàn và truy cập vào paste chứa **Flag**.

## 2. Phân tích thuật toán (Crypto Analysis)

Dưới đây là đoạn code PHP chịu trách nhiệm tạo chữ ký:

```php
function _x($a,$b){
    $r='';
    for($i=0;$i<strlen($a);$i++)
        $r.=chr(ord($a[$i])^ord($b[$i]));
    return $r;
}

function compute_sig($d,$k){
    $h=hash('sha256',$d,1);                    // 1. Hash dữ liệu (32 bytes)
    $m=substr(hash('sha256',$k,1),0,24);       // 2. Tạo mask 24 bytes từ Key
    $o='';
    for($i=0;$i<4;$i++){
        $s=$i<<3;                              // s = i * 8 (0, 8, 16, 24)
        $b=substr($h,$s,8);                    // 3. Lấy 8-byte chunk từ hash
        $p=(ord($h[$s])%3)<<3;                 // 4. Chọn vị trí mask: 0, 8, hoặc 16
        $c=substr($m,$p,8);                    // 5. Lấy 8-byte mask segment
        
        // 6. XOR chunk với mask. Từ chunk 2, XOR thêm với output trước đó.
        $o.=($i?_x(_x($b,$c),substr($o,$s-8,8)):_x($b,$c));
    }
    return $o;
}
```

### Cơ chế hoạt động:

1.  **Hash:** Dữ liệu đầu vào được băm bằng SHA-256 (32 bytes).
2.  **Mask:** Tạo một mask dài 24 bytes từ Key bí mật.
3.  **Chia Chunk:** Hash 32 bytes được chia thành 4 chunks, mỗi chunk 8 bytes.
4.  **Xử lý từng Chunk:**
    *   Với mỗi chunk, thuật toán chọn ngẫu nhiên một đoạn mask dựa trên byte đầu tiên của chunk đó (`ord($h[$s])%3`).
    *   Chunk được XOR với đoạn mask đã chọn.
    *   Nếu không phải chunk đầu tiên, nó còn được XOR thêm với kết quả của chunk liền trước (giống cơ chế CBC mode).

## 3. Lỗ hổng nghiêm trọng (Vulnerabilities)

### 1. Keyspace cực kỳ hạn chế

Mặc dù SHA-256 có không gian 256-bit, nhưng cách chọn mask lại làm giảm độ bảo mật nghiêm trọng.
Mỗi chunk chỉ có thể chọn 1 trong 3 vị trí mask (0, 8, 16).
Với 4 chunks, tổng số trường hợp chữ ký có thể xảy ra cho một key cố định chỉ là:
$$ 3^4 = 81 \text{ signatures} $$

Thay vì $2^{256}$ khả năng, chúng ta chỉ có khoảng 81 khả năng. Điều này tương đương với độ bảo mật chỉ khoảng **6.3 bits**!

### 2. Predictable Mask Selection

Việc chọn mask (`$p`) phụ thuộc hoàn toàn vào byte đầu tiên của chunk hash (`ord($h[$s])`). Vì SHA-256 là hàm xác định (deterministic), nên nếu ta biết dữ liệu đầu vào, ta biết chính xác thuật toán sẽ chọn đoạn mask nào.

### 3. Signature Forgery (Giả mạo chữ ký)

Từ một chữ ký hợp lệ của một dữ liệu bất kỳ, ta có thể:
1.  Tính ngược lại (Reverse Engineer) để tìm ra 3 đoạn mask segments ($M_0, M_1, M_2$).
2.  Sau khi có các mask segments, ta có thể tự tạo chữ ký cho bất kỳ dữ liệu nào khác (ví dụ: chuỗi "flag").

## 4. Chiến thuật khai thác (Exploitation)

### Bước 1: Thu thập thông tin

Tạo một paste bất kỳ trên trang web để lấy mẫu chữ ký.

*   **ID:** `43813b1fbb52cdbe`
*   **Signature:** `03534493a90d3610d921826acded5eeaead27bc8c7125b22ec13c0f93972ab8b`

### Bước 2: Reverse Engineer Mask Segments

Ta viết script Python để giải ngược tìm Mask.

```python
def analyze_signature(paste_id, signature_hex):
    signature = binascii.unhexlify(signature_hex)
    data_hash = hashlib.sha256(paste_id.encode()).digest()
    
    mask_segments = {}
    for i in range(4):
        s = i * 8
        chunk = data_hash[s:s+8]
        sig_chunk = signature[s:s+8]
        mask_pos = (chunk[0] % 3) * 8
        
        if i == 0:
            mask_segment = xor_bytes(chunk, sig_chunk)
        else:
            prev_sig_chunk = signature[s-8:s]
            temp = xor_bytes(sig_chunk, prev_sig_chunk)
            mask_segment = xor_bytes(chunk, temp)
        
        mask_segments[mask_pos] = mask_segment
    
    return mask_segments
```

**Kết quả phân tích:**
*   Chunk 0: `mask_pos=16`, `mask_segment=3899ea82fc144d8a`
*   Chunk 1: `mask_pos=0`, `mask_segment=8d77a517320e2c92`
*   ...

### Bước 3: Forge Signature cho "flag"

Sau khi có đủ các mảnh mask, ta dùng chúng để ký cho chuỗi `flag`.

```python
def forge_signature(data, mask_segments):
    data_hash = hashlib.sha256(data.encode()).digest()
    signature = b''
    
    for i in range(4):
        s = i * 8
        chunk = data_hash[s:s+8]
        mask_pos = (chunk[0] % 3) * 8
        mask_segment = mask_segments[mask_pos]
        
        if i == 0:
            sig_chunk = xor_bytes(chunk, mask_segment)
        else:
            prev_sig_chunk = signature[s-8:s]
            temp = xor_bytes(chunk, mask_segment)
            sig_chunk = xor_bytes(temp, prev_sig_chunk)
        
        signature += sig_chunk
    
    return signature.hex()
```

**Forged signature:** `b8e4e53e526806aa641e0dac06294218f67a1e18ea7c2d573d40a266a7703710`

### Bước 4: Lấy Flag

Truy cập URL với chữ ký giả mạo:
`http://52.59.124.14:5005/view.php?id=flag&sig=b8e4...`

**Kết quả:** `ENO{cr3at1v3_cr7pt0_c0nstruct5_cr4sh_c4rd5}`

## 5. Tổng kết và Bài học

*   **Đừng bao giờ tự implement crypto:** Luôn sử dụng các thư viện chuẩn đã được kiểm chứng (như OpenSSL, Sodium).
*   **Entropy thực tế $\neq$ Entropy lý thuyết:** Key dài 24 bytes không có nghĩa là bạn có 24 bytes entropy nếu thuật toán sử dụng nó kém.
*   **Nguy hiểm của Deterministic Selection:** Việc chọn tham số mã hóa dựa trên input data làm cho hệ thống dễ bị đoán trước.

Hy vọng bài writeup này giúp bạn hiểu thêm về tầm quan trọng của việc sử dụng Crypto đúng cách!
