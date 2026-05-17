# Day 8 — Đóng gói Docker & Nâng cấp Bảo mật (Security & Dockerization)

## 1) Mục tiêu của Day 8
Sau khi đã có một "Bộ não" AI Agent hoạt động ổn định ở Day 6 & 7, hôm nay chúng ta sẽ đưa hệ thống lên một tầm cao mới về tính chuyên nghiệp và an toàn:
- **Dockerize:** Đóng gói toàn bộ AutoOps Agent vào Container để có thể triển khai ở bất cứ đâu (Local, VPS, Cloud) mà không lo lỗi môi trường (Dependency hell).
- **Security hardening:** Kích hoạt lớp bảo mật API Key để đảm bảo chỉ có Grafana của bạn mới có quyền gửi yêu cầu tới Agent, tránh việc bị kẻ xấu tấn công Webhook.

---

## 2) Tại sao phải làm bước này?
- **Tính di động:** Bạn có thể mang cả "Stack" giám sát này (Prometheus, Grafana, Agent) sang máy tính khác chỉ bằng 1 câu lệnh `docker-compose up`.
- **Bảo mật:** Webhook mặc định là một URL công khai (nếu bạn dùng ngrok hoặc mở port). Nếu không có API Key, bất kỳ ai cũng có thể gửi JSON giả mạo để lừa Agent chạy script xóa file hoặc gửi rác về Telegram của bạn.

---

## 3) Việc cần làm (Checklist)

### 3.1 Tạo Dockerfile cho AutoOps Agent
Trong thư mục `agent_api`, hãy tạo một file tên là `Dockerfile` (không có đuôi file) với nội dung sau:

```dockerfile
# Sử dụng Python bản nhẹ (slim) để giảm dung lượng image
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở port 8000 (port mặc định của FastAPI)
EXPOSE 8000

# Lệnh khởi chạy server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Cấu hình bảo mật API Key (Hardening)
Mở file `agent_api/app/main.py` và tìm hàm `verify_api_key`. Hãy hiện thực hóa nó để kiểm tra Key từ Header:

```python
# Trong agent_api/app/main.py

def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # Lấy API Key từ biến môi trường .env
    VALID_API_KEY = os.getenv("AGENT_API_KEY", "default_secret_key")
    
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized: Invalid or missing X-API-Key header"
        )
```

**Lưu ý:** Đừng quên thêm dòng `AGENT_API_KEY=your_secret_key_here` vào file `.env` của bạn.

### 3.3 Cấu hình Grafana để gửi kèm API Key
1. Quay lại **Grafana -> Alerting -> Contact Points**.
2. Chọn Webhook của AutoOps Agent.
3. Tìm phần **HTTP Header** (hoặc Custom Headers).
4. Thêm một Header mới:
   - Key: `X-API-Key`
   - Value: `your_secret_key_here` (trùng với key trong file .env).
5. Bấm **Test** để kiểm tra xem Agent có còn nhận được dữ liệu không.

### 3.4 Cấu hình Docker Compose (Tùy chọn nâng cao)
Nếu bạn muốn chạy Agent chung với Prometheus/Grafana trong cùng một mạng Docker, hãy thêm service này vào file `docker-compose.yml` gốc của dự án:

```yaml
  autoops-agent:
    build: ./agent_api
    container_name: autoops-agent
    ports:
      - "8000:8000"
    env_file:
      - ./agent_api/.env
    volumes:
      - ./agent_api/storage:/app/storage
    restart: always
```

---

## 4) Kiểm tra và Nghiệm thu (Definition of Done - DoD)
- [ ] Build thành công Docker image bằng lệnh: `docker build -t autoops-agent ./agent_api`.
- [ ] Chạy được container và truy cập được vào `http://localhost:8000/health`.
- [ ] Khi gửi request Webhook **không kèm** `X-API-Key`, Server phải trả về lỗi `403 Forbidden`.
- [ ] Khi gửi request Webhook **có kèm** `X-API-Key` đúng, Server xử lý bình thường và AI Agent phản hồi thành công.
- [ ] Log của Docker (dùng `docker logs -f autoops-agent`) hiển thị quá trình nhận Alert và AI phân tích mượt mà.

---

## 5) Timebox gợi ý (Tổng cộng khoảng 1.5 - 2 tiếng)
- **30 phút:** Viết Dockerfile và build image lần đầu (có thể mất thời gian tải base image).
- **30 phút:** Hiện thực logic verify API Key trong Python.
- **30 phút:** Cấu hình lại Header trên Grafana và test luồng bảo mật.
- **30 phút:** Xử lý lỗi (nếu có) liên quan đến đường dẫn file (Path) khi chạy trong Docker (Lưu ý: Docker dùng Linux, nên các lệnh PowerShell có thể cần điều chỉnh hoặc chạy qua cơ chế SSH/Remote nếu muốn tác động lên Host Windows).

---
**Ghi chú cho các bước tiếp theo:** 
Ngày mai (Day 9), chúng ta sẽ tập trung vào việc **Làm sạch dữ liệu (Data Cleaning)** và **Tối ưu Prompt (Prompt Engineering)** để AI trả lời thông minh hơn, chuyên nghiệp hơn và ít tốn Token hơn!
