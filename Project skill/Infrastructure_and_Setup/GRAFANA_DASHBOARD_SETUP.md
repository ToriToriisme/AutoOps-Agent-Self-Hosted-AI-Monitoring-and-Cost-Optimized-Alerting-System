# Thiết lập Grafana Dashboard

Grafana giúp trực quan hóa dữ liệu [17] và làm nơi Admin phê duyệt tác vụ.
1. Kết nối Data Source: Trỏ URL về `http://prometheus:9090`.
2. Import Template: Dùng ID `1860` cho Node Exporter và `14282` cho Docker [18].
3. **Panel Pending Approvals:** Kết nối CSDL của AI Agent, tạo bảng hiển thị các lỗi mức Medium có trạng thái `pending`.
4. Gắn Data Link vào bảng để Admin click "Approve" (gọi API Webhook).
