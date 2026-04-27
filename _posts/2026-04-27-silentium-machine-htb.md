---
layout: single
title: "Silentium Machine - HTB"
date: 2026-04-27
categories: [writeups, "machine HTB"]
image: /assets/images/silentium-machine-htb/image.png
---
# Silentium Machine - HTB

![image.png](/assets/images/silentium-machine-htb/image.png)

### I. Recon

Như mọi machine như bình thường thì trước khi expxloit , mình đã recon bằng nmap và tìm được 2 port là 80 và 22 ,theo như suy đoán của mình lúc ban đầu thì sẽ là tìm thông tin đăng nhập ở trang web và sẽ ssh bằng tài khoản đó. Nhớ là trước tiên các bạn phải bỏ ip cùng với domain của lab vào /etc/hosts nhé.

![image.png](/assets/images/silentium-machine-htb/image%201.png)

![image.png](/assets/images/silentium-machine-htb/image%202.png)

![image.png](/assets/images/silentium-machine-htb/image%203.png)

Khi vào trang web thì thấy trang web này là 1 trang SPA , các nội dung tĩnh và dường như mình cũng không thao tác được các chức năng gì . Và sau đó mình cũng có sử dụng Gobuster hay ffuf để tìm các endpoint cũng như các đường dẫn ẩn để xem có attack surfaces gì đặc biệt không , ngoài assets cùng các file css ra như mình cũng ko thấy gì đặc biệt cả 

Sau đó mình mới dò thử các subdomain bằng gobuster vhost thì tìm ra 1 trang subdomain Staging.

![image.png](/assets/images/silentium-machine-htb/image%204.png)

Khi vào trang thì mình thấy hiện ra là 1 trang đăng nhập , thường thi các bài lab như này yêu cầu mình sẽ phải Bypass Authenication . Khi làm tới đoạn này thì cũng mất kha khá thời gian của mình khi mình ko có tài khoản để có thể test bởi vì nó ko có chức năng đăng kí , nhưng khi xem lại trang trước silentium.htb thì ở phía cuối có ba tên đáng nghi 

![image.png](/assets/images/silentium-machine-htb/image%205.png)

![image.png](/assets/images/silentium-machine-htb/image%206.png)

Và mình quyết định là test bằng 3 cái tên đó cùng với đuôi là @silentium.htb

Sau một hồi test bằng BurpSuite thì tui cũng thấy được trong phần forgot password thì khi sử dụng chúc năng quên mật khẩu và nhập email là ben@silentium.htb  , thì mình thấy một cái tempToken cùng với role là “admin” do lỗ hổng trả về  dữ liệu trả về ko an toàn . Và mình quyết định lấy token đó reset lại mật khẩu

![image.png](/assets/images/silentium-machine-htb/image%207.png)

![image.png](/assets/images/silentium-machine-htb/image%208.png)

![image.png](/assets/images/silentium-machine-htb/image%209.png)

Cuối cùng thì mình đã reset được mật khẩu và đăng nhập thành công.

Khi vào trang thì mình thấy đây là 1 trang về Flowise . Mình quyết định research trang này trên GG thì biết  Flowise **là công cụ mã nguồn mở, cho phép xây dựng các ứng dụng và tác nhân (agent) AI dựa trên [Large Language Models](https://www.google.com/search?q=Large+Language+Models&oq=Flowise+l%C3%A0+g%C3%AC&gs_lcrp=EgZjaHJvbWUqDggAEEUYJxg7GIAEGIoFMg4IABBFGCcYOxiABBiKBTIKCAEQABiABBiiBDIHCAIQABjvBTIHCAMQABjvBTIHCAQQABjvBdIBCDM0NDhqMGo0qAIDsAIB8QV473y8jcbzTw&sourceid=chrome&ie=UTF-8&mstk=AUtExfCO5Z1VipYhgmzndqn-15qpjHWkbQEhZYhKFqT4HNDp6n5ZL__jfedstkgrIeJNqx6AK8iq8bc2alJ7r5KpQhUgUnLwGCcB1MRHA8NvrPae_F_AsfdusqLiu61WyPs2fqfMvE1hoMZgmQHvJ7t_Zsw5HUEngMtW-IUYAgWBiivNErSOCyiwvrc8gDARXcjaRTUAJ4XrCLORbSmHFlgXuOhRbfn90SqREQT_IWUsxD8-GatdMa4Bff8DuVsIy5pQRUerYuDpxYMy6dC5NU3Qfh1W&csui=3&ved=2ahUKEwiu963l8ouUAxXDklYBHVnqJ3YQgK4QegQIARAC) (LLM) thông qua giao diện kéo-thả trực quan, không cần lập trình nhiều (low-code)**. Nó giúp đơn giản hóa việc tạo quy trình làm việc (workflow) tùy chỉnh bằng cách kết nối các thành phần LangChain

Và đồng thời vì đây là 1 trang khá lớn nên mình cũng dự đoán được và tra CVE của nó trên mạng thì đúng là nó bị dính khá là nhìu CVE . Thì sau khi tìm hiểu thì mình tìm thấy được 1 CVE critical gần đây điểm gần như là tối đa là 

- **CVE-2025-59528 (CVSS 10.0 )**: Lỗ hổng cực kỳ nghiêm trọng trong node `CustomMCP`. Do thiếu kiểm tra đầu vào, kẻ tấn công có thể tiêm mã JavaScript độc hại qua tham số `mcpServerConfig`, dẫn đến việc kiểm soát hoàn toàn hệ thống ( Tức là RCE)
- Lỗ hổng bảo mật tại nút CustomMCP thực chất là một lỗi thực thi mã từ xa (RCE) nghiêm trọng, phát sinh từ việc tin tưởng tuyệt đối vào dữ liệu người dùng. Thay vì sử dụng các phương thức an toàn để xử lý JSON, hàm `convertToValidJSONString` lại đưa trực tiếp chuỗi cấu hình vào hàm khởi tạo `Function()` để thực thi như mã JavaScript thuần túy. Do dữ liệu đi từ API đến thẳng bộ thực thi của Node.js mà không qua bất kỳ bộ lọc hay xác thực nào, kẻ tấn công có thể dễ dàng chèn mã độc để thao túng các module hệ thống như `child_process` hay `fs`. Kết quả là máy chủ bị chiếm quyền điều khiển hoàn toàn, cho phép thực thi lệnh hệ điều hành và đánh cắp dữ liệu nhạy cảm một cách dễ dàng.

[https://github.com/advisories/GHSA-3gcm-f6qx-ff7p](https://github.com/advisories/GHSA-3gcm-f6qx-ff7p)

Và cũng có POC cho lỗ hổng này và mình quyết định tấn công RCE thử , thì trước khi RCE thì trong POC có cần 1 cái gọi là API key ở  phần Authorization

```jsx
curl -X POST http://localhost:3000/api/v1/node-load-method/customMCP \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tmY1fIjgqZ6-nWUuZ9G7VzDtlsOiSZlDZjFSxZrDd0Q" \
  -d '{
    "loadMethod": "listActions",
    "inputs": {
      "mcpServerConfig": "({x:(function(){const cp = process.mainModule.require(\"child_process\");cp.execSync(\"echo !!RCE-OK!! >/tmp/RCE.txt\");return 1;})()})"
    }
  }'
```

 Và đoạn này cũng làm mình mất khá nhìu thời gian để RCE vì mình tưởng Bearer đó là cái JWT , nên mình ko thể reverse shell được hehee =)).

![image.png](/assets/images/silentium-machine-htb/image%2010.png)

Sau đó mình dựng 1 cổng lắng nghe ở máy của mình

![image.png](/assets/images/silentium-machine-htb/image%2011.png)

Và gửi lệnh Curl trong POC cùng với phần require là reverse shell tới máy của mình 

![image.png](/assets/images/silentium-machine-htb/image%2012.png)

Và mình đã giành được quyền kiểm soát hệ thống

Sau các lệnh liệt kê cơ bản thì mình thấy mình đang ở quyền root nhưng lại ở trong 1 container. Thì việc đầu tiên sẽ là escape ra khỏi container này. Thì sau khi đọc được env hay cat **`proc/1/environ`   như trong ảnh thì thấy được các password đáng ngờ**

![image.png](/assets/images/silentium-machine-htb/image%2013.png)

Sau khi tìm được cả 2 mật khẩu đáng ngờ thì mình SSH vào tài khoản ben cùng với mk tìm được ,tìm được cả 2 mật khẩu thì tui thử cả hai (1 trong 2 sẽ vào được ), thì đã vào được tài khoản Ben và phần tiếp theo chỉ còn là leo thang đặc quyền 

![image.png](/assets/images/silentium-machine-htb/17a88a28-7e4d-4ed0-b215-a8571d0a7e8b.png)

Flag của user 

![image.png](/assets/images/silentium-machine-htb/image%2014.png)

Sau khi kiểm tra 1 vài lệnh leo thang đặc quyền cơ bản thì mình vẫn chưa tìm ra được hướng giải gì .Nên mình quyết định research tham khảo các hướng giải của các pháp sư trung hoa =))).

![image.png](/assets/images/silentium-machine-htb/image%2015.png)

Sau khi mình tham khảo thì họ sẽ liệt kê thử các cổng đang lắng nghe và thấy được tên port là 3001 

Tiếp theo mình sẽ lôi port đó ra ngoài bằng lệnh
Lệnh này **dùng để SSH Tunneling (Local Port Forwarding)**. Nó giúp bạn truy cập một dịch vụ đang chạy bên trong máy chủ từ xa như thể nó đang chạy ngay trên máy tính của bạn.
Nhiều khả năng máy chủ (`10.129.197.47`) đang chạy một ứng dụng web  ở cổng **3001** nhưng chỉ cho phép truy cập nội bộ (**localhost**). Bằng cách dùng lệnh này, bạn có thể mở trình duyệt trên máy mình, gõ `localhost:3001` để truy cập trực tiếp vào ứng dụng đang chạy "ẩn" bên trong máy chủ đó

```jsx
ssh -L 3001:127.0.0.1:3001 ben@10.129.197.47 
```

Hãy đăng kí và vào trang chính xem sao 

![image.png](/assets/images/silentium-machine-htb/image%2016.png)

![image.png](/assets/images/silentium-machine-htb/image%2017.png)

bởi vì lúc tra source thì tui có 2 commit hash ?v =….

thì tui lên github của gogs thì thấy commit thì tui biết đây là It’s **Gogs 0.13.0**, a self-hosted Git platform

![image.png](/assets/images/silentium-machine-htb/image%2018.png)

Cũng tương tự như trên mình cũng research về CVE trên phiên bản này trở về trước thì ở năm 2025 gần đây 

 **Lỗ hổng 0-day mới nhất (2025)**

**CVE-2025-8110** là một lỗ hổng bảo mật nghiêm trọng (Remote Code Execution - RCE) trong **Gogs**, một dịch vụ quản lý mã nguồn Git tự lưu trữ. Lỗ hổng này cho phép kẻ tấn công đã xác thực thực thi mã từ xa thông qua việc xử lý sai các liên kết tượng trưng (symbolic links) trong API

**1. Thông tin** 

- **Tên lỗ hổng:** Gogs Symlink Path Traversal dẫn đến Remote Code Execution (RCE).
- **Mã định danh:** **CVE-2025-8110**.
- **Điểm CVSS:** **8.7 - 8.8 (High)**.
- **Đối tượng bị ảnh hưởng:** Tất cả các phiên bản Gogs **≤ 0.13.3**.
- **Trạng thái:** Đã có bản vá trong phiên bản **0.13.4** (phát hành tháng 1/2026), nhưng nhiều hệ thống vẫn chưa cập nhật.

**2. Cơ chế kỹ thuật**

Lỗ hổng này là một màn **Bypass** kinh điển của [**CVE-2024-55947**](https://github.com/advisories/GHSA-mq8m-42gh-wq7r):

- **Vấn đề cũ (CVE-2024-55947):** Gogs cho phép ghi đè tệp ngoài thư mục repository bằng cách sử dụng ký tự `../` (Path Traversal). Nhà phát triển đã vá bằng cách chặn chuỗi `../`.
- **Lỗ hổng mới (CVE-2025-8110):** Kẻ tấn công không dùng `../` nữa mà lợi dụng tính năng **Symbolic Link (Symlink)** của Git.
    - **Bước 1:** Kẻ tấn công (đã xác thực, quyền thấp) tạo một Symlink trong repository trỏ đến một tệp nhạy cảm bên ngoài (ví dụ: `.git/config` hoặc các tệp cấu hình hệ thống).
    - **Bước 2:** Sử dụng API `PutContents` để cập nhật nội dung cho Symlink đó.
    - **Bước 3:** Hệ thống Gogs không kiểm tra xem đích đến của Symlink có nằm ngoài phạm vi an toàn hay không. Nó ghi đè tệp mục tiêu theo liên kết đó.
    - **Kết quả:** Kẻ tấn công có thể ghi đè cấu hình để thực thi lệnh hệ thống (RCE).

![image.png](/assets/images/silentium-machine-htb/image%2019.png)

Để giải được bài này thì tui có kiếm được PoC của CVE này https://github.com/zAbuQasem/gogs-CVE-2025-8110

Đọc File exploit và chỉnh lại tên user và password đồng thời command dòng register để ko phải đăng kí vì có đăng kí rồi

![image.png](/assets/images/silentium-machine-htb/image%2020.png)

![image.png](/assets/images/silentium-machine-htb/image%2021.png)

Vậy là mình đã dành được reverse shell rồi , với quyền truy cập root thì t có thể đọc được cờ và Machine này kết thúc tại đây . Tổng quan về Machine này thì là sự kết hợp của 2 CVE khá là hay nhưng mà CVE sau thì mình phải tham khảo các wu thì mới hoàn thành được . Cảm ơn các bạn đã dành thời gian đọc nhé . Hẹn các bạn ở các bài sau ^_^

