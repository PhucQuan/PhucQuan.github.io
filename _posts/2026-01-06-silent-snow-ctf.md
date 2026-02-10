---
layout: single
title: "[Writeup] Silent Snow CTF 2025 - WordPress Privilege Escalation"
author_profile: false
classes: wide
categories: [Hack The Box, web]
tags: [wordpress, authentication, bypass, privilege-escalation]
date: 2026-01-06
permalink: /writeups/silent-snow-ctf/
---

## Challenge Info

**Event:** University CTF 2025: Tinsel Trouble  
**Challenge Name:** Silent Snow CTF  
**Category:** Web Exploitation (WordPress)  
**Difficulty:** Medium  

**Objective:** Bypass registration restrictions and escalate privileges to Administrator to retrieve the flag.

**Challenge Description:**

{: .notice--info}
**Original Description:**  
> The Snow-Post Owl Society is responsible for delivering all important news, including this week's festival updates and RSVP confirmations, precisely at midnight. However, a malicious code of the Tinker's growing influence—has corrupted the automation on the official website. As a result, no one is receiving the crucial midnight delivery, which means the village doesn't have the final instructions for the Festival, including the required attire, times, dates, and locations. This is a direct consequence of the Tinker’s logic of restrictive festive code, ensuring that the joyful details are locked away.  
>  
> **Mission:** Hack the official Snow-Post Owl Society website and find a way to bypass the corrupted code to trigger a mass resent of the latest article, ensuring the Festival details reach every resident before the lights dim forever.

**Tóm tắt nội dung:**
Hệ thống chuyển phát tin tức của Hiệp hội Cú Snow-Post đã bị Tinker can thiệp bằng mã độc, làm tê liệt quá trình thông báo các chỉ dẫn quan trọng cho Lễ hội. Dân làng đang đứng trước nguy cơ mất đi những thông tin cuối cùng về nghi lễ. Nhiệm vụ của chúng ta là xâm nhập vào website, bẻ khóa các đoạn mã hạn chế của Tinker để kích hoạt hệ thống gửi lại thông báo cho toàn bộ cư dân.

<!-- more -->

![Challenge Interface](/assets/images/htb/0.png)

---

## Initial Reconnaissance

### 1. Vấn đề đầu tiên: "Cánh cửa đóng kín"

Bước vào thử thách, điểm đến đầu tiên thường là trang đăng ký (`/wp-login.php?action=register`) với hy vọng tạo được tài khoản để thâm nhập sâu hơn. Tuy nhiên, hệ thống trả về thông báo: `registration=disabled`

![anh dang nhap](/assets/images/htb/1.png)



**Bài toán cốt lõi:** Làm sao để bật tính năng đăng ký này lên khi chúng ta chưa có quyền Admin?

### 2. Truy tìm manh mối (Source Code Analysis)

Để giải quyết vấn đề, ta cần phân tích bộ mã nguồn được cung cấp.

#### 2.1. Xác định môi trường (Dockerfile)
Mở file `Dockerfile`, dòng đầu tiên xác nhận đây là một trang WordPress chuẩn:
```dockerfile
FROM wordpress:latest
```
**=> Suy luận:** Cấu trúc thư mục và các đường dẫn mặc định sẽ tuân theo chuẩn WordPress. Trang đăng nhập/đăng ký chắc chắn nằm ở `/wp-login.php`.

#### 2.2. Tìm "Cánh cửa bí mật" (my-plugin.php)
Kiểm tra thư mục `wp-content/plugins/my-plugin/` và mở file `my-plugin.php`, ta thấy đoạn code khởi tạo:

```php
// Hook này có nghĩa là: Mỗi khi WordPress tải xong, hãy chạy hàm 'init'
add_action('wp_loaded', array($this, 'init'));

public function init() {
    // DÒNG QUAN TRỌNG NHẤT:
    if (isset($_GET['settings'])) { 
        $this->admin_page();
        exit;
    }
}
```
**=> Suy luận:** Hàm `init` kiểm tra tham số `settings` trên URL. Nếu `?settings` tồn tại, nó sẽ chạy hàm `admin_page()`.

---

## Enumeration & Analysis

### 2.3. Tại sao phải có "/wp-admin"? (Bypass Check)

Trong hàm `admin_page()`, ta thấy một lớp bảo vệ:

```php
public function admin_page() {
    // Nếu không phải admin thì chặn
    if (!is_admin()) { 
        wp_die('Access denied');
    }
    // ...
}
```

**Phân tích cơ chế:**
*   Hàm `is_admin()` trong WordPress thực chất kiểm tra xem URL hiện tại có bắt đầu bằng `/wp-admin/` hay không.
*   **Giải pháp:** Để "đánh lừa" hàm này trả về `true`, ta bắt buộc phải chèn `/wp-admin/` vào đường dẫn.

**Kết quả:**
*   `http://website.com/?settings=1` -> `is_admin()` là `false` -> **Bị chặn**.
*   `http://website.com/wp-admin/?settings=1` -> `is_admin()` là `true` -> **Vượt qua thành công!**

Khi truy cập vào đường dẫn này, chúng ta sẽ thấy giao diện quản lý của Plugin:

![Plugin Settings Page](/assets/images/htb/settings_page.png)

Giao diện này cho phép ta thay đổi giữa **Light Mode** và **Dark Mode**. Thông báo "Mode saved" xuất hiện khi ta nhấn Save Changes. Tuy nhiên, đằng sau nút bấm đơn giản này là một lỗ hổng cực lớn liên quan đến cách Plugin xử lý dữ liệu.

### 2.4. Lỗ hổng Arbitrary Option Update

Quay lại soi kỹ file `my-plugin.php` ở đoạn xử lý dữ liệu khi người dùng nhấn "Save Changes":

```php
if (isset($_POST['my_plugin_action'])) {
    check_admin_referer("my_plugin_nonce", "my_plugin_nonce"); // Check Nonce bảo mật
    
    // NGUY HIỂM CHẾT NGƯỜI:
    // Plugin lấy trực tiếp giá trị từ 'my_plugin_action' làm tên Option để cập nhật
    update_option($_POST['my_plugin_action'], $_POST['mode']); 
}
```

**Phân tích kỹ thuật:**
*   Thông thường, lập trình viên sẽ cố định tên Option cần sửa (ví dụ: `update_option('my_theme_mode', ...)`).
*   Nhưng ở đây, Plugin lại dùng biến `$_POST['my_plugin_action']`. Mà tất cả các biến trong `$_POST` đều là những thứ người dùng (attacker) có thể thay đổi hoàn toàn bằng các công cụ như Burp Suite hoặc cURL.
*   **Hệ quả:** Chúng ta có thể thay đổi **BẤT KỲ** cấu hình nào trong database của WordPress (bảng `wp_options`), không chỉ giới hạn ở việc đổi giao diện sáng/tối.

---

## Exploitation

### 3. Kế hoạch tác chiến chuyên sâu

Để tận dụng lỗ hổng này, chúng ta cần thực hiện hai bước thay đổi cấu hình quan trọng để mở toang cánh cửa vào hệ thống.

### Attack Strategy

1.  **Mục tiêu 1:** Bật đăng ký bằng cách sửa option `users_can_register = 1`.
2.  **Mục tiêu 2:** Leo thang đặc quyền bằng cách set `default_role = administrator`.
3.  **Vượt qua bảo vệ (Lấy Nonce):** 
    Để gửi request thành công, ta cần mã `my_plugin_nonce`. Bằng cách xem mã nguồn trang (View Source), ta có thể dễ dàng tìm thấy nó nằm trong một trường ẩn (hidden input).

![WP Nonce Source](/assets/images/htb/wp_nonce.png)

**Điểm mấu chốt:** 
Trong mã nguồn, nút "Save Changes" có thuộc tính `name="my_plugin_action"` và `value="my_plugin_dark_mode"`. 
```html
<button type="submit" name="my_plugin_action" value="my_plugin_dark_mode" ...>Save Changes</button>
```
Khi người dùng nhấn nút, trình duyệt sẽ gửi `my_plugin_action=my_plugin_dark_mode`. Tuy nhiên, vì chúng ta có thể can thiệp vào request, chúng ta có thể đổi giá trị này thành bất kỳ option nào trong WordPress (như `users_can_register`) để thao túng hệ thống.

Sử dụng cURL để gửi request thay đổi cấu hình trực tiếp từ terminal:

![cURL Commands Execution](/assets/images/htb/curl_commands.png)

Phân tích lệnh cURL thực tế:
*   `-i -s -k`: Các tham số để hiển thị headers, chạy chế độ im lặng và bỏ qua kiểm tra SSL.
*   `my_plugin_action=users_can_register`: Mục tiêu ghi đè option để cho phép đăng ký.
*   `mode=1`: Giá trị kích hoạt.
*   `my_plugin_nonce=1428f615ad`: Mã bảo mật thực tế lấy được từ hệ thống.

**Kết quả:**
Quay lại trang `/wp-login.php?action=register`, form đăng ký đã hiện ra. Tài khoản mới tạo sẽ mặc định có quyền **Administrator**.
![dashboard](/assets/images/htb/4.5.png)

![admin](/assets/images/htb/4.png)
---

## Post-Exploitation

### 5. Lấy cờ (The Finale)

Khi đã có quyền Admin, chúng ta sử dụng tính năng **Theme Editor** để can thiệp vào mã nguồn giao diện:

1.  Truy cập Theme Editor.
2.  Chọn file `footer.php`.
3.  Chèn lệnh thực thi hệ thống: `<?php system('cat /flag.txt'); ?>`.
4.  Tải lại trang chủ và nhận Flag.
![cURL Commands Execution](/assets/images/htb/cat.png)

![cURL Commands Execution](/assets/images/htb/flag.png)

---

## Key Lessons Learned

### Technical Insights
1.  **Đừng tin tưởng tuyệt đối vào `is_admin()`:** Hàm này chỉ kiểm tra ngữ cảnh URL, không kiểm tra quyền hạn thực sự của người dùng.
2.  **Nguy cơ từ `update_option()`:** Việc cho phép người dùng kiểm soát tham số đầu tiên của hàm `update_option` dẫn đến lỗ hổng ghi đè cấu hình hệ thống nghiêm trọng.
3.  **Kiểm tra Plugin Tùy chỉnh:** Trong các bài WordPress CTF, mã nguồn của các plugin hoặc theme tự viết luôn là nơi chứa đựng các "backdoor" hoặc sai lầm logic của người ra đề.

### Security Takeaways
*   Luôn sử dụng `current_user_can()` để kiểm tra quyền hạn thay vì `is_admin()`.
*   Whitelisting các option được phép thay đổi thay vì cho phép nhận input trực tiếp vào tên option.

---

## Solution Summary

| Step | Action | Result |
1 | Truy cập `/wp-admin/?settings=1` | Vượt qua check `is_admin()` |
2 | Lấy nonce và gửi POST request | Đè cấu hình `users_can_register` và `default_role` |
3 | Đăng ký tài khoản mới | Có quyền Administrator |
4 | Sửa `footer.php` trong Theme Editor | Thực thi lệnh đọc `/flag.txt` để lấy Flag |

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Browser DevTools | Phân tích mã nguồn và lấy Nonce |
| cURL / Burp Suite | Gửi Request can thiệp cấu hình |
| WordPress Dashboard | Thực hiện các thao tác hậu khai thác |

---
*Writeup by PhucQuan*
