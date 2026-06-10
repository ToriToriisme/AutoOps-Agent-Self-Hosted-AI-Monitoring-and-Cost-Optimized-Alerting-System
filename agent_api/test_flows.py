import asyncio
import os
import sys

# Thêm đường dẫn để import từ app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_api.app.main import learn_from_resolution, telegram_webhook
from agent_api.app.database import insert_agent_task, get_agent_task

# Mock Request class for FastAPI
class MockRequest:
    def __init__(self, json_data):
        self._json_data = json_data
    
    async def json(self):
        return self._json_data

async def test_telegram_webhook_approve():
    print("--- Test Telegram Webhook Approve ---")
    
    # 1. Tạo một pending task ảo trong DB (Xóa trước nếu đã tồn tại)
    test_alert_id = "ALT-TEST-12345"
    from agent_api.app.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agent_tasks WHERE task_id = ?", (test_alert_id,))
    cursor.execute("DELETE FROM audit_logs WHERE task_id = ?", (test_alert_id,))
    conn.commit()
    conn.close()
    
    insert_agent_task(
        task_id=test_alert_id,
        alert_title="Test CPU High",
        labels={"instance": "test-node"},
        severity="MEDIUM",
        proposed_action="restart_service",
        status="pending"
    )
    print(f"Created pending task: {test_alert_id}")
    
    # 2. Giả lập payload từ Telegram (Admin bấm Approve)
    mock_payload = {
        "update_id": 10000,
        "callback_query": {
            "id": "4382bfdw8732",
            "from": {"id": 1111111, "is_bot": False, "first_name": "Admin"},
            "message": {
                "message_id": 112,
                "from": {"id": 2222222, "is_bot": True, "first_name": "AutoOps Bot"},
                "chat": {"id": 1111111, "type": "private"},
                "date": 1610000000,
                "text": "🤖 Chào admin, hệ thống vừa ghi nhận một sự cố cần được chú ý!..."
            },
            "chat_instance": "444444",
            "data": f"approve_{test_alert_id}"
        }
    }
    
    request = MockRequest(mock_payload)
    
    # 3. Gọi webhook
    response = await telegram_webhook(request)
    print(f"Webhook response: {response}")
    
    # 4. Kiểm tra xem DB đã update chưa
    task = get_agent_task(test_alert_id)
    if task:
        print(f"Task status sau khi duyệt: {task['status']}")
        assert task['status'] == "executed", "Trạng thái phải là executed"
    else:
        print("Không tìm thấy task trong DB")
        
    print("Test Approve: OK\n")

async def test_telegram_webhook_reject():
    print("--- Test Telegram Webhook Reject ---")
    
    # 1. Tạo một pending task ảo trong DB (Xóa trước nếu đã tồn tại)
    test_alert_id = "ALT-TEST-99999"
    from agent_api.app.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agent_tasks WHERE task_id = ?", (test_alert_id,))
    cursor.execute("DELETE FROM audit_logs WHERE task_id = ?", (test_alert_id,))
    conn.commit()
    conn.close()
    
    insert_agent_task(
        task_id=test_alert_id,
        alert_title="Test DB Down",
        labels={"instance": "db-node"},
        severity="CRITICAL",
        proposed_action="restart_service",
        status="pending"
    )
    print(f"Created pending task: {test_alert_id}")
    
    # 2. Giả lập payload từ Telegram (Admin bấm Reject)
    mock_payload = {
        "update_id": 10001,
        "callback_query": {
            "id": "4382bfdw8733",
            "from": {"id": 1111111, "is_bot": False, "first_name": "Admin"},
            "message": {
                "message_id": 113,
                "chat": {"id": 1111111, "type": "private"},
                "text": "Cảnh báo khẩn cấp..."
            },
            "data": f"reject_{test_alert_id}"
        }
    }
    
    request = MockRequest(mock_payload)
    
    # 3. Gọi webhook
    response = await telegram_webhook(request)
    print(f"Webhook response: {response}")
    
    # 4. Kiểm tra xem DB đã update chưa
    task = get_agent_task(test_alert_id)
    if task:
        print(f"Task status sau khi reject: {task['status']}")
        assert task['status'] == "rejected", "Trạng thái phải là rejected"
        
    print("Test Reject: OK\n")

def test_learn_from_resolution():
    print("--- Test ChromaDB Learning ---")
    alert_id = "ALT-LEARN-001"
    title = "C Drive Full"
    action = "cleanup_temp_files"
    result = "executed"
    reason = "Test học hỏi kinh nghiệm"
    
    try:
        learn_from_resolution(alert_id, title, action, result, reason)
        print("ChromaDB Upsert thành công!")
        
        # Thử query lại xem có ra không
        import chromadb
        client = chromadb.PersistentClient(path="storage/chroma_db")
        collection = client.get_or_create_collection("playbooks")
        results = collection.get(ids=[f"learned_{alert_id}"])
        print(f"Dữ liệu đã lưu trong ChromaDB: {results['documents']}")
        print("Test Learning: OK\n")
    except Exception as e:
        print(f"Test Learning Failed: {e}")

if __name__ == "__main__":
    print("Bắt đầu chạy Tests...\n")
    
    # 1. Khởi tạo DB nếu chưa có
    from agent_api.app.database import init_db
    init_db()
    
    # 2. Chạy test đồng bộ (ChromaDB)
    test_learn_from_resolution()
    
    # 3. Chạy test bất đồng bộ (Webhook FastAPI)
    asyncio.run(test_telegram_webhook_approve())
    asyncio.run(test_telegram_webhook_reject())
    
    print("Tất cả Tests hoàn tất!")
