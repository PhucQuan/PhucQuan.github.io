---
layout: single
title: "[Writeup] HCMUTE CTF 2026 - Qualification Round"
date: 2026-01-29
classes: wide
categories: [HCMUTE CTF 2026, web]
tags: [hcmute, web, javascript, client-side]
permalink: /writeups/hcmute-ctf-overtrust/
---

Tiếp theo là tới giải HCMUTE CTF của trường mình nha. Đây là giải vòng loại câu lạc bộ HCMUTE ISC, và trộm vía là mình đã đạt Top 1 ! :D.Nên mình muốn chia sẻ quá trình giải của mình ở trên đây cho mọi người cùng tham khảooo 

![HCMUTE Scoreboard](/assets/images/hcmute/scoreboard.png)

Mình sẽ chia sẻ writeup từng phần, và phần đầu tiên bắt đầu với Web.

## Bài 1: Overtrust

Bài này mình tìm thấy một đoạn code JavaScript khá thú vị trong source code mà họ public:

```javascript
let questions = [];
let answerOptions = [];
let userAnswers = {};
let currentQuestionIndex = 0;

const correctAnswers = {
    1: "C", 2: "A", 3: "D", 4: "A", 5: "A", 6: "A", 7: "C", 8: "B", 9: "B", 10: "D",
    11: "C", 12: "A", 13: "A", 14: "A", 15: "B", 16: "C", 17: "D", 18: "C", 19: "C", 20: "B",
    21: "B", 22: "C", 23: "B", 24: "C", 25: "A", 26: "C", 27: "A", 28: "A", 29: "A", 30: "A",
    31: "B", 32: "C", 33: "A", 34: "A", 35: "B", 36: "C", 37: "B", 38: "C", 39: "B", 40: "A"
};

// ... (các hàm loadQuizData, displayQuestion...)

function submitQuiz() {
    const totalQuestions = questions.length;
    const answeredCount = Object.keys(userAnswers).length;

    if (answeredCount < totalQuestions) {
        alert(`You have only answered ${answeredCount} out of ${totalQuestions} questions. Please answer all questions.`);
        return;
    }

    let correctCount = 0;
    for (let questionId in correctAnswers) {
        if (userAnswers[questionId] === correctAnswers[questionId]) {
            correctCount++;
        }
    }

    if (correctCount === totalQuestions) {
        window.location.href = 'congratulation.php';
    } else {
        alert(`Try Harder to get a perfect score :))\n\nYou got ${correctCount}/${totalQuestions} correct answers.`);
        userAnswers = {};
        currentQuestionIndex = 0;
        displayQuestion();
    }
}
```

Trong đoạn code JavaScript trên, có hai điểm cực kỳ yếu kém về bảo mật mà mình nhận thấy ngay:

### 1. Lộ toàn bộ đáp án (Hardcoded Answers)

Biến `const correctAnswers` chứa toàn bộ đáp án từ câu 1 đến 40 ngay trong mã nguồn. Chúng ta không cần phải suy nghĩ hay tìm kiếm đâu xa, đáp án nằm ngay trước mắt:

- **Câu 1-10:** C, A, D, A, A, A, C, B, B, D.
- **Câu 11-20:** C, A, A, A, B, C, D, C, C, B.
- ...và tương tự cho đến câu 40.

### 2. Kiểm tra điểm số tại Client (Client-Side Verification)

Hàm `submitQuiz()` thực hiện việc tính toán số câu đúng ngay trên trình duyệt của người dùng:

```javascript
if (correctCount === totalQuestions) {
    window.location.href = 'congratulation.php';
}
```

Nếu `correctCount` bằng tổng số câu hỏi, nó sẽ chuyển hướng chúng ta đến `congratulation.php`. Đây chính là nơi khả năng cao sẽ hiển thị **Flag**.

---

## Cách khai thác (Cách làm "Tà đạo" nhanh nhất)

Vì logic kiểm tra nằm hoàn toàn ở máy của mình (Client-side), mình không cần phải ngồi tích từng câu làm gì cho mệt.

Mình mở trang quiz lên, nhấn **F12**, chọn tab **Console** và dán đoạn code sau vào rồi nhấn Enter:

```javascript
// Bước 1: Tự động điền tất cả đáp án đúng vào biến userAnswers
for (let id in correctAnswers) {
    userAnswers[id] = correctAnswers[id];
}

// Bước 2: Gọi hàm nộp bài để kích hoạt chuyển hướng
submitQuiz();
```

### Tại sao cách này hoạt động?

1.  **Thao túng dữ liệu:** Mình ghi đè biến `userAnswers` bằng dữ liệu từ `correctAnswers` (đáp án đúng) ngay trong bộ nhớ trình duyệt.
2.  **Bypass kiểm tra:** Khi `submitQuiz()` chạy, vòng lặp so sánh sẽ thấy 100% khớp nhau, `correctCount` sẽ bằng `totalQuestions`, và lệnh `window.location.href` sẽ thực thi, đưa mình thẳng đến nơi cất giấu Flag.

Hẹn gặp mọi người ở các phần writeup tiếp theo của giải này nhé!

---

### Series Writeup HCMUTE CTF 2026:

1.  **[Web] Overtrust** (Bài này)
2.  **[Web/SSTI] [Greeting](/writeups/hcmute-ctf-greeting/)**
3.  **[Web/Socket] [Gau](/writeups/hcmute-ctf-gau/)**
4.  **[Web/Pentest] [FinTrack](/writeups/hcmute-ctf-fintrack/)**
5.  **[Reverse] [XiDach](/writeups/hcmute-ctf-xidach/)**
6.  **[Crypto] [Mirror Split Secrets](/writeups/hcmute-ctf-mirror-split/)**
7.  **[Crypto] [Power Tower](/writeups/hcmute-ctf-power-tower/)**
8.  **[Crypto] [What is a secret](/writeups/utectf-what-is-a-secret/)**
