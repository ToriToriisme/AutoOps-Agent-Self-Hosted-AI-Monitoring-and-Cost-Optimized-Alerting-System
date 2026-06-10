# Log Learning and Auto-Remediation Flow

## 1. Mục Đích
Luồng này đảm bảo hệ thống không chỉ xử lý sự cố một cách thụ động theo các quy tắc cố định, mà còn có khả năng **học hỏi từ dữ liệu log lịch sử** (Event Logs, Grafana Alerts) và **kết quả của các lần xử lý trước đó**. Qua đó, AI Agent có thể đưa ra các hành động tự phục hồi (Auto-remediation) chính xác và tối ưu hơn trong tương lai.

## 2. Các Bước Thực Hiện (Workflow)

### Bước 1: Thu thập và Làm giàu dữ liệu (Data Ingestion & Enrichment)
- Khi nhận được một cảnh báo (Alert) từ Grafana, hệ thống không xử lý ngay lập tức.
- AutoOps Agent tự động kích hoạt tiến trình thu thập **Windows Event Logs** (thông qua PowerShell) liên quan đến sự cố trong khung thời gian gần nhất (ví dụ: 15 phút qua).
- Kết hợp dữ liệu Grafana và Event Logs để tạo thành một Context đầy đủ nhất về sự cố.

### Bước 2: Phân tích ngữ cảnh với RAG (Contextual Analysis)
- Đưa Context thu thập được truy vấn vào **Vector Database (ChromaDB)**.
- Hệ thống tìm kiếm các "Playbook" chuẩn hoặc các "Sự cố tương tự" đã từng xảy ra trong quá khứ.
- Trích xuất thông tin về hành động (Action) nào đã được sử dụng trước đây và kết quả của hành động đó (Thành công hay Thất bại).

### Bước 3: Đưa ra Quyết định (AI Decision Making)
- LLM (Gemini) phân tích Context + RAG data để đưa ra quyết định:
  - **Độ tự tin cao (High Confidence) - Mức độ SMALL:** Lỗi đã từng xuất hiện và có script khắc phục chuẩn (ví dụ: dọn ổ cứng, restart service an toàn). Hệ thống **tự động chạy script** (Auto-remediation) từ Whitelist.
  - **Độ tự tin thấp / Sự cố phức tạp - Mức độ MEDIUM hoặc CRITICAL:** LLM không chắc chắn hoặc sự cố đòi hỏi can thiệp sâu. Hệ thống không tự động sửa mà chuyển sang luồng **Approval Flow** hoặc gửi Cảnh báo khẩn cấp.

### Bước 4: Học hỏi liên tục (Knowledge Update)
- Bất kể sự cố được giải quyết tự động (Auto) hay thủ công bởi Admin (Manual), sau khi đóng Task, kết quả (Resolution) sẽ được tổng hợp.
- Kết quả này được chuyển đổi thành Embedding và **cập nhật lại vào ChromaDB**.
- **Kết quả:** Ở lần gặp sự cố tương tự tiếp theo, AI sẽ có thêm dữ liệu thực tế để tự tin hơn trong việc đưa ra quyết định tự động.
