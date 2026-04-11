# Cẩm nang Xử lý Sự cố

- **Lỗi: Prometheus không cào được dữ liệu.** -> *Giải pháp:* Kiểm tra port 9100 (Node exporter) hoặc 8080 (cAdvisor) có bị tường lửa chặn không.
- **Lỗi: AI phản hồi quá chậm.** -> *Giải pháp:* Kiểm tra VRAM của GPU, đổi sang mô hình LLM nhỏ hơn (Vd: từ 8B xuống 4B/3B), tối ưu lại Context prompt.
- **Lỗi: AI bịa ra tool ảo.** -> *Giải pháp:* Xem lại file `PROMPT_ENGINEERING.md`, dùng Circuit Breaker để ngắt luồng.
