# 🛡️ ScamCheck AI

## Giới thiệu

ScamCheck AI là một hệ thống hỗ trợ phát hiện tin nhắn và website có dấu hiệu lừa đảo bằng Google Gemini AI.

Người dùng chỉ cần nhập nội dung tin nhắn hoặc đường dẫn website cần kiểm tra, hệ thống sẽ:

* Phân tích bằng Gemini AI.
* Đánh giá mức độ rủi ro (**An toàn – Nghi ngờ – Nguy hiểm**).
* Giải thích lý do đánh giá.
* Đưa ra các bước xử lý phù hợp.
* Hỗ trợ ứng cứu khi người dùng đã bấm link, chuyển khoản hoặc cung cấp OTP.
* Tạo thẻ cảnh báo để chia sẻ cho người thân.

---

# ✨ Tính năng

* 🤖 Phân tích tin nhắn bằng Gemini AI
* 🌐 Phân tích website nghi ngờ lừa đảo
* 🟢 Phân loại mức độ rủi ro (An toàn, Nghi ngờ, Nguy hiểm)
* 📖 Scam Library giới thiệu các hình thức lừa đảo phổ biến
* 👩‍🏫 Cô tâm lý giải thích thủ thuật tâm lý của kẻ gian
* 🚑 Người ứng cứu hướng dẫn xử lý khi đã bị lừa
* 📜 Lưu lịch sử 10 lần phân tích gần nhất
* 🔗 Chia sẻ kết quả bằng đường dẫn
* 🖼️ Tạo thẻ cảnh báo để chia sẻ
* 🔄 Có cơ chế dự phòng khi Gemini API gặp lỗi

---

# 💻 Công nghệ sử dụng

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask
* Flask-CORS

### AI

* Google Gemini API

### Database

* JSON

---

## ⚙️ Cách cài đặt

### 1. Clone project

```bash
git clone https://github.com/USERNAME/ScamCheck.git
cd ScamCheck
```

### 2. Cài thư viện

```bash
pip install -r requirements.txt
```

### 3. Tạo file cấu hình API Key

Tạo thư mục:

```text
.gitignore
```

Tạo file:

```text
.gitignore/config.json
```

Nội dung:

```json
{
  "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY"
}
```

> Hoặc nếu dự án của bạn sử dụng nhiều API Key:

```json
{
  "GEMINI_API_KEYS": [
    "API_KEY_1",
    "API_KEY_2",
    "API_KEY_3"
  ]
}
```

### 4. Chạy ứng dụng

```bash
python app.py
```

hoặc

```bash
py app.py
```

Mở trình duyệt:

```text
http://127.0.0.1:5000
```

---

## 🌐 Triển khai Render

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
python app.py
```

### Environment Variables

```text
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

Sau khi deploy thành công:

```text
https://your-app.onrender.com
```

---

# 📂 Cấu trúc dự án

```text
ScamCheck
│
├── FrontEnd/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .gitignore/
│   └── config.json
│
├── app.py
├── requirements.txt
└── README.md
```

---

# 👥 Thành viên nhóm

| Họ và tên               | Mã học viên | Vai trò                                          |
| ----------------------- | ----------- | ------------------------------------------------ |
| **Nguyễn Tuấn Kiệt**    | FCT0623     | Leader, Làm slide, tài liệu, script thuyết trình |
| **Phạm Tuấn Kiệt**      | FCT0624     | Backend & AI Integration                         |
| **Vũ Trí Cường**        | FCT0607     | Backend & Frontend Development                   |
| **Hồ Nguyễn Hoàng Nam** | FCT0629     | Backend & Frontend Development                   |
| **Vương Minh Tuấn**     | FCT0648     | Soạn nội dung, chuẩn bị hình ảnh                 |

---

# 📄 Giấy phép

Dự án được phát triển nhằm phục vụ mục đích học tập và tham gia Hackathon FCT.

ScamCheck AI chỉ hỗ trợ đánh giá và cảnh báo nguy cơ, không thay thế kết luận của cơ quan chức năng hoặc tổ chức tài chính.
