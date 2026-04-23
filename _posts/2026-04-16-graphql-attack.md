---
layout: single
title: "Phân tích lỗ hổng về GraphQL"
date: 2026-04-16
categories: [Penetration-Testing]
tags: [graphql, api, idor, introspection, brute-force, portswigger, owasp]
---

## I. Lời mở đầu

Nếu bạn từng làm việc tới API trong một thời gian , thì gần như chắc chắn bạn đã tiếp xúc với REST API , thứ gần như là “default choice” của các backend system hiện nay bởi vì tính tiện lợi của nó.

Trước đó nữa , trong các hệ thống enterphise cũ hơn , bạn cũng có thể sẽ gặp SOAP - verbose , chặt chẽ nhưng khá nặng nề . Gần đây hơn , các hệ thống microservices lại gRPC hơn vì tính hiệu năng của nó và binary protocol.

Nhưng có 1 vấn đề chung là user ngày càng có nhu cầu và linh hoạt hơn trong việc lấy dữ liệu 

Và đó là lúc GraphQL xuất hiện , ban đầu GraphQL được xem như là một “REST killer” nhưng thực tế thì nó ko thay thế hoàn toàn REST , mà nó mở ra 1 cách tiếp cận API hoàn toàn mới 

> Client chủ động lấy dữ liệu khi họ cần , thay vì server quyết định
> 

Điều này nghe có vể là tốt nhưng dưới góc nhìn của security , thì nó cũng mở ra 1 loạt vấn đề thú vị 

## II. GraphQL là gì?

![image.png](/assets/images/graphql/image.png)

GraphQL thực chất là 1 ngôn ngữ truy vấn API cho phép User kiểm soát chính sát dữ liệu được trả về từ server

Không giống như REST API , mỗi endpoint sẽ đại diện cho 1 resource cụ thể , GraphQL sử dụng 1 endpoint duy nhất để xử lí tất cả các request , Hành vi của request sẽ được xác định bởi nội dung của query thay vì URL hoặc HTTP method.

GraphQL cho phép client :

- Chỉ định chính xác các field cần thiết
- Truy vấn nhiều resource trong 1 request duy nhất
- Nhận repspone có cấu trúc đúng với query đã gửi

Điều này giúp làm giảm số lượng request tới máy chủ và tránh các vấn đề như over-fetching và under-fetching thường gặp trong REST.

## III. GraphQL hoạt động như thế nào ?

GraphQL hoạt động dựa trên một schema , đóng vai trò là hợp đồng giữa client và server

Một Schema sẽ định nghĩa :

- Các object type ( kiểu dữ liệu)
- Các field có thể truy vấn
- Mối quan hệ giữa các Object
- Các operation có sẵn hay còn gọi là các thao tác có ẵn

GraphQL hỗ trợ 3 loại operation chính :

**a. Queries**

Queries được sử dụng để lấy dữ liệu từ kho dữ liệu server , tương đương với GET trong REST

Các truy vấn thường có các thành phần chính sau:

- Loại `query opetation`. Về mặt kỹ thuật, đây là tùy chọn nhưng được khuyến khích, vì nó cho máy chủ biết rõ ràng rằng yêu cầu đến là một truy vấn.
- Tên truy vấn. Bạn có thể đặt bất kỳ tên nào tùy ý. Tên truy vấn là tùy chọn, nhưng được khuyến khích vì nó có thể giúp ích cho việc debug sau này.
- Data structure :  Đây là dữ liệu mà truy vấn nên trả về.
- Optionally, có thể có một hoặc nhiều đối số. Chúng được sử dụng để tạo các truy vấn trả về thông tin chi tiết của một đối tượng cụ thể (ví dụ: "cho tôi tên và mô tả của sản phẩm có ID 123").

```jsx
query {
  getProduct(id: 123) {
    name
    description
  }
}
```

Response sẽ có cấu trúc giống với query

```jsx
{
  "data": {
    "getProduct": {
      "name": "Example",
      "description": "Example description"
    }
  }
}
```

**b. Mutations**

Mutations được sử dụng để thay đổi kiểu dữ liệu theo 1 cách nào đó  ( thêm, cập nhật , xóa) chúng tương đương với POST , PUT , DELETE của API REST

```jsx

    #Example mutation request

    mutation {
        createProduct(name: "Flamin' Cocktail Glasses", listed: "yes") {
            id
            name
            listed
        }
    }

    #Example mutation response

    {
        "data": {
            "createProduct": {
                "id": 123,
                "name": "Flamin' Cocktail Glasses",
                "listed": "yes"
            }
        }
    }
```

Giống như các truy vấn, các thao tác thay đổi dữ liệu (mutations) cũng có operation type, name và structure cho dữ liệu trả về. Tuy nhiên, các thao tác thay đổi dữ liệu luôn nhận một đầu vào thuộc một kiểu dữ liệu nào đó. Đầu vào này có thể là một giá trị nội tuyến, nhưng trên thực tế thường được cung cấp dưới dạng một biến.

Mutations thường yêu cầu input và có thể gây side effects tới server . Cho các bạn ko biết side effect là gì thì Side effect (tác dụng phụ) tới server trong lập trình là **các hành động tương tác làm thay đổi trạng thái, dữ liệu hoặc hệ thống bên ngoài phạm vi hàm đang chạy**, phổ biến nhất là gửi yêu cầu (request) đến API máy chủ (Backend), ghi nhật ký (logging), hoặc lưu trữ/cập nhật dữ liệu. Đây là các thao tác bất đồng bộ (async) không thuần khiết, khác với việc chỉ nhận và trả về giá trị

**c. Subscriptions**

Subscriptions cho phép client cho phép thiết lập kết nối lâu dài tới server để nhận dữ liệu theo thời gian thực , thường thiệt lập qua WebSocket.

## **Components of queries and mutations**

### **Fields**

Tất cả các kiểu dữ liệu GraphQL đều chứa các mục dữ liệu có thể truy vấn được gọi là trường (fields). Khi bạn gửi một truy vấn hoặc thao tác sửa đổi (mutation), bạn chỉ định trường nào bạn muốn API trả về. Phản hồi sẽ phản ánh nội dung được chỉ định trong yêu cầu.

Ví dụ dưới đây minh họa một truy vấn để lấy thông tin ID và tên của tất cả nhân viên, cùng với kết quả trả về tương ứng. Trong trường hợp này, `id`, `name.firstname`, và `name.lastname`là các trường được yêu cầu.

```

    #Request

    query myGetEmployeeQuery {
        getEmployees {
            id
            name {
                firstname
                lastname
            }
        }
    }
```

```

    #Response

    {
        "data": {
            "getEmployees": [
                {
                    "id": 1,
                    "name" {
                        "firstname": "Carlos",
                        "lastname": "Montoya"
                    }
                },
                {
                    "id": 2,
                    "name" {
                        "firstname": "Peter",
                        "lastname": "Wiener"
                    }
                }
            ]
        }
    }
```

**Arguments**

Các agruments là các đối số được chỉ định cho các trường cụ thể , 

Khi bạn gửi một truy vấn hoặc thao tác thay đổi dữ liệu có chứa các tham số, máy chủ GraphQL sẽ xác định cách phản hồi dựa trên cấu hình của nó. Ví dụ, nó có thể trả về một đối tượng cụ thể thay vì thông tin chi tiết của tất cả các đối tượng.

Ví dụ dưới đây minh họa một `getEmployee`yêu cầu nhận mã số nhân viên làm tham số. Trong trường hợp này, máy chủ chỉ phản hồi thông tin chi tiết của nhân viên có mã số đó.

```

    #Example query with arguments

    query myGetEmployeeQuery {
        getEmployees(id:1) {
            name {
                firstname
                lastname
            }
        }
    }
```

```

    #Response to query

    {
        "data": {
            "getEmployees": [
            {
                "name" {
                    "firstname": Carlos,
                    "lastname": Montoya
                    }
                }
            ]
        }
    }
    
```

> 
> 
> 
> Nếu các đối số do người dùng cung cấp được sử dụng để truy cập trực tiếp vào các đối tượng, thì API GraphQL có thể dễ bị tổn thương bởi các lỗ hổng IDOR.
> 

**Variables**

Variables cho phép truyền tham số động vào query thay vì hardcode trực tiếp trong request.

Cấu trúc gồm 3 phần:

- Khai báo biến và kiểu dữ liệu
- Sử dụng biến trong query
- Truyền giá trị qua JSON

Ví dụ:

```
query getEmployee($id: ID!) {
  getEmployees(id: $id) {
    name {
      firstname
      lastname
    }
  }
}
```

```
{
  "id":1
}
```

Dấu `!` nghĩa là biến bắt buộc.

Sử dụng variables giúp tái sử dụng query và tách logic khỏi dữ liệu đầu vào.

**Aliases**

GraphQL không cho phép trùng field trong cùng một query. Aliases giải quyết vấn đề này bằng cách đặt tên khác cho từng kết quả.

Ví dụ:

```
query {
  product1: getProduct(id: "1") {
    id
    name
  }
  product2: getProduct(id: "2") {
    id
    name
  }
}
```

Aliases cho phép lấy nhiều object cùng loại trong một request.

Ngoài ra, chúng có thể bị lạm dụng để gửi nhiều request logic trong một HTTP request (ví dụ: bypass rate limit).

**Fragments**

Fragments là các block field có thể tái sử dụng trong nhiều query.

Ví dụ:

```
fragment productInfo on Product {
  id
  name
  listed
}
```

Sử dụng:

```
query {
  getProduct(id: 1) {
    ...productInfo
    stock
  }
}
```

Fragments giúp giảm lặp code và dễ maintain khi schema thay đổi.

## Subscriptions

Như đã nhắc ở trên thì Subscriptions là một loại operation cho phép client duy trì kết nối lâu dài với server để nhận dữ liệu theo thời gian thực.

Thay vì client phải liên tục gửi request (polling), server sẽ chủ động push dữ liệu khi có thay đổi.

Subscriptions thường được dùng cho:

- Chat
- Realtime notifications
- Collaborative applications

Khác với queries và mutations, subscriptions thường được triển khai qua WebSocket thay vì HTTP.

Client vẫn định nghĩa cấu trúc dữ liệu cần nhận, tương tự như các operation khác.

---

## Introspection

Introspection là tính năng cho phép client truy vấn thông tin về schema của GraphQL.

Thông qua introspection, client có thể:

- Liệt kê toàn bộ type
- Xem các field và arguments
- Xác định các query và mutation có sẵn

Tính năng này thường được sử dụng bởi:

- GraphQL IDEs
- Tools sinh tài liệu API

Tuy nhiên, introspection cũng làm lộ toàn bộ cấu trúc API.

## III . Lỗ hổng GraphQL API

Nãy giờ nói lí thuyết cũng khá nhiều chắc các bạn cũng đã nắm rõ sơ bộ về cấu trúc của GraphQL rồi thì trong phần này chúng ta sẽ đi tới phần tấn công GraphQL cũng như thực hành vài bài về nó nhé.

![image.png](/assets/images/graphql/image-1.png)

Hình ảnh minh họa ( [https://portswigger.net/web-security/graphql#finding-graphql-endpoints](https://portswigger.net/web-security/graphql#finding-graphql-endpoints))

## 1. Tìm các endpoint của GraphQL

Trước khi có thể kiểm thử về tấn công GraphQL thì việc đầu tiên bạn cần làm là tìm các endpoint của nó. Bởi vì theo kiến trúc thì GraphQL chỉ sử dụng 1 endpoint cho các request gửi tới 

**Universal queries**

Nếu bạn gửi yêu cầu `query{__typename}`đến bất kỳ điểm cuối GraphQL nào, chuỗi đó sẽ được bao gồm `{"data": {"__typename": "query"}}`ở đâu đó trong phản hồi của nó. Điều này được gọi là truy vấn phổ quát, và là một công cụ hữu ích để kiểm tra xem URL có tương ứng với dịch vụ GraphQL hay không.

Truy vấn hoạt động vì mỗi điểm cuối GraphQL đều có một trường dành riêng có tên là `type` `__typename`trả về kiểu dữ liệu của đối tượng được truy vấn dưới dạng chuỗi.

**Tìm các điểm cuối phổ biến** 

Các dịch vụ GraphQL thường sử dụng các hậu tố điểm cuối tương tự. Khi kiểm thử các điểm cuối GraphQL, bạn nên gửi các truy vấn chung đến các vị trí sau:

- `/graphql`
- `/api`
- `/api/graphql`
- `/graphql/api`
- `/graphql/graphql`

Nếu các điểm cuối phổ biến này không trả về phản hồi GraphQL, bạn cũng có thể thử thêm `/v1`vào đường dẫn.

## Request methods

GraphQL endpoint trong production thường:

- Chỉ chấp nhận `POST`
- Content-Type: `application/json`

Điều này giúp giảm rủi ro như CSRF.

Tuy nhiên, một số hệ thống vẫn hỗ trợ:

- `GET` requests
- `POST` với `x-www-form-urlencoded`

 Khi không tìm được endpoint bằng POST, nên thử lại với các method khác.


Sau khi xác định endpoint, bước tiếp theo là gửi các query cơ bản để hiểu cách API hoạt động.

Nếu endpoint được dùng bởi web app:

- Dùng Burp Suite browser
- Quan sát HTTP history
- Phân tích các query thực tế được gửi

Mục tiêu:

- Xác định structure query
- Hiểu cách truyền arguments
- Xem response format

## Exploiting unsanitized arguments

Arguments là điểm bắt đầu tốt để tìm bug.

Nếu API dùng arguments để truy cập trực tiếp object, có thể xảy ra:

**IDOR (Insecure Direct Object Reference)**

Ví dụ:

```
query {
  products {
    id
    name
    listed
  }
}
```

Response chỉ trả về sản phẩm `listed = true`.

Nếu ID là tuần tự, có thể suy ra:

- ID bị thiếu có thể là dữ liệu bị ẩn

Thử query trực tiếp:

```
query {
  product(id: 3) {
    id
    name
    listed
  }
}
```

Nếu server trả dữ liệu thì xác nhận có vấn đề về access control

## Discovering schema information

Bước tiếp theo trong quá trình kiểm thử là thu thập thông tin về lượt đồ cơ bản , cần reconstruct schema.

Cách tốt nhất để làm điều này là sử dụng các truy vấn nội suy. Nội suy hay còn gọi là instropection là một chức năng tích hợp sẵn của GraphQL cho phép bạn truy vấn máy chủ để lấy thông tin về lược đồ.

Để sử dụng phương pháp nội quan nhằm khám phá thông tin lược đồ, hãy truy vấn `__schema`trường này. Trường này có sẵn trên kiểu gốc của tất cả các truy vấn.

Tương tự như các truy vấn thông thường, bạn có thể chỉ định các trường và cấu trúc của phản hồi mà bạn muốn nhận được khi chạy truy vấn nội suy. Ví dụ, bạn có thể muốn phản hồi chỉ chứa tên của các mutation khả dụng.

Ngoài ra Burp cũng có thể tạo các truy vấn nội suy cho bạn. Để biết thêm thông tin, hãy xem [Truy cập lược đồ API GraphQL bằng cách sử dụng nội suy](https://portswigger.net/burp/documentation/desktop/testing-workflow/working-with-graphql#accessing-graphql-api-schemas-using-introspection) .

![image.png](/assets/images/graphql/image-2.png)

Query vào `__schema` để lấy thông tin:

```
{
  "query":"{__schema{queryType{name}}}"
}
```

Nếu thành công:

- Introspection đang bật
- Có thể enumerate toàn bộ API

## Full introspection

Chạy full introspection query để lấy:

- Queries
- Mutations
- Types
- Fields
- Relationships

## Visualizing schema

Kết quả introspection thường khó phân tích trực tiếp.

Có thể dùng GraphQL visualizer để:

- Map relationships
- Hiểu flow data nhanh hơn
- Bạn có thể tham khảo link ở đây [https://nathanrandal.com/graphql-visualizer/](https://nathanrandal.com/graphql-visualizer/)

Dù best practice là disable introspection, nhưng thực tế nhiều hệ thống vẫn bật.

 Luôn thử introspection query đơn giản trước

Nếu thành công:

→ attack surface tăng đáng kể

## Suggestions (khi introspection bị tắt)

Ngay cả khi introspection bị disable, vẫn có thể leak thông tin qua error message.

Ví dụ:

```
Did you mean 'productInformation'?
```

Server vô tình tiết lộ tên field hợp lệ

Một số tool có thể tận dụng cơ chế này để rebuild schema.

## Summary (pentest mindset)

- Test nhiều HTTP methods → tìm endpoint
- Quan sát traffic thật → hiểu cách app dùng GraphQL
- Fuzz arguments → tìm IDOR
- Introspection → map toàn bộ schema
- Suggestions → fallback khi introspection bị tắt

Để các bạn có thể hình dung rõ hơn thì bài này mình sẽ làm rõ hơn về các cách tấn công thông qua các bài lab trên PortSwigger 

Thì bài đầu tiên thì yêu cầu chúng ta phải tìm ra 1 secret password để có thể solve the lab.

![image.png](/assets/images/graphql/image-3.png)

## Lab: Accessing private GraphQL posts – Walkthrough

Khi vào lab, việc đầu tiên mình làm là mở trang blog bằng browser tích hợp trong Burp Suite để quan sát cách dữ liệu được load.

Ngay lập tức có thể thấy các bài viết không được render sẵn từ server-side, mà được fetch thông qua một request API. Mở sang tab **HTTP history**, mình thấy có request gửi tới endpoint `/graphql/v1`. Đây là dấu hiệu rõ ràng ứng dụng đang sử dụng GraphQL.

Khi xem response của request này, có một chi tiết khá đáng chú ý: mỗi bài blog đều có một `id` và các id này tăng tuần tự. Tuy nhiên danh sách trả về lại bị thiếu `id = 3`. Điều này thường không phải ngẫu nhiên — nhiều khả năng đây là một bài viết bị ẩn.

![image.png](/assets/images/graphql/image-4.png)

### Recon – hiểu schema

Để hiểu API rõ hơn, mình gửi request này sang Repeater.

Tại đây, Burp hỗ trợ rất tiện: chỉ cần click chuột phải → **GraphQL → Set introspection query**, nó sẽ tự generate một introspection query hoàn chỉnh. Sau khi gửi request, response trả về toàn bộ schema của API.

Khi đọc qua schema, mình phát hiện trong type `BlogPost` có một field khá thú vị là `postPassword`. Field này không xuất hiện trong response ban đầu, nghĩa là client bình thường không request tới — nhưng backend vẫn expose.

Bạn có thể ném vào trang này để có thể hiểu rõ hơn về response

![image.png](/assets/images/graphql/image-5.png)

Đây gần như là “mùi bug” rõ ràng bởi vì có khả năng dữ liệu nhạy cảm tồn tại nhưng không được kiểm soát đúng cách.

![image.png](/assets/images/graphql/image-6.png)

### 

Quay lại request ban đầu trong HTTP history và gửi lại vào Repeater, lần này mình không dùng introspection nữa mà chỉnh trực tiếp query.

Trong phần variables, mình đổi `id` thành `3` — chính là ID bị thiếu trước đó.

Sau đó, trong query, mình thêm field `postPassword` vào cùng với các field khác.

Khi gửi request, server trả về đầy đủ thông tin của bài viết `id = 3`, bao gồm cả `postPassword`.

Điều này xác nhận:

- Không có kiểm soát truy cập theo ID
- Backend cho phép truy vấn dữ liệu ẩn nếu biết ID

Đây chính là một dạng **IDOR trong GraphQL**.

### 

![image.png](/assets/images/graphql/image-7.png)

Lúc này chỉ cần copy giá trị của `postPassword` từ response và submit vào lab là xong.

![image.png](/assets/images/graphql/image-8.png)

## Lab: Accidental exposure of private GraphQL fields – Walkthrough

Khi vào lab, mình mở trang **My account** và thử đăng nhập như bình thường. Mục đích không phải để login thành công, mà để xem phía client đang gửi request gì.

Chuyển sang tab HTTP history trong Burp Suite, mình thấy request login không phải dạng REST quen thuộc mà là một **GraphQL mutation**. Payload chứa `username` và `password`, nghĩa là toàn bộ logic auth đang đi qua GraphQL.

Đểm quan trọng t có thấy thấy là nếu login dùng GraphQL, khả năng cao user data cũng có thể bị truy vấn qua các query khác.

![image.png](/assets/images/graphql/image-9.png)

### Recon – enumerate schema

Mình gửi request login này sang Repeater, sau đó dùng tính năng **Set introspection query** để dump schema.

Sau khi gửi request, Burp cho phép lưu toàn bộ query vào site map. Khi xem lại, có một query khá đáng chú ý: `getUser`.

Query này cho phép lấy thông tin user dựa trên `id`, và quan trọng hơn là nó trả về cả **username và password**.

![image.png](/assets/images/graphql/image-10.png)

Đây là một design flaw rõ ràng:

- API expose field nhạy cảm (password)
- Không có dấu hiệu filtering theo role

Mình gửi query `getUser` sang Repeater và thử với giá trị mặc định (`id = 0`) nhưng không có kết quả.

Để thuận tiện cho việc generate ra querry thì bạn có thể sử dụng extension InQL trong BAppstore của Burpsuite

![image.png](/assets/images/graphql/image-11.png)

Tiếp theo, đơn giản là thử các giá trị ID khác. Vì đây là lab, ID thường là số nhỏ và tuần tự. Khi thử `id = 1`, server trả về:

![image.png](/assets/images/graphql/image-12.png)

- username: administrator
- password: (password thật)

Dùng username và password vừa lấy được để đăng nhập lại vào hệ thống.

Sau khi login thành công với quyền admin, truy cập vào Admin panel và xóa user `carlos` là hoàn thành lab.

Lab: Finding a hidden GraphQL endpoint – Walkthrough

![image.png](/assets/images/graphql/image-13.png)

Khi vào lab, nếu chỉ click qua các chức năng trên web thì gần như không thấy dấu hiệu nào của GraphQL. Điều này gợi ý ngay từ đầu: endpoint có thể bị ẩn, không được gọi trực tiếp từ frontend.

Lúc này mình không đi theo hướng “click UI” nữa mà chuyển sang brute nhẹ các endpoint phổ biến trong Repeater, kiểu như `/graphql`, `/api`, `/graphql/v1`…

Khi gửi request GET tới `/api`, server trả về lỗi kiểu `"Query not present"`. Đây là một dấu hiệu rất đặc trưng của GraphQL — tức là endpoint tồn tại, nhưng mình chưa gửi query.

![image.png](/assets/images/graphql/image-14.png)

Thử thêm một universal query đơn giản vào URL:

```
/api?query=query{__typename}
```

Response trả về:

![image.png](/assets/images/graphql/image-15.png)

Đến đây có thể khẳng định `/api` chính là GraphQL endpoint, chỉ là nó không được expose ra UI.

### 

Bước tiếp theo là enumerate schema bằng introspection. Tuy nhiên khi gửi introspection query bình thường, server từ chối — rõ ràng có cơ chế chặn.

![image.png](/assets/images/graphql/image-16.png)

Nhưng điểm yếu ở đây là cách chặn không cẩn thận. Nhiều hệ thống chỉ dùng regex để block pattern kiểu `__schema{`.

GraphQL parser thì không quan tâm whitespace, nên nếu chèn thêm ký tự xuống dòng hoặc space, query vẫn hợp lệ nhưng không còn match regex nữa.

Mình sửa introspection query bằng cách thêm newline sau `__schema`, rồi encode lại vào URL.

Sau khi gửi lại request, lần này server trả về full schema.

![image.png](/assets/images/graphql/image-17.png)

 Điều này giúp mình xác nhận rằng :

- Introspection không thực sự bị disable
- Chỉ bị filter bằng regex yếu

Sau khi có schema, mình dùng Burp lưu toàn bộ query vào site map để dễ xem.

Lúc này có thể thấy các query và mutation quan trọng, trong đó có:

- `getUser`
- `deleteOrganizationUser`

Đây là 2 function rất đáng chú ý:

- Một cái để lấy user
- Một cái để xóa user

Mình gửi `getUser` vào Repeater và thử với các ID khác nhau.

Ban đầu `id = 0` không trả về gì. Tiếp tục tăng dần, đến `id = 3` thì thấy trả về user `carlos`.

![image.png](/assets/images/graphql/image-18.png)

Như vậy: ID của carlos là 3

![image.png](/assets/images/graphql/image-19.png)

### 

Quay lại schema, mình thấy mutation `deleteOrganizationUser` nhận input là user ID.

Chỉ cần craft một mutation đơn giản, truyền `id = 3`.

![image.png](/assets/images/graphql/image-20.png)

Sau khi gửi, user `carlos` bị xóa và lab hoàn thành.

### Lab: Bypassing GraphQL brute force protections

Lab này yêu cầu brute force tài khoản `carlos`, nhưng API có **rate limiting**.

Điểm mấu chốt là phải **bypass rate limit bằng GraphQL aliases**.

Khi truy cập chức năng đăng nhập, có thể thấy request login được gửi dưới dạng **GraphQL mutation**. 

![image.png](/assets/images/graphql/image-21.png)

Khi thử login sai nhiều lần trong Burp Repeater, server bắt đầu trả về lỗi rate limit. Điều này chứng tỏ API đang giới hạn số lượng request theo thời gian.

Tuy nhiên, cơ chế này chỉ đếm **số HTTP request**, không quan tâm bên trong request có bao nhiêu operation.

GraphQL hỗ trợ **aliases**, để cho các bạn ko biết aliases là gì thì mình có viết ở trên nhé , thì aliases cho phép gửi nhiều operation trong một request.

Điều này tạo ra một điểm yếu quan trọng:

- Thay vì gửi nhiều request → bị rate limit
- Ta gửi **1 request duy nhất chứa hàng chục login thì sẽ ko bị dính request**

Sau khi gửi request login vào Repeater, bạn cần chỉnh sửa lại payload.

Đầu tiên, bỏ phần `variables` và `operationName`, vì ta sẽ viết query thủ công.

![image.png](/assets/images/graphql/image-22.png)

Sau đó, tạo một mutation chứa nhiều alias, mỗi alias là một lần thử password khác nhau cho user `carlos`.

Ví dụ:

```
mutation {
  bruteforce0: login(input:{username:"carlos", password:"123456"}) {
    token
    success
  }

  bruteforce1: login(input:{username:"carlos", password:"password"}) {
    token
    success
  }

  bruteforce2: login(input:{username:"carlos", password:"qwerty"}) {
    token
    success
  }
}
```

Bạn có thể generate danh sách này từ wordlist password của lab (bạn có thể nhờ gpt viết dùm cho nhanh hehe =))

![image.png](/assets/images/graphql/image-23.png)

Khi gửi request:

- Server sẽ trả về response chứa **kết quả của từng alias**
- Mỗi alias có field `success`

Chỉ cần tìm:

```
"success": true
```

→ đó là password đúng.

![image.png](/assets/images/graphql/image-24.png)

# Preventing graphql-attacks

Khi deploy GraphQL API lên production, nếu cấu hình không cẩn thận thì rất dễ dính các lỗi như lộ schema, brute force, hoặc CSRF. Dưới đây là những điểm quan trọng cần lưu ý.

## Bảo vệ schema và thông tin nhạy cảm

Nếu API không dành cho public, nên **tắt introspection** để tránh việc attacker dễ dàng xem toàn bộ schema. Điều này giúp giảm đáng kể khả năng bị lộ cấu trúc API và các field nhạy cảm.

Trong trường hợp API public và bắt buộc phải bật introspection, cần rà soát kỹ schema để đảm bảo không expose các field quan trọng như email, user ID hoặc dữ liệu nội bộ.

Ngoài ra, nên **tắt cơ chế suggestions**. Nếu để bật, attacker có thể lợi dụng lỗi gợi ý để suy ra tên field hoặc query hợp lệ, từ đó từng bước reconstruct schema (ví dụ dùng tool như Clairvoyance).

## Ngăn chặn brute force & abuse

GraphQL có một điểm yếu là có thể bị abuse thông qua **aliases** hoặc query phức tạp. Vì vậy, việc chỉ dùng rate limit theo HTTP request là chưa đủ.

Cách phòng thủ hiệu quả hơn là kiểm soát trực tiếp query:

- **Giới hạn độ sâu (query depth)**: tránh các query lồng nhiều tầng gây tốn tài nguyên hoặc bị lợi dụng cho DoS
- **Giới hạn số lượng operation / alias**: ngăn attacker nhồi nhiều request vào một query
- **Giới hạn kích thước query**: tránh payload quá lớn
- **Áp dụng cost analysis**: tính toán “chi phí” của query, nếu quá nặng thì reject ngay

Những biện pháp này giúp giảm khả năng brute force và abuse tài nguyên server.

## Ngăn chặn CSRF với GraphQL

GraphQL cũng có thể dính CSRF nếu cấu hình không đúng.

Để phòng tránh:

- Chỉ accept request dạng **POST + application/json**
- Validate đúng **Content-Type**
- Sử dụng **CSRF token** cho các hành động quan trọng

Điều này giúp đảm bảo request thực sự đến từ client hợp lệ, không phải bị giả mạo từ bên thứ ba.

Cảm ơn các bạn đã dành thời gian đọc bài viết mình!!!

Bạn có thể tham khảo thêm về blog về lỗ hổng này mình thấy họ viết khá là hay ở đây 

[https://deepstrike.io/blog/graphql-api-vulnerabilities-and-common-attacks](https://deepstrike.io/blog/graphql-api-vulnerabilities-and-common-attacks)

[Document từ thầy Nguyễn Thành Tâm - team mình ❤️](https://docs.google.com/document/d/10QUvigaj1IYl2TAStm96mXcroP7ysVX-q0ryXxAJFwU/edit?tab=t.0)
