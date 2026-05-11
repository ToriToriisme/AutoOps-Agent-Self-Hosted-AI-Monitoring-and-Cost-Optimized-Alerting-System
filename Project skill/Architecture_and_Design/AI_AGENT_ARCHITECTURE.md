# AI Agent Architecture

Tài liệu này mô tả chi tiết kiến trúc tổng thể của hệ thống AutoOps Agent.

## Các công cụ sử dụng (Tools & Technologies)

- **AI & LLM:** OpenAI API, Anthropic, hoặc Local LLMs (Ollama)
- **Vector Database:** ChromaDB, Qdrant, hoặc Milvus (lưu trữ RAG context)
- **Framework AI:** LangChain, LlamaIndex, hoặc AutoGen
- **Monitoring & Alerting:** Prometheus, Grafana, Alertmanager
- **Observability LLM:** Langfuse, Helicone (theo dõi token, chi phí, độ trễ)
- **Infrastructure:** Docker, Docker Compose
- **Ngôn ngữ lập trình:** Python (cho Agent), YAML (cho Cấu hình)

---

## 1. Architecture Goals (Mục tiêu Kiến trúc)

- **Tự động hóa toàn diện (Automated Remediation):** Giảm thiểu sự can thiệp của con người bằng cách để AI tự động phân tích alert và thực hiện hành động khắc phục (tool calling).
- **Tối ưu chi phí (Cost-Optimized):** Theo dõi sát sao và có chiến lược giới hạn chi phí gọi API của LLM (ví dụ: bộ nhớ đệm, định tuyến thông minh giữa các model).
- **Self-Hosted & Bảo mật:** Có khả năng triển khai toàn bộ on-premise (bao gồm cả local LLM nếu cần) để đảm bảo dữ liệu log/metrics không bị lộ ra ngoài.
- **Khả năng quan sát cao (High Observability):** Không chỉ giám sát hệ thống server mà còn giám sát chính bản thân AI Agent (thời gian phản hồi, tỉ lệ lỗi, chất lượng quyết định).
- **Dễ dàng mở rộng (Extensibility):** Dễ dàng thêm các tool mới (plugin) hoặc thay đổi Vector DB, LLM provider mà không làm phá vỡ hệ thống.

---

## 2. Architecture Styles (Phong cách Kiến trúc)

- **Event-Driven Architecture (Kiến trúc hướng sự kiện):** Hệ thống hoạt động dựa trên các sự kiện (alerts) được đẩy từ Prometheus/Alertmanager qua Webhook.
- **Microservices:** Các thành phần (Prometheus, Grafana, Vector DB, AI Agent Service) được tách biệt, đóng gói trong các container Docker độc lập.
- **RAG-based AI (Retrieval-Augmented Generation):** AI Agent không chỉ dựa vào kiến thức nền tảng mà còn liên tục truy xuất dữ liệu từ Vector DB (lịch sử sự cố, runbooks) để đưa ra quyết định chính xác.

---

## 3. Folder Structure (Cấu trúc Thư mục)

Dưới đây là kiến trúc thư mục chuẩn cho dự án AutoOps Agent:

```text
/
├── .github/                   # CI/CD workflows, GitHub actions
├── agent/                     # Source code chính của AI Agent
│   ├── core/                  # Xử lý LLM, prompt templates, router logic
│   ├── tools/                 # Các function/tool cho Agent (ví dụ: restart docker, clear cache)
│   ├── memory/                # Quản lý ngữ cảnh và kết nối Vector DB
│   └── main.py                # Điểm vào (Entry point) của Agent API (FastAPI/Flask)
├── observability/             # Cấu hình giám sát hệ thống
│   ├── prometheus/            # File cấu hình và rules của Prometheus
│   ├── grafana/               # Dashboards và datasources của Grafana
│   └── docker-compose.yml     # Chạy toàn bộ stack observability
├── vector_db/                 # Cấu hình và volume data cho Vector DB
├── docs/                      # Tài liệu dự án (bao gồm thư mục Project skill)
└── scripts/                   # Các script hỗ trợ deploy, backup, testing

```

---

## 4. Component Diagram & Data Flow (Luồng dữ liệu & Thành phần)

Luồng xử lý cốt lõi của bộ não AI Agent:

1. **Trigger (Khởi tạo):** Alertmanager phát hiện bất thường và gửi Webhook chứa JSON payload tới API của AI Agent.
2. **Context Enrichment (Làm giàu dữ liệu):** Agent tự động truy vấn thêm log trong 15 phút gần nhất và tìm kiếm các sự cố tương tự trong Vector DB (RAG).
3. **Decision Engine (Động cơ ra quyết định):** LLM tổng hợp thông tin, sử dụng Prompt Engineering tối ưu để phân tích nguyên nhân gốc rễ (Root Cause Analysis).
4. **Action Router (Bộ định tuyến hành động):**
   - *Luồng 1 (Low/Auto-fix):* Sự cố đã biết rõ ràng -> Agent gọi trực tiếp Tool (ví dụ gọi script bash) để xử lý.
   - *Luồng 2 (Medium/Pending):* Cần xác nhận -> Ghi log vào DB, hiển thị trạng thái "Pending Approval" lên Grafana.
   - *Luồng 3 (Critical/Escalation):* Vượt quá khả năng -> Gửi ngay Webhook khẩn cấp đa kênh (Slack, Telegram, PagerDuty).

---

## 5. Security & Cost Controls (Bảo mật & Quản lý Chi phí)

- **Secret Management:** Mọi API Key (OpenAI, Anthropic), mật khẩu DB đều lưu qua biến môi trường (`.env`) hoặc Secret Manager, tuyệt đối không hardcode.
- **Authentication:** API webhook của AI Agent được bảo vệ bằng Token tĩnh hoặc HMAC signature để tránh bị trigger giả mạo.
- **Circuit Breaker cho LLM:** Nếu hệ thống bị "Alert Storm" (bão cảnh báo liên tục), Agent sẽ tự động gộp (group) các alert hoặc tạm ngưng gọi LLM để tránh chi phí tăng đột biến (Billing limits).
- **Audit Logging:** Mọi hành động (Tool Calls) mà Agent thực hiện (ví dụ: chạy lệnh xóa file, restart service) đều phải được lưu trữ vĩnh viễn (Audit trail) để con người có thể truy vết khi có lỗi do AI gây ra.
