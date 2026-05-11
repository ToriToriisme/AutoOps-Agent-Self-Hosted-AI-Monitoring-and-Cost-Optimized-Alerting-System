# Kiến trúc Frontend, Backend và Database trong dự án AutoOps

Đối với một dự án mang tính chất **DevOps / AI-driven Automation** như AutoOps Agent, khái niệm về Frontend, Backend và Database mang tính "thực dụng" và khác biệt nhiều so với các ứng dụng Web/App truyền thống. Thay vì xây dựng từ đầu (from scratch), dự án tận dụng tối đa hệ sinh thái mã nguồn mở.

Dưới đây là kiến trúc chi tiết cho 3 thành phần này:

## 1. Frontend (Giao diện người dùng & Tương tác)

Dự án không yêu cầu xây dựng một Frontend phức tạp (React, Vue, Angular), mà sử dụng các giải pháp có sẵn:

* **Grafana (UI Giám sát chính):** Được dùng để trực quan hóa toàn bộ hệ thống. Grafana hiển thị các metric của server, log quyết định của AI, chi phí token, và trạng thái của các Alert đang chờ xử lý. Đây là màn hình hiển thị chính của người quản trị.
* **ChatOps (Slack / Telegram Bot):** Đóng vai trò là giao diện tương tác (Interactive UI). Khi hệ thống ở chế độ "Human-in-the-loop" (cần con người phê duyệt), Agent gửi tin nhắn kèm các nút bấm `[Approve]` và `[Reject]` qua ứng dụng chat. Người dùng thao tác trực tiếp trên điện thoại/máy tính mà không cần đăng nhập vào hệ thống phức tạp.
* **Internal Admin UI (Tùy chọn):** Nếu cần giao diện để chỉnh sửa Prompt hoặc xem lịch sử hội thoại chi tiết, có thể sử dụng các framework Python siêu nhẹ như **Streamlit** hoặc **Gradio** để dựng UI nhanh chóng trong vài chục dòng code.

## 2. Backend (Bộ não AI & Điều phối)

Backend chính là cốt lõi của dự án - **AI Agent Service**.

* **Ngôn ngữ & Framework:** **Python** kết hợp với **FastAPI** (hoặc Flask). Python sở hữu hệ sinh thái AI mạnh mẽ nhất hiện nay (LangChain, LlamaIndex, AutoGen).
* **Nhiệm vụ của Backend:**
  1. **Webhook Receiver:** Mở API endpoint để nhận cảnh báo (alerts) đẩy từ Prometheus Alertmanager.
  2. **Orchestrator (Điều phối viên):** Giao tiếp với nhiều nguồn dữ liệu (Lấy metric từ Prometheus, lấy log từ server) để tổng hợp thành một bức tranh toàn cảnh (Context) trước khi gửi cho AI.
  3. **LLM Integration:** Gửi ngữ cảnh (Prompt) tới các API LLM (OpenAI, Anthropic, hoặc mô hình Local qua Ollama) để phân tích nguyên nhân sự cố.
  4. **Tool Execution:** Nhận quyết định từ AI và thực thi các lệnh thực tế (ví dụ: chạy kịch bản Bash, gọi API khởi động lại container Docker, giải phóng RAM).
* **Xử lý bất đồng bộ (Asynchronous):** Hệ thống cần xử lý hàng đợi (Queue - ví dụ Celery, Redis) để đảm bảo không bị quá tải khi xảy ra "Alert Storm" (bão cảnh báo), vì thời gian gọi LLM thường mất vài giây tới hàng chục giây.

## 3. Database (Cơ sở dữ liệu)

Không dùng một DB duy nhất, dự án sử dụng mô hình Polyglot Persistence (kết hợp nhiều loại DB) cho các mục đích chuyên biệt:

* **Time-Series Database (TSDB):** Sử dụng **Prometheus**. Đây là nơi lưu trữ dữ liệu dạng chuỗi thời gian (CPU, RAM, Network IO). AI không ghi dữ liệu vào đây mà chỉ *đọc* qua hệ thống truy vấn PromQL.
* **Vector Database:** Sử dụng **ChromaDB, Qdrant hoặc Milvus**. Thành phần này phục vụ cơ chế RAG (Retrieval-Augmented Generation). Nó lưu trữ dưới dạng vector (embeddings) các tài liệu như: sổ tay vận hành (Runbooks), lịch sử lỗi đã giải quyết, tài liệu kiến trúc. Khi có lỗi, Agent "search" trong Vector DB để tìm cách sửa tương tự trong quá khứ.
* **Relational/NoSQL Database:** Sử dụng **PostgreSQL, SQLite hoặc MongoDB** để lưu trữ trạng thái (State):
  * **Audit Logs:** Ghi lại mọi hành động AI đã thực thi (để truy vết và chịu trách nhiệm bảo mật).
  * **Cost & Token Tracking:** Ghi nhận số token tiêu thụ, chi phí API của mỗi lần giải quyết sự cố.
  * **Approval Queue:** Lưu trữ các Alert đang trong trạng thái chờ con người phê duyệt. Với dự án quy mô vừa và tự host, **SQLite** là lựa chọn tuyệt vời vì tính đơn giản, không cần thiết lập server riêng và vô cùng hiệu quả.
