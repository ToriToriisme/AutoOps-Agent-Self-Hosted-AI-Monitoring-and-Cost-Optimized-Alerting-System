# FIX (Giai đoạn Thực thi & Sửa chữa)

Đây là giai đoạn cốt lõi nơi bạn tập trung viết code và giải quyết các bài toán kỹ thuật, đồng thời cũng là lúc AI Agent thực thi nhiệm vụ của nó.

## Đối với bạn (Dev/Admin)

- **Viết và sửa script:** Bạn phải code và tối ưu các script trong Whitelist như `cleanup_temp.sh` hoặc `restart_container.sh`. Đảm bảo phân quyền chặt chẽ để hệ thống an toàn (Least Privilege).
- **Fix logic AI & RAG:** Nếu lúc "Catchup" bạn thấy AI phán đoán sai, bạn phải "Fix" bằng cách sửa lại System Prompt, điều chỉnh lại tham số `chunk_size`, `chunk_overlap`, hoặc thử áp dụng Semantic Chunking/Hybrid Search thay vì Recursive Chunking thông thường để AI đọc hiểu tài liệu tốt hơn.
- **Xử lý bug:** Sửa lỗi API trên FastAPI, đảm bảo luồng nhận Webhook và phân loại SMALL/MEDIUM/CRITICAL chạy mượt mà không bị crash.

## Đối với AI Agent (Bước Execution)

Thực hiện hành động Auto-fix đối với các lỗi SMALL (ví dụ: tự động dọn rác ổ cứng `cleanup_temp_files` khi Disk đầy 85-95%).
