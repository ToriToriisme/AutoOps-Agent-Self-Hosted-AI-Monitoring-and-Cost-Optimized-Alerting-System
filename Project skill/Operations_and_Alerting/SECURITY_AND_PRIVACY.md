# Cẩm nang Bảo mật & Quyền riêng tư

- **Nguyên tắc Self-Host:** Dữ liệu log máy chủ, tên service KHÔNG bao giờ được đi ra ngoài Internet.
- **Air-Gapped Ready:** Image AI (ví dụ Ollama) cần được pull về máy và chạy Offline [28].
- **Nguyên tắc Đặc quyền Tối thiểu (Least Privilege):** AI chỉ có quyền gọi các hàm API đã viết sẵn, tuyệt đối KHÔNG cấp quyền root shell (`/bin/bash`) cho LLM tự do thao tác.
