# CATCHUP (Nắm tình hình / Cập nhật trạng thái)

Trong dự án của bạn, "Catchup" mang hai ý nghĩa: một là cho bạn (Dev/Admin) và hai là cho con AI Agent.

## Đối với bạn (Dev/Admin)

- Mở **Grafana Dashboard** để xem trạng thái hiện tại của các máy chủ và Docker container (CPU, RAM, Disk).
- Kiểm tra cơ sở dữ liệu (bảng `agent_tasks`) xem có cảnh báo lỗi mức MEDIUM nào đang bị treo ở trạng thái pending chờ bạn phê duyệt hay không.
- Đọc `audit_logs` để "catchup" xem đêm qua AI Agent đã đưa ra những quyết định gì, gọi tool nào, có bị ảo giác (hallucination) không và tốn bao nhiêu token.

## Đối với AI Agent (Bước Enrich & Retrieval)

Ngay khi nhận được Webhook từ Grafana, AI Agent cũng phải "catchup" tình hình bằng cách: Đọc log lỗi → Kích hoạt công cụ RAG để truy vấn Vector Database tìm các quy trình xử lý (Playbooks) hoặc lịch sử lỗi tương tự trước khi đưa ra quyết định phân loại (Triage).
