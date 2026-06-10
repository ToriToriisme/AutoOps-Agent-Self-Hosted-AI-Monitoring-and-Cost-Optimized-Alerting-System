# Hướng dẫn chi tiết Triển khai AutoOps Agent lên Google Cloud Run (Serverless)

**Google Cloud Run** là dịch vụ serverless cho phép bạn chạy các ứng dụng được đóng gói trong container (Docker) mà không cần tự quản lý máy chủ. Khi không có cảnh báo (Webhook) gửi đến, Cloud Run có thể tự động hạ số lượng container xuống **0** để tối ưu hóa chi phí (gần như bằng 0 khi không chạy).

Dưới đây là tài liệu chi tiết hướng dẫn từ khâu chuẩn bị mã nguồn, cấu hình lưu trữ, đóng gói Docker và deploy lên Cloud Run.

---

## 1. Bản chất của Cloud Run & Cách xử lý cho dự án AutoOps Agent

Cloud Run hoạt động theo cơ chế **Stateless (Không lưu trạng thái)**:
1. **Container có thể bị khởi động lại hoặc tắt đi bất kỳ lúc nào.**
2. **Dữ liệu SQLite (`storage/agent.db`) và ChromaDB (`storage/chroma_db`) lưu trên ổ đĩa cục bộ của container sẽ bị mất sạch** khi container tắt đi.
3. **Môi trường chạy là Linux**, do đó không thể thực thi trực tiếp file PowerShell `.ps1` cục bộ để can thiệp vào máy chủ Windows khác.

### 💡 Các giải pháp khắc phục:

#### Giải pháp A: Gắn Cloud Storage Bucket làm ổ đĩa ảo (Cloud Storage Volume Mounts) - *Dễ nhất*
GCP hiện đã hỗ trợ gắn trực tiếp một Cloud Storage Bucket vào một đường dẫn bên trong container Cloud Run (sử dụng công nghệ Cloud Storage FUSE ngầm).
* **Ứng dụng:** Ta sẽ gắn Bucket vào thư mục `/app/storage` của container. SQLite và ChromaDB sẽ đọc/ghi trực tiếp lên Bucket này, giúp giữ lại dữ liệu khi container khởi động lại.
* **Lưu ý:** Vì SQLite ghi file và khóa file (file locking), tốc độ đọc/ghi qua mạng có thể chậm hơn ổ cứng thường, nhưng hoàn toàn chấp nhận được cho quy mô nhỏ (MVP).

#### Giải pháp B: Điều chỉnh cổng chạy (Port)
Mặc định `Dockerfile` của bạn đang expose port `8000`. Khi deploy lên Cloud Run, ta có 2 cách:
* Sử dụng tham số `--port=8000` khi chạy lệnh deploy (Cloud Run sẽ tự chuyển tiếp traffic từ cổng mặc định 8080/443 của nó vào cổng 8000 của container).
* Hoặc cập nhật Dockerfile để đọc biến môi trường `$PORT` do Cloud Run truyền vào.

---

## 2. Các bước triển khai qua dòng lệnh (gcloud CLI)

### Bước 1: Chuẩn bị môi trường GCP & gcloud CLI
1. Tải và cài đặt [Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
2. Mở terminal và đăng nhập vào tài khoản Google Cloud của bạn:
   ```bash
   gcloud auth login
   ```
3. Thiết lập dự án mặc định của bạn (thay `[PROJECT_ID]` bằng ID dự án GCP của bạn):
   ```bash
   gcloud config set project [PROJECT_ID]
   ```
4. Kích hoạt các API cần thiết:
   ```bash
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com storage.googleapis.com
   ```

---

### Bước 2: Tạo Google Cloud Storage Bucket để lưu Database
Để lưu SQLite và ChromaDB bền vững, chúng ta tạo một Cloud Storage bucket và cấu hình để gắn vào container.
1. Tạo Bucket (chọn region trùng với region định chạy Cloud Run, ví dụ `asia-southeast1` ở Singapore):
   ```bash
   gcloud storage buckets create gs://autoops-storage-bucket --location=asia-southeast1
   ```

---

### Bước 3: Tạo Registry và Push Docker Image lên GCP
Chúng ta cần đóng gói API Backend thành Docker Image và tải lên dịch vụ **Artifact Registry** của GCP.

1. Tạo một repository trên Artifact Registry:
   ```bash
   gcloud artifacts repositories create autoops-repo \
       --repository-format=docker \
       --location=asia-southeast1 \
       --description="Repository chua docker image cho AutoOps Agent"
   ```
2. Cấu hình Docker xác thực với registry của GCP:
   ```bash
   gcloud auth configure-docker asia-southeast1-docker.pkg.dev
   ```
3. Build Docker Image (Chạy lệnh này tại thư mục `agent_api`):
   ```bash
   # Build cho nền tảng Linux amd64 để đảm bảo chạy được trên Cloud Run (nhất là khi bạn đang dùng máy Mac chip M1/M2/M3)
   docker build --platform linux/amd64 -t asia-southeast1-docker.pkg.dev/[PROJECT_ID]/autoops-repo/autoops-agent:latest .
   ```
4. Push image lên Cloud:
   ```bash
   docker push asia-southeast1-docker.pkg.dev/[PROJECT_ID]/autoops-repo/autoops-agent:latest
   ```

---

### Bước 4: Deploy lên Cloud Run & Gắn ổ đĩa ảo (Volume Mount)
Chúng ta sẽ triển khai container vừa đẩy lên, cấu hình biến môi trường và gắn ổ đĩa chứa DB.

Chạy lệnh deploy (thay thế `[PROJECT_ID]` bằng ID dự án thực tế của bạn):
```bash
gcloud run deploy autoops-agent \
    --image=asia-southeast1-docker.pkg.dev/[PROJECT_ID]/autoops-repo/autoops-agent:latest \
    --platform=managed \
    --region=asia-southeast1 \
    --allow-unauthenticated \
    --port=8000 \
    --set-env-vars="GOOGLE_API_KEY=your_gemini_api_key,AGENT_API_KEY=your_secure_agent_key,TELEGRAM_BOT_TOKEN=your_bot_token,TELEGRAM_CHAT_ID=your_chat_id" \
    --add-volume=name=db-volume,type=cloud-storage,bucket=autoops-storage-bucket \
    --add-volume-mount=volume=db-volume,mount-path=/app/storage
```

**Giải thích các tham số quan trọng:**
* `--allow-unauthenticated`: Cho phép truy cập công khai (để Grafana bên ngoài có thể bắn webhook vào). Hệ thống của chúng ta đã được bảo vệ bằng lớp trung gian `verify_api_key` với header `X-API-Key` nên cực kỳ an toàn.
* `--port=8000`: Bảo Cloud Run chuyển hướng traffic vào port `8000` (port mặc định của FastAPI).
* `--add-volume` và `--add-volume-mount`: Gắn trực tiếp Google Cloud Storage Bucket `autoops-storage-bucket` vào thư mục `/app/storage` của Container. Nhờ vậy, file `agent.db` và vector DB `chroma_db` sẽ được ghi đè trực tiếp lên Cloud Storage mà không lo bị mất.

Sau khi lệnh chạy hoàn tất, bạn sẽ nhận được một **Service URL** dạng:
`https://autoops-agent-xxxxxxx-as.a.run.app`

---

## 3. Cấu hình Grafana gửi tín hiệu đến Cloud Run

1. Vào dashboard **Grafana** của bạn.
2. Chọn **Alerting** -> **Contact Points**.
3. Sửa Contact Point webhook hiện tại của bạn:
   - **URL**: `https://autoops-agent-xxxxxxx-as.a.run.app/api/v1/alerts/webhook`
   - **HTTP Method**: `POST`
4. Ở phần **HTTP Headers** (Custom Headers), hãy thêm:
   - **Key**: `X-API-Key`
   - **Value**: `your_secure_agent_key` (phải trùng khớp với giá trị `AGENT_API_KEY` bạn đã truyền vào biến môi trường ở Bước 4).
5. Bấm **Test** để xác nhận tín hiệu bắn lên Cloud Run trả về mã trạng thái `200 OK` thành công.

---

## 4. Cách theo dõi Log và Quản lý trên GCP Console

* **Xem Logs vận hành của AI Agent:** 
  Vào GCP Console -> **Cloud Run** -> Chọn dịch vụ `autoops-agent` -> Chọn tab **LOGS**. Tại đây bạn sẽ thấy toàn bộ quá trình nhận webhook, log gọi Gemini AI phân tích triage, và các hoạt động của luồng chạy ngầm.
* **Theo dõi hiệu năng và chi phí:**
  Tab **METRICS** trong Cloud Run sẽ hiển thị biểu đồ CPU, RAM tiêu thụ, và số lượng container đang hoạt động (có những lúc sẽ tự động đưa về 0 container để tiết kiệm tiền cho bạn).
* **Chỉnh sửa cấu hình nhanh:**
  If muốn cập nhật API Key hoặc đổi biến môi trường mà không muốn chạy lại lệnh CLI, bạn có thể click nút **Edit & Deploy New Revision** ở góc trên màn hình dịch vụ Cloud Run trong giao diện web Console của GCP.
