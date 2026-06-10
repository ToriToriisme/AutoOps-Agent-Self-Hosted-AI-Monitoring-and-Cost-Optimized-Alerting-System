4.3 Thực nghiệm thống kê token tiêu thụ và chi phí vận hành API
Trình bày dữ liệu bóc tách từ bảng `audit_logs` về lượng Prompt Tokens và Completion Tokens tiêu thụ cho mỗi cuộc gọi AI. Tính toán chi phí thực tế dựa trên bảng giá API của Google Gemini 3.1 Flash Lite.

Chương 5: Kết Luận và Hướng Phát Triển
Định biên trang: 3 - 5 trang. Tổng kết lại toàn bộ đóng góp và hạn chế của đề tài.

5.1 Các kết quả nghiên cứu và thực nghiệm đạt được
Tóm tắt các đóng góp lớn của dự án: Xây dựng thành công hệ thống giám sát tự phục hồi khép kín (Closed-loop AIOps); Tích hợp RAG để giảm thiểu ảo giác của AI; Đảm bảo an toàn tuyệt đối nhờ cơ chế kiểm tra whitelist cứng tại backend và phê duyệt qua Telegram.

5.2 Những hạn chế kỹ thuật hiện tại
Thừa nhận trung thực các điểm yếu của phiên bản MVP hiện tại:

1. Hệ thống chạy script PowerShell cục bộ nên mới chỉ áp dụng được trên một server đơn lẻ, chưa hỗ trợ hạ tầng phân tán.
2. Chưa tích hợp hệ thống gom log tập trung nên việc đọc Event Log còn thủ công qua PowerShell command cục bộ.

5.3 Hướng mở rộng và phát triển tương lai
Đề xuất giải pháp nâng cấp hệ thống:

1. Tích hợp giải pháp gom log tập trung như Grafana Loki kết hợp Promtail để AI Agent có thể truy vấn log của bất kỳ node nào trong hệ thống thông qua API tập trung.
2. Nâng cấp bộ máy thực thi script từ PowerShell cục bộ sang các công cụ quản lý cấu hình tập trung như Ansible / Kubernetes API để điều khiển hạ tầng quy mô lớn.
3. Sử dụng lịch sử audit logs tốt nhất để xây dựng bộ dữ liệu Few-shot Prompting chất lượng cao giúp AI ngày càng thông minh.

sau khi kết thúc chương 5 hãy viết tất cả tài liệu tham khảo cho tôi , kèm theo 1 danh mục từ viết tắt.
