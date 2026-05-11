# Skill AI-lookup (Kỹ năng Tra cứu có cấu trúc)

Trong dự án của bạn, AI-lookup không gì khác chính là công cụ RAG (Retrieval-Augmented Generation) mà hệ thống đang sử dụng làm lõi trung tâm.

## Cách thức hoạt động

Thay vì để LLM tự do "đoán" cách sửa lỗi server (dễ dẫn đến hiện tượng ảo giác - hallucination), skill AI-lookup sẽ biến AI Agent thành một "chuyên viên tra cứu tài liệu SRE". Khi nhận được một webhook từ Grafana (ví dụ: CPU > 90%), AI sẽ không trả lời ngay. Nó sẽ kích hoạt AI-lookup để tìm kiếm trong Vector Database (ChromaDB) nhằm lấy ra các SOP (Standard Operating Procedure) hoặc Playbook tương ứng với lỗi đó.

## Ví dụ trong Project của bạn

- **Input:** Cảnh báo Container `backend-api` bị DOWN.
- **AI-lookup thực thi:** AI tự động lục tìm tài liệu nội bộ, tìm thấy quy định: *"Nếu là container Core (DB, API) bị DOWN thì phân loại là CRITICAL và hú báo động. Nếu là container phụ thì phân loại MEDIUM."*
- **Output:** Quyết định Triage chính xác, nhất quán thay vì tự ý gọi lệnh restart lung tung. AI-lookup đóng vai trò là quá trình "Grounding" (neo thông tin vào sự thật) để đảm bảo độ tin cậy tuyệt đối.
