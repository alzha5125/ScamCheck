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

### 4. Chạy ứng dụng

```bash
python app.py
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
