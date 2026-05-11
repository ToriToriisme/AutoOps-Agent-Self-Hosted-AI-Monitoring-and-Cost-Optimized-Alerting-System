# SHIP (Đóng gói và Bàn giao)

Vì mục tiêu của bạn là hoàn thành sớm một MVP (Minimum Viable Product) tiết kiệm chi phí để báo cáo/thực tập, "Ship" là lúc bạn đóng gói và chứng minh kết quả.

## Đóng gói sản phẩm

Bạn gom toàn bộ Prometheus, Grafana, Backend FastAPI, và Database thành một khối thống nhất khởi chạy chỉ bằng một lệnh qua file `docker-compose.yml`.

## Hoàn tất Definition of Done (DoD)

Bạn rà soát lại các tiêu chí nghiệm thu để "Ship":

- ✅ Webhook từ Grafana bắn thành công.
- ✅ Luồng SMALL tự chạy tool và ghi kết quả.
- ✅ Luồng MEDIUM treo chờ duyệt (API Approve/Reject hoạt động).
- ✅ Luồng CRITICAL gửi thông báo khẩn qua Telegram/Email dưới 30 giây (đạt SLA).

## Bàn giao (Deliverables)

Bạn xuất bản các tài liệu đã viết (SRS, HLD, LLD), kịch bản demo (demo end-to-end), hướng dẫn cài đặt và mang ra trình bày trước hội đồng hoặc khách hàng. Đối với một dự án sinh viên, "Ship" chính là lúc bạn chứng minh hệ thống chạy khép kín thực tế và chi phí API AI đúng bằng 0đ (nhờ self-host Ollama).
