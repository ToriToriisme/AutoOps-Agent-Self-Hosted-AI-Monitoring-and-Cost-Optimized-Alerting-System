# KỊCH BẢN BẢO VỆ ĐỒ ÁN — 10 PHÚT

**AutoOps Agent — Self-Hosted AI Monitoring & Cost-Optimized Alerting System**

---

## PHẦN 1: TRÌNH BÀY SLIDE (~2 phút)

### Slide 1 — Mục tiêu & Chức năng (20s)

> *"Đề tài giải quyết bài toán vận hành IT truyền thống tốn thời gian và nhân lực. Em xây dựng AutoOps Agent – hệ thống tự giám sát, tự phân tích lỗi bằng AI và tự sửa lỗi khép kín."*

### Slide 2 — Kiến trúc hệ thống (25s)

> *"Prometheus thu thập metrics → Grafana phát hiện lỗi → Webhook bắn về FastAPI → FastAPI phản hồi 200 OK ngay lập tức rồi đẩy tác vụ AI xuống BackgroundTasks xử lý ngầm."*

### Slide 3 — AI RAG & An toàn (30s)

> *"AI tra cứu Playbook từ ChromaDB (RAG) để giảm ảo giác. Bảo mật 2 lớp: Human-in-the-loop qua Telegram cho lỗi MEDIUM, và Whitelist Circuit Breaker chặn mọi lệnh ngoài danh sách trắng."*

### Slide 4 — Kết quả (25s)

> *"Thời gian xử lý trung bình 4-5 giây, nhanh hơn 200 lần so với thủ công. Chi phí API chỉ ~1.5 USD/tháng nhờ dùng Gemini Flash Lite."*

### Slide 5 — Kết luận & Slogan (20s)

> *"Automate the predictable, solve the exceptional. Sau đây em xin trình bày phần Demo thực tế ạ."*

---

## PHẦN 2: GIỚI THIỆU DỰ ÁN & CÔNG NGHỆ (~1.5 phút)

*Mở VS Code hoặc Terminal, show cấu trúc cho giám khảo thấy tổng quan.*

### Bước 1: Giới thiệu công nghệ cốt lõi & Prometheus Targets

> *"Hệ thống sử dụng **Prometheus** làm cơ sở dữ liệu lưu trữ metrics theo dạng Pull-based. Trên giao diện Prometheus, khi truy cập vào **Status → Targets**, ta sẽ thấy trạng thái **UP (Healthy)** của `windows_exporter` — điều này chứng minh Prometheus đang kéo metrics thành công từ máy chủ Windows. Đồng thời, các cảnh báo được quản lý tập trung qua Alertmanager hoặc Grafana Alerting, tự động bắn Webhook về Backend. Ở Backend, Ollama/Gemini đóng vai trò AI Agent để phân tích và ra quyết định tự động."*

### Bước 2: Show cấu trúc thư mục

Gõ lệnh: `tree /F /A` hoặc chỉ trực tiếp trên VS Code Explorer.

> *"Dự án của em gồm 4 thư mục chính: agent\_api chứa Backend FastAPI, tools/powershell chứa script sửa lỗi, demo\_scripts chứa các kịch bản test, và observability chứa cấu hình Prometheus & Grafana."*

### Bước 3: Mở Grafana Dashboard (nếu đang chạy)

Mở trình duyệt: `http://localhost:3000`

> *"Đây là Dashboard giám sát Windows Server của em trên Grafana. Các biểu đồ hiển thị CPU, RAM, Disk Usage theo thời gian thực. Khi bất kỳ chỉ số nào vượt ngưỡng, Grafana sẽ tự động bắn Webhook cảnh báo về Backend API."*

### Bước 4: Show các file source code quan trọng

| File cần mở | Dòng cần chỉ | Nói gì |
|---|---|---|
| `agent_api/app/main.py` | Dòng 56-59 (`ALLOWED_TOOLS`) | "Đây là danh sách trắng Whitelist, chỉ cho phép 2 script chạy" |
| `agent_api/app/main.py` | Dòng 101-138 (`run_script`) | "Circuit Breaker: nếu tool không nằm trong Whitelist → từ chối ngay" |
| `agent_api/app/main.py` | Dòng 64-72 (`prompt_template`) | "Prompt Template ép AI trả JSON chuẩn, tuân thủ Playbook RAG" |
| `agent_api/app/main.py` | Dòng 439-484 (Phân nhánh SMALL/MEDIUM/CRITICAL) | "3 nhánh xử lý: SMALL tự sửa, MEDIUM chờ duyệt, CRITICAL chỉ cảnh báo" |
| `agent_api/.env` | Toàn bộ | "File cấu hình Secret, không đẩy lên GitHub nhờ .gitignore" |
| `tools/powershell/cleanup_temp_files.ps1` | Hàm `Is-AllowedPath` | "Script chỉ cho phép xóa file trong thư mục Temp an toàn" |

---

## PHẦN 3: LIVE DEMO (~3.5 phút)

*Chuẩn bị: Terminal Docker đang chạy + Terminal PowerShell để gõ lệnh + Telegram trên điện thoại.*

### Demo 1 — Lỗi SMALL — Tự động sửa (1 phút)

**Lệnh:** `powershell -ExecutionPolicy Bypass -File .\demo_scripts\demo_small_error.ps1`

> *"Em giả lập ổ đĩa C sắp đầy. Hệ thống nhận webhook, AI đánh giá SMALL, tự gọi script cleanup\_temp\_files dọn rác. Telegram nhận được báo cáo 'Tự động xử lý thành công' — không có nút bấm vì không cần duyệt."*

**Giải thích Source Code:**

- **Prompt cho script AI:** `main.py` (dòng 64-72) — biến `prompt_template`.
- **Hàm chạy Script:** `main.py` (dòng 101-138) — hàm `run_script`.
- **Phân nhánh SMALL:** `main.py` (dòng 439-470) — AI tự động chạy script.
- **Lưu Database:** `database.py` (dòng 122-160) — hàm `insert_agent_task`.

**Show:** Log Docker hiện `Severity: SMALL. Status: executed` + Telegram báo cáo không nút bấm.

### Demo 2 — Lỗi MEDIUM — Human-in-the-loop (1.5 phút)

**Lệnh:** `powershell -ExecutionPolicy Bypass -File .\demo_scripts\demo_medium_error.ps1`

> *"CPU quá tải. AI đề xuất restart service nhưng treo Pending chờ duyệt. Telegram hiện 2 nút Phê duyệt / Từ chối. Bây giờ em bấm Phê duyệt..."*

**Giải thích Source Code:**

- **Phân nhánh MEDIUM:** `main.py` (dòng 471-476) — Treo trạng thái 'pending' và gửi Telegram.
- **Webhook Telegram nhận duyệt:** `main.py` (dòng 554-631) — hàm `telegram_webhook`.
- **Cập nhật Database:** `database.py` (dòng 162-181) — hàm `update_agent_task_status`.

**Show:** Bấm Approve trên Telegram → nút biến mất → hiện kết quả thực thi.

> *"Sau khi em duyệt, Backend gọi editMessageText xóa nút bấm, tránh bấm nhầm lần 2. Đây là cơ chế chống Race Condition."*

### Demo 3 — Tấn công Hacker / Lỗi CRITICAL (1 phút)

**Lệnh:** `powershell -ExecutionPolicy Bypass -File .\demo_scripts\demo_hacker_injection.ps1`

> *"Hacker chèn lệnh rm -rf / vào payload Grafana. Quý thầy cô xem log Docker: lệnh bị Whitelist chặn đứng, không có script nào được thực thi. Hệ thống an toàn tuyệt đối."*

**Giải thích Source Code:**

- **Phân nhánh CRITICAL:** `main.py` (dòng 477-484) — Chỉ gửi báo động, không tự sửa.
- **Bảo vệ Whitelist:** `main.py` (dòng 106-107) — Chặn lệnh nếu không có trong ALLOWED\_TOOLS.
- **Ghi Audit Log:** `database.py` (dòng 197-256) — hàm `insert_audit_log` lưu bằng chứng.

**Show:** Log Docker hiện `ERROR: Tool 'rm -rf /' is not in ALLOWED_TOOLS whitelist`

---

## PHẦN 4: CÂU HỎI PHẢN BIỆN & TRẢ LỜI

### Nhóm 1: Câu hỏi về Nội dung Báo cáo

**Q: Tại sao chọn FastAPI mà không phải Flask hoặc Django?**

**Trả lời:** FastAPI hỗ trợ async ngay từ đầu và có sẵn `BackgroundTasks` để đẩy tác vụ nặng ra nền. Flask thiếu tính năng này. Django thì quá nặng cho một Webhook API đơn giản. FastAPI cũng tự sinh tài liệu API (Swagger) tại `/docs`.

---

**Q: Hệ thống tự giám sát (self-monitoring) của em cụ thể là giám sát những gì?**

**Trả lời:** Hệ thống tập trung giám sát 3 tầng của máy chủ Windows:

1. **Tài nguyên phần cứng (OS Metrics):** CPU load, RAM, dung lượng ổ đĩa (Disk C:), băng thông mạng thông qua `windows_exporter` thu thập gửi về Prometheus.
2. **Trạng thái các dịch vụ core (Service Health):** Cảnh báo khi các Service quan trọng (như Spooler, Docker, IIS) bị tắt hoặc treo.
3. **Log hệ thống (System Logs):** Lấy trực tiếp Windows Event Logs trong 15 phút gần nhất (dòng 141-182 trong `main.py`) để cung cấp cho AI làm ngữ cảnh chẩn đoán nguyên nhân gốc rễ.

---

**Q: RAG hoạt động như thế nào trong hệ thống?**

**Trả lời:** Khi có cảnh báo, Backend truy vấn ChromaDB bằng tiêu đề lỗi để tìm Playbook phù hợp nhất. Playbook được nhúng vào Prompt gửi cho Gemini, ép AI tuân theo quy trình nội bộ. Sau mỗi lần xử lý thành công, hệ thống tự nạp ngược bài học vào ChromaDB (Self-Learning RAG).

---

**Q: Prompt Injection là gì và hệ thống phòng thủ thế nào?**

**Trả lời:** Prompt Injection là kỹ thuật hacker chèn lệnh vào dữ liệu đầu vào để lừa AI. Em phòng thủ 2 lớp: (1) Prompt template ép AI chỉ trả JSON chuẩn; (2) Backend có `ALLOWED_TOOLS` Whitelist chặn cứng mọi lệnh không hợp lệ — kể cả khi AI bị lừa.

---

**Q: Em đánh giá điểm mạnh nhất và điểm yếu nhất của đồ án?**

**Trả lời:** **Điểm mạnh:** Kiến trúc phòng vệ 2 lớp (AI + Whitelist) đảm bảo an toàn tuyệt đối, RAG Self-Learning giúp AI tiến hóa liên tục. **Điểm yếu:** Hiện tại chỉ quản lý 1 máy chủ đơn lẻ, chưa hỗ trợ hạ tầng phân tán quy mô doanh nghiệp.

---

### Nhóm 2: Câu hỏi về `main.py`

**Q: Dòng 50-54 — Cấu hình AI model có ý nghĩa gì?**

**Trả lời:** Block `llm = ChatGoogleGenerativeAI(...)` khởi tạo kết nối tới Gemini 3.1 Flash Lite với `temperature=0.2`. Temperature thấp giúp AI ổn định nhưng vẫn giữ chút linh hoạt, không cứng nhắc như 0 tuyệt đối.

---

**Q: Dòng 56-59 — ALLOWED\_TOOLS là gì? Tại sao chỉ có 2 script?**

**Trả lời:** Đây là **danh sách trắng (Whitelist)**, chỉ cho phép 2 lệnh: `cleanup_temp_files` và `restart_service`. Mọi lệnh khác — kể cả do AI đề xuất — đều bị từ chối. Đây là lớp phòng vệ cứng nhất của hệ thống.

---

**Q: Dòng 64-72 — Prompt Template ép AI trả kết quả kiểu gì?**

**Trả lời:** Prompt ép AI phải trả JSON thuần với 3 key: `severity_assessment`, `root_cause_analysis`, `suggested_action`. Ràng buộc severity chỉ được SMALL/MEDIUM/CRITICAL, action phải nằm trong whitelist. Không được trả markdown hay giải thích thêm.

---

**Q: Dòng 74-79 — TRIAGE\_POLICY dùng để làm gì?**

**Trả lời:** Đây là bảng định tuyến O(1) tra cứu nhanh. Mỗi loại alert được gán sẵn severity cứng: `Windows Server Down → CRITICAL`, `CPU High → MEDIUM`, `C: Drive Low → SMALL`. Dùng kết hợp với AI để đảm bảo routing chính xác.

---

**Q: Dòng 101-138 — Hàm run\_script hoạt động thế nào?**

**Trả lời:** Đầu tiên kiểm tra **Circuit Breaker** (dòng 106-107): nếu tool không nằm trong ALLOWED\_TOOLS → từ chối ngay. Nếu hợp lệ, build command PowerShell, map tham số an toàn, chạy với timeout 15s. Trong Docker không có PowerShell sẽ trả kết quả giả lập (dòng 131-133).

---

**Q: Dòng 186-221 — Hàm query\_rag\_context làm gì?**

**Trả lời:** Truy vấn ChromaDB lấy Playbook phù hợp nhất với tiêu đề lỗi. Nếu ChromaDB chưa có dữ liệu, fallback sang quy tắc cứng: disk → SMALL, down → CRITICAL, còn lại → MEDIUM. Trả về cả nội dung Playbook và URN tham chiếu.

---

**Q: Dòng 226-333 — Hàm call\_llm\_triage phức tạp thế nào?**

**Trả lời:** Gọi Gemini phân loại lỗi. Bước 1: trích xuất mô tả từ payload. Bước 2: lấy Event Logs Windows. Bước 3: gọi LLM Chain. Bước 4: parse JSON bằng Pydantic. Bước 5: **Demo Safety Routing** (dòng 286-296) ép severity chính xác cho demo. Cuối cùng kiểm duyệt whitelist. Nếu mọi thứ fail → Fallback Rules (dòng 308-333).

---

**Q: Dòng 381-401 — learn\_from\_resolution là gì?**

**Trả lời:** Đây là cơ chế **Self-Learning RAG**. Sau mỗi lần xử lý sự cố thành công, hệ thống tự tạo document mới và upsert vào ChromaDB. Lần sau gặp lỗi tương tự, AI sẽ tìm được bài học này qua RAG.

---

**Q: Dòng 439-484 — Phân nhánh SMALL/MEDIUM/CRITICAL khác nhau thế nào?**

**Trả lời:** **SMALL (439-470):** Tự động chạy script + gửi Telegram báo cáo không có nút bấm. **MEDIUM (471-476):** Treo pending, gửi Telegram có 2 nút Approve/Reject. **CRITICAL (477-484):** Chỉ gửi cảnh báo khẩn cấp, không tự sửa.

---

**Q: Dòng 530-551 — Endpoint webhook nhận alert thế nào?**

**Trả lời:** Endpoint `POST /api/v1/alerts/webhook` nhận payload từ Grafana, ghi nhận thời gian T0, tạo Alert ID duy nhất, rồi đẩy toàn bộ xử lý vào `BackgroundTasks`. Phản hồi 200 OK ngay lập tức cho Grafana không bị timeout.

---

**Q: Dòng 554-631 — Webhook Telegram xử lý nút bấm ra sao?**

**Trả lời:** Nhận callback\_query khi Admin bấm Approve/Reject. Kiểm tra task có đang pending không (chống bấm 2 lần). Nếu Approve → gọi `run_script` thực thi. Sau đó gọi `editMessageText` xóa nút bấm cũ để tránh Race Condition.

---

### Nhóm 3: Câu hỏi về `database.py`

**Q: Dòng 29-48 — get\_db\_connection hỗ trợ bao nhiêu loại DB?**

**Trả lời:** Hỗ trợ 2 loại: **PostgreSQL** (cho production/cloud) và **SQLite** (cho local/demo). Biến `IS_POSTGRES` (dòng 24) tự phát hiện dựa trên biến môi trường `DATABASE_URL` hoặc `DB_HOST`.

---

**Q: Dòng 51-119 — init\_db tạo những bảng gì?**

**Trả lời:** Tạo 2 bảng: **agent\_tasks** (lưu thông tin task: severity, proposed\_action, status) và **audit\_logs** (lưu RAG context, decision reason, execution result, token count). Bảng audit\_logs có FK tới agent\_tasks.

---

**Q: Dòng 122-160 — insert\_agent\_task lưu gì vào DB?**

**Trả lời:** Lưu bản ghi task mới gồm: task\_id, alert\_title, labels (JSON), severity, proposed\_action, status, và timestamp. Hàm này được gọi ở dòng 430 trong main.py ngay khi bắt đầu xử lý alert.

---

**Q: Dòng 162-181 — update\_agent\_task\_status dùng ở đâu?**

**Trả lời:** Được gọi mỗi khi status thay đổi: từ `received → executed` (SMALL), `received → pending` (MEDIUM), `received → notified` (CRITICAL), hoặc `pending → executed/rejected` (sau khi Admin duyệt qua Telegram).

---

**Q: Dòng 183-194 — get\_agent\_task dùng khi nào?**

**Trả lời:** Dùng trong Telegram webhook (main.py dòng 577) để kiểm tra task có tồn tại không và status hiện tại có phải pending/notified không — tránh duyệt 2 lần (Race Condition).

---

**Q: Dòng 197-256 — insert\_audit\_log ghi nhận những gì?**

**Trả lời:** Ghi log đầy đủ: RAG context đã dùng, tham chiếu URN, lý do quyết định, kết quả thực thi, thời gian xử lý (ms), và **token tiêu thụ** (prompt\_tokens + completion\_tokens) để theo dõi chi phí LLM.

---

### Nhóm 4: Công nghệ & Thiết bị sử dụng

**Q: Tại sao chọn Gemini mà không phải GPT-4 hoặc Claude?**

**Trả lời:** Gemini 3.1 Flash Lite có giá API thấp nhất thị trường, tốc độ phản hồi nhanh nhất (SLA < 30s), đủ chính xác cho bài toán phân loại có RAG. GPT-4 đắt hơn 10-50 lần mà không vượt trội cho use case này.

---

**Q: Temperature = 0.2 nghĩa là gì? Sao không để 0?**

**Trả lời:** Temperature kiểm soát tính ngẫu nhiên của AI. 0.2 rất ổn định nhưng giữ chút linh hoạt. Để 0 tuyệt đối thì câu trả lời quá cứng nhắc, đôi khi lặp lại y hệt và mất suy luận ngữ cảnh.

---

**Q: Nếu API Google bị mất mạng thì hệ thống có chết không?**

**Trả lời:** Không. Em có **Fallback Rules** trong hàm `call_llm_triage` (main.py dòng 308-333). Khi API lỗi, hệ thống tự phân loại dựa trên từ khóa: disk → SMALL, down → CRITICAL, cpu → MEDIUM.

---

**Q: BackgroundTasks chạy trong bộ nhớ, server crash thì sao?**

**Trả lời:** Đây là hạn chế của MVP. Production sẽ nâng cấp lên **Celery + Redis** để đảm bảo Persistence kể cả khi server restart.

---

### Nhóm 5: Tối ưu & Mở rộng

**Q: Dự án có ứng dụng thực tế gì cho doanh nghiệp?**

**Trả lời:** Doanh nghiệp vừa và nhỏ không đủ ngân sách thuê kỹ sư trực 24/7. AutoOps thay thế với chi phí ~1.5 USD/tháng: giám sát liên tục, tự dọn rác, restart dịch vụ, cảnh báo khẩn qua Telegram.

---

**Q: Scale lên 50-100 máy chủ thì cần thay đổi gì?**

**Trả lời:** Thay PowerShell cục bộ bằng **Ansible** hoặc **Kubernetes API**. Tích hợp **Grafana Loki + Promtail** để gom log tập trung. Backend giữ nguyên kiến trúc, chỉ thay đổi lớp thực thi.

---

**Q: Làm sao tối ưu chi phí LLM thêm nữa?**

**Trả lời:** Em đã theo dõi token qua `prompt_tokens` và `completion_tokens` trong audit\_logs. Có thể tối ưu thêm bằng: (1) Cache RAG context tránh query lặp; (2) Dùng Ollama self-hosted thay API cloud; (3) Giảm prompt length bằng few-shot examples ngắn gọn.

---

*AutoOps Agent © 2026 — "Automate the predictable, solve the exceptional."*
