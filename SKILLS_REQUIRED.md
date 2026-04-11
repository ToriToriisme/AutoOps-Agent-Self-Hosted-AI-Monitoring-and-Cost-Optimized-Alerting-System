# Danh sách Kỹ năng cần thiết (Skills Required)

Để xây dựng thành công dự án **Self-Hosted AI Agent Monitor System**, một Kỹ sư Hệ thống / Kỹ sư AI cần trang bị sự kết hợp giữa kiến thức Vận hành hệ thống (DevOps/SRE) và Trí tuệ nhân tạo (AI/LLM). Dưới đây là danh sách chi tiết:

## 1. Kỹ năng Hệ thống & DevOps (Infrastructure & Ops)
* **Linux Server Administration:** Nắm vững dòng lệnh Linux, quản lý tiến trình, phân quyền file, hệ thống mạng cơ bản.
* **Docker & Containerization:** 
  * Cách viết `Dockerfile` và `docker-compose.yml`.
  * Quản lý vòng đời Container, Volumes, Networks nội bộ.
* **Monitoring & Observability:**
  * **Prometheus:** Hiểu kiến trúc Pull-based, viết câu lệnh truy vấn thời gian thực bằng `PromQL`.
  * **Exporters:** Biết cách gắn `node_exporter` (bắt CPU, RAM, Disk) và `cAdvisor` (bắt thông số Docker).
  * **Grafana:** Kỹ năng trực quan hóa dữ liệu, import template và vẽ biểu đồ.

## 2. Kỹ năng Trí tuệ nhân tạo (AI & LLM Integration)
* **Self-hosting LLM:** Biết cách triển khai các mô hình AI mã nguồn mở (như Llama 3, Mistral) cục bộ trên máy chủ sử dụng Ollama, vLLM hoặc Hugging Face.
* **Prompt Engineering:** Kỹ năng ra lệnh cho AI (System prompt) định hình AI đóng vai trò làm chuyên gia SRE, ràng buộc điều kiện khắt khe để chống ảo giác (hallucination).
* **Function Calling / Tool Use:** Lập trình để kết nối đầu ra văn bản của AI thành các hành động kỹ thuật thực tế (Ví dụ: biến output JSON của AI thành lệnh `docker restart`).
* **RAG (Retrieval-Augmented Generation):**
  * Biết cách nhúng (Embedding) văn bản.
  * Thao tác với Vector Database (Milvus, Qdrant, ChromaDB...) để lưu trữ lịch sử lỗi và Playbook.

## 3. Kỹ năng Lập trình (Programming)
* **Python (Ngôn ngữ chính):**
  * Xây dựng API và Webhook (bằng FastAPI hoặc Flask) để nhận cảnh báo từ Prometheus Alertmanager.
  * Sử dụng các framework AI (như LangChain, LlamaIndex hoặc CrewAI) để tạo tác nhân tự động.
* **Bash Scripting:** Viết các đoạn mã tự động hóa trên server để AI gọi khi cần (VD: script giải phóng dung lượng ổ đĩa).
* **Xử lý JSON & YAML:** Đọc, trích xuất và biến đổi định dạng dữ liệu, đặc biệt là parsing các *intermediate_steps* (bước trung gian) để đếm token.

## 4. Kỹ năng Phân tích & Tư duy hệ thống (System Design)
* **Tư duy Kiến trúc:** Hiểu về sự khác biệt giữa Centralized và Microservices, kiến trúc tự trị Closed-loop AIOps.
* **Bảo mật (Security):** Hiểu nguyên tắc "Đặc quyền tối thiểu" (Principle of Least Privilege) - cấp cho AI quyền hạn sửa lỗi nhưng không có quyền phá hoại hệ thống.