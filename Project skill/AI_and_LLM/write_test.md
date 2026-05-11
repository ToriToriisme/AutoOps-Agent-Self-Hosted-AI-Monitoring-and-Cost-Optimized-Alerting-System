# Skill write_test (Kỹ năng Viết kiểm thử)

Skill này áp dụng cho cả quá trình bạn phát triển dự án (Dev Workflow) lẫn kiểm thử chất lượng của chính con AI (Agent Evaluation).

## Đối với quy trình code (Bạn là Dev)

Bạn có thể đóng gói một workflow yêu cầu AI tự động viết các Test Case (bài kiểm thử) cho Backend FastAPI. Ví dụ: Viết test script để mô phỏng (simulate) việc Grafana bắn payload lỗi vào API `/api/v1/alerts/webhook`, hoặc viết unit test để chắc chắn rằng tính năng Circuit Breaker sẽ chặn đứng mọi Tool không nằm trong Whitelist.

## Đối với bản thân AI Agent (LLM Evaluation)

Giống như phần mềm truyền thống cần test, AI Agent cũng cần được đánh giá trước khi release. Các tài liệu chuyên sâu chỉ ra rằng bạn có thể dùng skill write_test để xây dựng một bộ công cụ đánh giá (như Ragas hoặc DeepEval).

## Workflow thực thi

Bạn cấp cho AI nguồn tài liệu hệ thống, skill write_test (Testset Generator) sẽ tự động sinh ra hàng loạt các mẫu câu hỏi kiểm thử (ví dụ: *"Mã truy cập bí mật là gì?"*, *"Lỗi 503 xử lý ra sao?"*) và tự tạo ra các câu trả lời tham chiếu (Reference Answers).

**Mục tiêu:** Giúp bạn tạo ra một bộ dataset kiểm thử (Testset) nhanh chóng. Sau đó, bạn cho con AI Agent của mình chạy qua bộ test này để đo lường các chỉ số như Faithfulness (Độ trung thực), Answer Relevancy (Độ liên quan), để xem nó phân loại lỗi (SMALL/MEDIUM/CRITICAL) có chuẩn xác không trước khi thực sự cắm vào hệ thống server.
