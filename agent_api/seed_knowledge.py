"""
Seed Knowledge Script — Nạp sẵn Playbook/SOP vào ChromaDB
Chạy một lần duy nhất khi khởi động hệ thống lần đầu hoặc khi cần cập nhật tri thức.
Lệnh chạy: python seed_knowledge.py
"""

import chromadb

# =====================================================================
# ĐỊNH NGHĨA BỘ PLAYBOOK / SOP NỘI BỘ
# Mỗi Playbook là một quy trình chuẩn xử lý 1 loại sự cố.
# Đây chính là "bộ não kiến thức" cho AI RAG.
# =====================================================================
PLAYBOOKS = [
    {
        "id": "pb_disk_001",
        "document": (
            "Tên sự cố: Disk Space Low / C Drive Low Space. "
            "Phân loại mức độ: SMALL. "
            "Nguyên nhân phổ biến: Thư mục Temp tích lũy file rác, "
            "file log hệ thống quá lớn, hoặc ứng dụng ghi cache không giới hạn. "
            "Quy trình xử lý chuẩn (SOP): "
            "Bước 1: Chạy công cụ cleanup_temp_files để dọn dẹp thư mục Temp và Cache. "
            "Bước 2: Sau khi chạy xong, kiểm tra lại dung lượng ổ đĩa. "
            "Bước 3: Nếu vẫn dưới ngưỡng an toàn, báo cáo cho Admin xem xét mở rộng dung lượng. "
            "Hành động đề xuất: cleanup_temp_files. "
            "Không cần phê duyệt của Admin nếu chỉ là dọn Temp."
        ),
        "metadata": {
            "urn": "rag:playbook:disk:cleanup_001",
            "category": "storage",
            "severity": "SMALL",
            "action": "cleanup_temp_files",
        },
    },
    {
        "id": "pb_cpu_001",
        "document": (
            "Tên sự cố: CPU High / Windows CPU High / High CPU Usage. "
            "Phân loại mức độ: MEDIUM. "
            "Nguyên nhân phổ biến: Tiến trình bị treo (hang), ứng dụng rò rỉ bộ nhớ, "
            "hoặc service lặp vô hạn. "
            "Quy trình xử lý chuẩn (SOP): "
            "Bước 1: Xác định process chiếm CPU cao nhất qua Task Manager hoặc PowerShell. "
            "Bước 2: Đề xuất khởi động lại service liên quan (restart_service). "
            "Bước 3: Bắt buộc phải có phê duyệt của Admin trước khi restart bất kỳ service nào "
            "để tránh ảnh hưởng đến dịch vụ đang hoạt động. "
            "Hành động đề xuất: restart_service. "
            "Yêu cầu phê duyệt Admin (Human-in-the-loop)."
        ),
        "metadata": {
            "urn": "rag:playbook:cpu:restart_001",
            "category": "performance",
            "severity": "MEDIUM",
            "action": "restart_service",
        },
    },
    {
        "id": "pb_service_down_001",
        "document": (
            "Tên sự cố: Windows Server Down / Service Down / Instance Down. "
            "Phân loại mức độ: CRITICAL. "
            "Nguyên nhân phổ biến: Mất điện đột ngột, lỗi phần cứng, "
            "kernel panic, hoặc tấn công mạng. "
            "Quy trình xử lý chuẩn (SOP): "
            "Bước 1: TUYỆT ĐỐI KHÔNG tự động khởi động lại hay can thiệp bất kỳ. "
            "Bước 2: Ngay lập tức gửi cảnh báo khẩn cấp tới toàn bộ đội ngũ SRE on-call. "
            "Bước 3: Đội SRE kiểm tra phần cứng và network trực tiếp tại chỗ. "
            "Bước 4: Sau khi điều tra xong mới quyết định hướng xử lý. "
            "Hành động đề xuất: Không có hành động tự động. Chỉ gửi cảnh báo. "
            "Lý do: Can thiệp sai vào server CRITICAL có thể gây mất dữ liệu vĩnh viễn."
        ),
        "metadata": {
            "urn": "rag:sop:server:critical_down_001",
            "category": "availability",
            "severity": "CRITICAL",
            "action": "",
        },
    },
    {
        "id": "pb_ram_001",
        "document": (
            "Tên sự cố: Memory High / RAM Usage High / High Memory. "
            "Phân loại mức độ: MEDIUM. "
            "Nguyên nhân phổ biến: Memory leak trong ứng dụng, quá nhiều tiến trình "
            "đồng thời, hoặc cấu hình bộ nhớ ảo (virtual memory) không đủ. "
            "Quy trình xử lý chuẩn (SOP): "
            "Bước 1: Ghi nhận danh sách process tiêu thụ RAM nhiều nhất. "
            "Bước 2: Đề xuất restart service bị rò rỉ bộ nhớ. "
            "Bước 3: Bắt buộc phải có phê duyệt Admin trước khi thực thi. "
            "Hành động đề xuất: restart_service. "
            "Yêu cầu phê duyệt Admin."
        ),
        "metadata": {
            "urn": "rag:playbook:memory:high_usage_001",
            "category": "performance",
            "severity": "MEDIUM",
            "action": "restart_service",
        },
    },
    {
        "id": "pb_network_001",
        "document": (
            "Tên sự cố: Network Down / Network Unreachable / Connection Lost. "
            "Phân loại mức độ: CRITICAL. "
            "Nguyên nhân phổ biến: Card mạng lỗi, cấu hình firewall sai, "
            "hoặc bị tấn công DDoS. "
            "Quy trình xử lý chuẩn (SOP): "
            "Bước 1: Không tự động can thiệp. "
            "Bước 2: Gửi cảnh báo khẩn cấp tới đội network on-call. "
            "Bước 3: Đội network kiểm tra switch, router và firewall. "
            "Hành động đề xuất: Không có hành động tự động. Chỉ gửi cảnh báo."
        ),
        "metadata": {
            "urn": "rag:sop:network:down_001",
            "category": "connectivity",
            "severity": "CRITICAL",
            "action": "",
        },
    },
]


def seed_chromadb(chroma_path: str = "storage/chroma_db") -> None:
    """
    Nạp toàn bộ Playbook/SOP vào ChromaDB.
    Sử dụng upsert() để tránh trùng lặp khi chạy lại nhiều lần.
    """
    print(f"[*] Kết nối tới ChromaDB tại: {chroma_path}")
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection("playbooks")

    ids = [pb["id"] for pb in PLAYBOOKS]
    docs = [pb["document"] for pb in PLAYBOOKS]
    metas = [pb["metadata"] for pb in PLAYBOOKS]

    collection.upsert(documents=docs, metadatas=metas, ids=ids)

    print(f"[+] Đã nạp thành công {len(PLAYBOOKS)} Playbook/SOP vào ChromaDB!")
    print("[+] Danh sách Playbook đã nạp:")
    for pb in PLAYBOOKS:
        print(f"    - [{pb['metadata']['severity']}] {pb['id']}: {pb['metadata']['urn']}")

    # Kiểm tra xem query hoạt động đúng không
    print("\n[*] Kiểm tra thử truy vấn RAG với câu lệnh: 'disk is almost full'...")
    results = collection.query(query_texts=["disk is almost full"], n_results=1)
    if results and results.get("documents") and results["documents"][0]:
        print(f"[+] Kết quả truy vấn: {results['documents'][0][0][:100]}...")
    print("\n[✓] ChromaDB đã sẵn sàng phục vụ AI RAG!")


if __name__ == "__main__":
    seed_chromadb()
