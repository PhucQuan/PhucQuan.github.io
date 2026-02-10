---
layout: single
title: "HTB Challenge - NextPath Writeup"
categories: [Hack The Box]
tags: [web, nodejs, path-traversal, procfs, truncation]
date: 2026-01-15
permalink: /writeups/htb-nextpath/
---

## Challenge Info

**Event:** HackTheBox  
**Challenge Name:** NextPath  
**Category:** Web  
**Difficulty:** Medium  

**Challenge Description:**
Một bài challenge thú vị về lỗ hổng Path Traversal trong môi trường Node.js. Mục tiêu của chúng ta là đọc được nội dung file `/flag.txt` nằm trong thư mục gốc của container. Bài này đòi hỏi kết hợp nhiều kỹ thuật từ bypass filter, xử lý truncation (cắt chuỗi) cho đến kiến thức sâu về hệ thống file `/proc` trên Linux.

<!-- more -->

---

## Initial Reconnaissance

### Phân tích mã nguồn (Source Code Analysis)
Khi tiếp cận challenge này, chúng ta được cung cấp mã nguồn. File quan trọng nhất cần phân tích là `team.js`:

```javascript
import path from 'path';
import fs from 'fs';

const ID_REGEX = /^[0-9]+$/m;

export default function handler({ query }, res) {
  if (!query.id) {
    res.status(400).end("Missing id parameter");
    return;
  }

  // Check format
  if (!ID_REGEX.test(query.id)) {
    console.error("Invalid format:", query.id);
    res.status(400).end("Invalid format");
    return;
  }
  // Prevent directory traversal
  if (query.id.includes("/") || query.id.includes("..")) {
    console.error("DIRECTORY TRAVERSAL DETECTED:", query.id);
    res.status(400).end("DIRECTORY TRAVERSAL DETECTED?!? This incident will be reported.");
    return;
  }

  try {
    const filepath = path.join("team", query.id + ".png");
    const content = fs.readFileSync(filepath.slice(0, 100));

    res.setHeader("Content-Type", "image/png");
    res.status(200).end(content);
  } catch (e) {
    console.error("Not Found", e.toString());
    res.status(404).end(e.toString());
  }
}
```

Sau khi xem xét, mình phát hiện ra hai điểm yếu "chết người" trong logic xử lý đường dẫn của ứng dụng Node.js này.

#### 1. Filter Bypass: Câu chuyện "Vỏ quýt dày có móng tay nhọn"

Hãy đặt mình vào vị trí của lập trình viên (Developer) khi viết đoạn code này. Họ đã cố gắng dựng lên 2 lớp rào chắn để ngăn chặn hacker, nhưng tiếc thay, cả 2 đều có kẽ hở nghiêm trọng.

##### a. Lớp bảo vệ 1: Regular Expression (Regex)
**Ý tưởng của Dev:** "Tôi chỉ cho phép nhập số. Dùng Regex `^[0-9]+$` là chuẩn bài, chỉ chấp nhận chuỗi số từ đầu (`^`) đến cuối (`$`)."

**Sai lầm tai hại:** Họ thêm flag `/m` (multiline).
```javascript
const ID_REGEX = /^[0-9]+$/m;
```
Flag `/m` thay đổi luật chơi: Thay vì kiểm tra *toàn bộ văn bản*, nó kiểm tra *từng dòng*. Nếu *bất kỳ dòng nào* là số hợp lệ, nó sẽ trả về `True`.

**Tư duy Hacker (Solve):**
"À, vậy thì mình không cần toàn bộ payload phải là số. Mình chỉ cần **dòng đầu tiên** là số để đánh lừa Regex, còn **dòng thứ hai** chứa mã độc thì nó không quan tâm!"
=> **Payload:** `123` (xuống dòng) `../../etc/passwd`

##### b. Lớp bảo vệ 2: Hàm `.includes()`
**Ý tưởng của Dev:** "Nếu hacker cố tình chèn ký tự lạ như `..` hay `/`, mình sẽ block ngay bằng hàm `.includes()`."

**Sai lầm tai hại:** Họ quên rằng trong Node.js (Express), tham số `id` có thể là một **Chuỗi (String)** hoặc một **Mảng (Array)**.

**Tư duy Hacker (Solve - Type Confusion):**
*   Nếu `id` là chuỗi `"../flag"`, hàm `.includes("..")` sẽ soi từng ký tự bên trong -> Bị phát hiện ngay.
*   Nhưng nếu mình biến `id` thành Mảng `["123", "../flag"]` thì sao?
    *   Hàm `.includes()` của Mảng hoạt động khác hẳn. Nó hỏi: "Có phần tử nào **bằng y hệt** chuỗi `..` không?".
    *   Câu trả lời là **KHÔNG**. Vì phần tử thứ 2 là `"../flag"`, nó *chứa* `..` chứ không *bằng* `..`.

**Chốt hạ:** Bằng cách gửi `?id=123&id=../flag`, ta biến `id` thành mảng, vượt qua cả Regex (chỉ check dòng đầu) và `.includes()` (check sai kiểu).

##### c. Cơ chế "Nối chuỗi" (Path Join)
Sau khi vượt qua kiểm tra, ứng dụng thực hiện:
```javascript
const filepath = path.join("team", query.id + ".png");
```
Khi `query.id` là mảng, phép cộng chuỗi `query.id + ".png"` sẽ ép kiểu mảng thành chuỗi theo quy tắc nối dấu phẩy:
`"1\n" + "," + "../../etc/passwd" + ".png"` -> `"1\n,../../etc/passwd.png"`

Cuối cùng `path.join` sẽ xử lý chuỗi này:
`team/1\n,../../etc/passwd.png`
Hệ điều hành sẽ hiểu là: Vào thư mục `team`, vào thư mục (tên lạ) `1\n,`, sau đó đi ngược lên 2 lần (`../../`).
Điều này cho phép chúng ta thoát khỏi thư mục giới hạn.

#### 2. Truncation: Cuộc chiến với 100 ký tự

Sau khi bypass được filter, chúng ta đối mặt với "trùm cuối": đoạn code nối chuỗi `+ '.png'` và cắt chuỗi `.slice(0, 100)`.

```javascript
// Mã server
const filepath = path.join("teams", id + ".png").slice(0, 100);
```

**Mục tiêu:** Làm sao để đường dẫn của chúng ta, khi cộng thêm `.png`, có tổng độ dài > 100 ký tự. Quan trọng hơn, phần đuôi `.png` phải bắt đầu từ ký tự thứ 101 trở đi để bị hàm `.slice()` cắt bỏ.

**Thử nghiệm 1: Padding thủ công**
Ý tưởng đầu tiên là thêm thật nhiều dấu `../` hoặc `./` để độn độ dài.
Tuy nhiên, hàm `path.join()` trong Node.js quá thông minh. Nó tự động:
*   Xóa bỏ `./` thừa.
*   Gộp `foo//bar` thành `foo/bar`.
*   Triệt tiêu các cặp `dir/../`.

Do đó, việc căn chỉnh độ dài bằng các ký tự này là **bất khả thi**. Nếu chuỗi ngắn quá hoặc dài quá mà không khớp, ta sẽ gặp các lỗi hài hước như:

*   **Thiếu độ dài (`flag.txt.p`):** Chuỗi chưa đủ dài để đẩy hết đuôi `.png`.
    ![Lỗi flag.txt.p](/assets/images/htb-nextpath/truncation-fail-1.png)

*   **Thừa độ dài (`flag.tx`):** Chuỗi quá dài, cắt mất nội dung.
    ![Lỗi flag.tx](/assets/images/htb-nextpath/truncation-fail-2.png)

---

## Exploitation: Kỹ thuật "Vàng" `/proc`

### Phép thử và sai (Trial and Error)
Bế tắc với việc padding, mình tự hỏi: **"Làm sao để có một đường dẫn rất dài, nhưng lại hợp lệ và trỏ về đúng file gốc?"**

Trong Linux, hệ thống file `/proc` là một "kho báu".
*   `/proc/self/root`: Trỏ về thư mục gốc `/`.
*   `/proc/1/root`: Cũng trỏ về thư mục gốc `/` (nếu ta có quyền, và trong Docker container thì thường PID 1 là process chính).

**Ý tưởng đột phá:**
Thay vì chỉ dùng `/flag.txt` (quá ngắn), ta dùng `/proc/1/task/1/root/flag.txt`.
*   Nó vẫn trỏ về đúng file flag.
*   Nhưng nó dài hơn rất nhiều! (Thêm được khoảng 21 ký tự "sạch").

Điều này giúp ta dễ dàng lấp đầy 100 ký tự mà không cần phụ thuộc hoàn toàn vào `../`.

### Payload hoàn hảo
Sau vài lần tính toán độ dài, mình tìm ra công thức chuẩn:

$$ \text{Length} = \text{Prefix ("teams/")} + \text{Padding ("../" * n)} + \text{Target Path (/proc/...)} = 100 $$

Payload cuối cùng gửi đi sẽ có dạng:
`?id=1%0a&id=../../../../[...]/proc/1/task/1/root/flag.txt`

---

## Exploitation: Kỹ thuật "Vàng" `/proc`

Đây là lúc kiến thức về hệ thống file Linux phát huy tác dụng. Thay vì cố gắng trỏ trực tiếp đến `/flag.txt`, chúng ta sẽ đi đường vòng qua hệ thống file ảo `/proc`.

Đường dẫn mình sử dụng là:
`/proc/1/task/1/root/`

### 1. Tại sao cách này lại thành công?
Sử dụng `/proc/1/task/1/root/` mang lại hai lợi thế lớn mà các cách trước đó không làm được:

*   **Tăng độ dài "sạch" cho chuỗi:** Đường dẫn `/proc/1/task/1/root/` dài tới **21 ký tự** (so với 1 ký tự `/` ở root). Việc này giúp chúng ta "lấp đầy" khung 100 ký tự nhanh hơn rất nhiều mà không cần dùng quá nhiều cụm `../` (vốn dễ gây sai sót và khó căn chỉnh).
*   **Trỏ thẳng vào Root của Container:** Trong các môi trường Docker (như bài HTB này), Process 1 (PID 1) thường là tiến trình chính khởi chạy container. Symbolic link `/root/` bên trong thư mục của tiến trình đó (`/proc/1/root`) thực chất dẫn thẳng đến thư mục gốc `/` của toàn bộ container.

### 2. Phép toán "về đích"

Bài toán bây giờ trở thành một phép tính cộng đơn giản để đảm bảo ký tự cuối cùng của `flag.txt` nằm đúng ở vị trí index 99 (ký tự thứ 100).

Công thức tính:
$$ \text{Length} = \text{Prefix ("teams/")} + \text{Padding ("../" * n)} + \text{Target Path} = 100 $$

Với đường dẫn mới: `.../proc/1/task/1/root/flag.txt`
Đường dẫn này dài hơn, giúp chữ `t` cuối cùng của `flag.txt` dễ dàng rơi đúng vào vị trí thứ 100.

### 3. Payload cuối cùng

URL Payload hoàn chỉnh sẽ trông như thế này:

```http
http://<IP>:<PORT>/api/team?id=1%0a&id=../../../../../../../../../../../../../../../../../../../../../../proc/1/task/1/root/flag.txt
```

**Giải thích payload:**
*   `id=1%0a`: Phần tử đầu tiên của mảng (dummy), có thể chứa ký tự xuống dòng để tránh lỗi hoặc chỉ là rác.
*   `id=...`: Phần tử thứ hai chính là payload tấn công của chúng ta.
*   `../../...`: Chuỗi Path Traversal để quay về gốc.
*   `/proc/1/task/1/root/flag.txt`: Đường dẫn đi qua ProcFS để trỏ vào file flag, đồng thời padding độ dài.

---

## Kết quả (Result)

Khi gửi request trên, phía Server sẽ xử lý như sau:
1.  Hàm `path.join` nối chuỗi.
2.  Kết quả sau khi nối đạt đúng 100 ký tự tại chữ `t` cuối cùng của `flag.txt`.
3.  Phần `.png` được nối thêm vào trở thành ký tự thứ 101 trở đi.
4.  Hàm `.slice(0, 100)` cắt bỏ `.png`.
5.  Server đọc đúng file `/flag.txt` và trả về nội dung.

Kiểm tra trong tab **RAW** của Burp Suite (hoặc view source), chúng ta sẽ thấy Flag (lưu ý không xem ở tab Render/Preview vì nó sẽ cố hiển thị text như hình ảnh và bị lỗi).

**Flag:**
```
HTB{p4th_trunc4t1on_v14_proc_fs_m4st3ry}
```

---

## Key Lessons Learned

1.  **Node.js Query Parameter Pollution:** Luôn cẩn thận khi đối số `req.query` có thể là mảng thay vì chuỗi. Nên sử dụng Type Checking hoặc các thư viện validation chặt chẽ.
2.  **Path Truncation:** Việc cắt chuỗi đường dẫn (như dùng `.slice`) sau khi validate hoặc nối chuỗi có thể dẫn đến việc thay đổi extension của file, cho phép đọc các file không mong muốn.
3.  **ProcFS Power:** Hệ thống file `/proc` không chỉ chứa thông tin tiến trình mà còn là một vector tấn công lợi hại để bypass các bộ lọc đường dẫn hoặc leo thang đặc quyền trong một số trường hợp.
4.  **Luôn kiểm tra Raw Response:** Trong các bài CTF web, đôi khi flag nằm trong response nhưng client (trình duyệt/tool) không hiển thị được do sai định dạng (ví dụ response text nhưng header là image).

--- 
*Writeup by PhucQuan*
