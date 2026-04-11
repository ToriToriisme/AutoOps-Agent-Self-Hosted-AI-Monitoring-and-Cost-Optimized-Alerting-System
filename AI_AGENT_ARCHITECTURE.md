# Kiến trúc Bộ não AI Agent

1. **Trigger:** Nhận JSON payload từ Alertmanager.
2. **Context Enrichment:** Kéo logs 15 phút gần nhất + Truy vấn Vector DB.
3. **Decision Engine:** LLM xử lý Prompt.
4. **Router (Bộ định tuyến):**
   - Luồng 1 (Small): Gọi trực tiếp Tool.
   - Luồng 2 (Medium): Ghi DB trạng thái Pending, báo lên Grafana.
   - Luồng 3 (Critical): Gửi Webhook khẩn cấp đa kênh.
