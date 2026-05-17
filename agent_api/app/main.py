import json
import os
import subprocess
import time
import uuid
from datetime import datetime, timezone

from pathlib import Path
from dotenv import load_dotenv

# Tự động tìm đường dẫn tuyệt đối đến file .env (nằm cùng cấp với thư mục app)
base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"

# Nạp các biến môi trường từ file .env
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"[DEBUG] Đã nạp file .env từ: {env_path}")
else:
    print(f"[DEBUG] CẢNH BÁO: Không tìm thấy file .env tại: {env_path}")

# Kiểm tra xem đã nhận đúng Key chưa
api_key_raw = os.getenv("GOOGLE_API_KEY", "")
api_key = api_key_raw.strip() # Xóa khoảng trắng thừa nếu có
if api_key:
    print(f"[DEBUG] Đã nhận API Key: {api_key[:5]}***")
else:
    print("[DEBUG] CẢNH BÁO: GOOGLE_API_KEY vẫn đang trống (None)!")
    print("[DEBUG] CẢNH BÁO: GOOGLE_API_KEY vẫn đang trống (None)!")


from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from .database import init_db, insert_agent_task, insert_audit_log, update_agent_task_status
from .schemas.grafana_webhook import GrafanaWebhookPayload

app = FastAPI(title="AutoOps Agent API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    # Tự động khởi tạo cấu trúc bảng SQLite khi khởi động server
    init_db()


# --- PHẦN CẤU HÌNH AI (GEMINI) ---
# Sử dụng Gemini 3.1 Flash Lite - Phiên bản mới nhất năm 2026
llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    google_api_key=api_key,
    temperature=0.2,
)

ALLOWED_TOOLS = {
    "cleanup_temp_files": "tools/powershell/cleanup_temp_files.ps1",
    "restart_service": "tools/powershell/restart_service.ps1",
}

whitelist_str = ", ".join(ALLOWED_TOOLS.keys())

# Định nghĩa Prompt Template chuyên nghiệp cho DevOps Senior
prompt_template = PromptTemplate.from_template(
    "Bạn là một DevOps Senior. Hệ thống vừa có cảnh báo: [{alert_name}] (Trạng thái: {status}).\n"
    "Mô tả chi tiết: {description}\n"
    "Event Logs hệ thống Windows gần đây (Nếu 'Không tìm thấy log...', hãy chỉ dựa vào Grafana): {event_logs}\n\n"
    "RÀNG BUỘC QUAN TRỌNG:\n"
    "1. Phân loại mức độ sự cố: Chỉ được chọn SMALL, MEDIUM, hoặc CRITICAL.\n"
    f"2. Đề xuất HÀNH ĐỘNG xử lý: BẮT BUỘC phải nằm trong danh sách sau: [{whitelist_str}]. Nếu sự cố không khớp với lệnh nào, hãy trả về chuỗi rỗng.\n"
    "3. Trả kết quả DƯỚI DẠNG JSON với các key sau: severity_assessment, root_cause_analysis, suggested_action. Trả về JSON thuần, KHÔNG kèm giải thích markdown."
)

# Bảng định tuyến O(1) Triage Policy
TRIAGE_POLICY = {
    "Windows Server Down": "CRITICAL",
    "Windows CPU High": "MEDIUM",
    "Windows C: Drive Low Space": "SMALL",
}


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    # Lấy API Key từ biến môi trường .env
    VALID_API_KEY = os.getenv("AGENT_API_KEY", "default_secret_key")
    
    # DEBUG: In ra để thám tử tìm lỗi (Sẽ hiện trong docker logs)
    print(f"[DEBUG] Auth Check - Expected: {VALID_API_KEY[:3]}***, Received: {x_api_key[:3] if x_api_key else 'NONE'}***")

    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized: Invalid or missing X-API-Key header"
        )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def run_script(tool_name: str, args: dict) -> str:
    """
    Thực thi an toàn script PowerShell với cơ chế Circuit Breaker (Whitelist).
    """
    # CIRCUIT BREAKER: Kiểm tra chặt chẽ allowlist
    if tool_name not in ALLOWED_TOOLS:
        return f"ERROR: Tool '{tool_name}' is not in ALLOWED_TOOLS whitelist."

    script_path = ALLOWED_TOOLS[tool_name]
    cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]

    # Map tham số an toàn từ payload args
    if tool_name == "cleanup_temp_files":
        target_path = args.get("target_path") or args.get("TargetPath") or "C:\\Windows\\Temp"
        cmd.extend(["-TargetPath", str(target_path)])
    elif tool_name == "restart_service":
        service_name = args.get("service_name") or args.get("ServiceName") or "Spooler"
        cmd.extend(["-ServiceName", str(service_name)])

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = res.stdout.strip() if res.stdout else res.stderr.strip()
        if not output:
            return f"SUCCESS: {tool_name} completed successfully."

        # Chuẩn hoá trả về đúng 1 dòng output theo thoả thuận
        for line in output.splitlines():
            if line.startswith("SUCCESS:") or line.startswith("ERROR:"):
                return line
        return f"SUCCESS: {tool_name} completed. Output: {output[:100]}"
    except subprocess.TimeoutExpired:
        return f"ERROR: Tool {tool_name} execution timed out."
    except Exception as e:
        return f"ERROR: Failed to run tool {tool_name}: {str(e)}"


# === DAY 12: Mục 2.1 & 2.2 - Lấy log Windows và làm sạch ===
def get_windows_event_logs() -> str:
    """
    Chạy lệnh PowerShell ngầm để lấy Event Logs của Windows.
    Giới hạn 5 sự kiện trong 15 phút gần nhất.
    """
    ps_command = (
        "Get-WinEvent -FilterHashtable @{LogName='System'; Level=2,3; StartTime=(Get-Date).AddMinutes(-15)} -MaxEvents 5 -ErrorAction SilentlyContinue | "
        "Select-Object @{Name='TimeCreated';Expression={$_.TimeCreated.ToString('yyyy-MM-dd HH:mm:ss')}}, Message | ConvertTo-Json -Compress"
    )
    
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                logs = json.loads(result.stdout)
                clean_logs = []
                if isinstance(logs, dict):
                    logs = [logs]
                    
                for log in logs:
                    time_created = log.get("TimeCreated", "N/A")
                    message = str(log.get("Message", "")).replace('\r', '').replace('\n', ' ')
                    if len(message) > 500:
                        message = message[:497] + "..."
                    clean_logs.append(f"[{time_created}] {message}")
                
                return "\n".join(clean_logs)
            except json.JSONDecodeError:
                return "Không thể parse dữ liệu log từ Windows."
        else:
            return "Không tìm thấy log lỗi nào trong 15 phút qua."
            
    except subprocess.TimeoutExpired:
        return "Lỗi: Quá hạn 5 giây khi lấy log hệ thống."
    except Exception as e:
        return f"Lỗi không xác định khi lấy log: {str(e)}"
# ==============================================================


def query_rag_context(title: str) -> tuple[str, list[str]]:
    """
    Truy xuất RAG lấy Context Playbook và danh sách tham chiếu chuẩn URN.
    """
    try:
        
        import chromadb

        client = chromadb.PersistentClient(path="storage/chroma_db")
        collection = client.get_or_create_collection("playbooks")
        results = collection.query(query_texts=[title], n_results=1)
        if results and results.get("documents") and results["documents"][0]:
            doc = results["documents"][0][0]
            meta = results["metadatas"][0][0] if results.get("metadatas") else {}
            ref = meta.get("urn", f"rag:playbook:system:{title.lower().replace(' ', '_')}")
            return doc, [ref]
    except Exception:
        pass  # Fallback mượt mà sang quy tắc chốt sẵn nếu chưa dựng ChromaDB

    title_lower = title.lower()
    if "disk" in title_lower or "space" in title_lower:
        return (
            "Playbook hướng dẫn: Khi Disk Space Low, tự động gọi công cụ cleanup_temp_files để dọn dẹp thư mục Temp giải phóng dung lượng.",
            ["rag:playbook:system:disk_cleanup_001"],
        )
    elif "down" in title_lower or "critical" in title_lower:
        return (
            "Playbook hướng dẫn: Khi Core Service DOWN, tuyệt đối không tự can thiệp, gửi thông báo khẩn cấp (CRITICAL notify) tới đội ngũ SRE.",
            ["rag:sop:docker:restart_policy"],
        )
    else:
        return (
            "Playbook hướng dẫn: Khi CPU hoặc RAM quá tải (>90%), đề xuất giải pháp restart_service, tạo bản ghi pending chờ Admin duyệt.",
            ["rag:playbook:system:high_load_handling"],
        )


import re
from .schemas.ai_triage import AITriageResponse

def call_llm_triage(title: str, context: str, payload_dict: dict) -> tuple[str, str, str, int, int]:
    """
    Gọi Gemini 3.1 Flash Lite phân loại sự cố (Triage) với cơ chế Fallback an toàn.
    Trả về: (severity, proposed_action, decision_reason, prompt_tokens, completion_tokens)
    """
    try:
        # 1. Trích xuất thông tin từ payload
        status = payload_dict.get("status", "firing")
        
        # Cố gắng lấy message, nếu không có thì lấy từ annotations của alert đầu tiên
        description = payload_dict.get("message")
        if not description and payload_dict.get("alerts"):
            first_alert_annotations = payload_dict["alerts"][0].get("annotations", {})
            summary = first_alert_annotations.get("summary", "")
            desc = first_alert_annotations.get("description", "")
            description = f"{summary} - {desc}".strip(" -")
            
        if not description:
            description = "Không có mô tả chi tiết."

        # 1.5. Lấy Event Logs từ Windows (Day 12 - Bước 2.1)
        print(f"[*] Đang lấy Windows Event Logs làm ngữ cảnh...")
        event_logs = get_windows_event_logs()

        # 2. Xây dựng Chain và gọi Gemini
        print(f"[*] Đang nhờ Gemini phân tích lỗi: {title}...")
        chain = prompt_template | llm
        ai_msg = chain.invoke(
            {
                "alert_name": title, 
                "status": status, 
                "description": f"{description}\n\nContext từ RAG: {context}",
                "event_logs": event_logs
            }
        )
        
        # 3. LLM Observability: Trích xuất Token tiêu thụ
        p_tokens = 0
        c_tokens = 0
        if hasattr(ai_msg, "usage_metadata") and ai_msg.usage_metadata:
            p_tokens = ai_msg.usage_metadata.get("input_tokens", 0)
            c_tokens = ai_msg.usage_metadata.get("output_tokens", 0)

        # 4. Ép kiểu Validation bằng Pydantic
        raw_text = ai_msg.content
        if isinstance(raw_text, list):
            raw_text = "\n".join([block.get("text", "") for block in raw_text if isinstance(block, dict) and "text" in block])
        elif not isinstance(raw_text, str):
            raw_text = str(raw_text)
            
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(1)
            
        parsed_data = AITriageResponse.model_validate_json(raw_text)

        severity = parsed_data.severity_assessment
        proposed_action = parsed_data.suggested_action
        decision_reason = parsed_data.root_cause_analysis

        # 5. Kiểm duyệt Whitelist
        if proposed_action and proposed_action not in ALLOWED_TOOLS:
            raise ValueError(f"AI đề xuất lệnh cấm '{proposed_action}' không nằm trong whitelist!")

        return severity, proposed_action, decision_reason, p_tokens, c_tokens

    except Exception as e:
        print(f"[-] Gemini integration failed hoặc vi phạm bảo mật. Chi tiết lỗi: {str(e)}")
        print("[!] applying robust fallback policy (Đang kích hoạt quy tắc dự phòng)...")

    # Fallback chuẩn Day1.md
    title_lower = title.lower()
    if "disk" in title_lower or "space" in title_lower:
        return (
            "SMALL",
            "cleanup_temp_files",
            "Fallback rule: Disk space warning tự động gọi dọn dẹp temp files.",
            0,
            0,
        )
    elif "down" in title_lower or "critical" in title_lower:
        return (
            "CRITICAL",
            "",
            "Fallback rule: Service/Container DOWN kích hoạt báo động khẩn cấp.",
            0,
            0,
        )
    else:
        return (
            "MEDIUM",
            "restart_service",
            "Fallback rule: CPU/Memory load cao cần tạo task pending chờ duyệt.",
            0,
            0,
        )


def send_telegram_alert(payload: GrafanaWebhookPayload, ai_analysis: str = "") -> bool:
    """
    Gửi thông báo khẩn cấp tới Telegram kèm phân tích của AI.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        print("Telegram Bot Token or Chat ID not found in .env. Skipping external notification.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Soạn nội dung tin nhắn chuyên nghiệp
    text = (
        f"🚨 **HỆ THỐNG PHÁT HIỆN SỰ CỐ** 🚨\n\n"
        f"🔹 **Cảnh báo:** {payload.title}\n"
        f"🔹 **Trạng thái:** {payload.status.upper()}\n\n"
        f"🧠 **PHÂN TÍCH TỪ AI (DevOps Senior):**\n"
        f"{ai_analysis if ai_analysis else 'AI đang bận, vui lòng kiểm tra log.'}"
    )
    
    try:
        import requests

        # Bỏ parse_mode tạm thời để tránh lỗi sập API khi AI sinh ra ký tự lạ (Markdown không chuẩn)
        resp = requests.post(
            url, json={"chat_id": chat_id, "text": text}, timeout=5
        )
        if resp.status_code != 200:
            print(f"[-] Lỗi gửi Telegram! HTTP {resp.status_code}: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"[-] Telegram notification failed: {str(e)}")
        return False


# Hàm xử lý nghiệp vụ chạy ngầm
def process_alert_workflow(
    alert_id: str, payload: GrafanaWebhookPayload, received_at: datetime
) -> None:
    """
    Đây là "bộ não" thực sự của AI Agent.
    """
    start_time = time.time()
    payload_dict = payload.dict()

    try:
        # BƯỚC 1: AI-LOOKUP (RAG)
        rag_context, rag_refs = query_rag_context(payload.title)

        # BƯỚC 2: TRIAGE BẰNG LLM (OLLAMA)
        severity, proposed_action, decision_reason, p_tokens, c_tokens = call_llm_triage(
            payload.title, rag_context, payload_dict
        )

        # BƯỚC 3: PHÂN NHÁNH THỰC THI (ACTION DISPATCHER)
        status = "received"
        execution_output = ""
        notified_at = None

        # Khởi tạo bản ghi agent_tasks trong Database
        insert_agent_task(
            task_id=alert_id,
            alert_title=payload.title,
            labels=payload.labels,
            severity=severity,
            proposed_action=proposed_action,
            status=status,
        )

        if severity == "SMALL":
            # Tự động chạy script trong whitelist
            execution_output = run_script(proposed_action, payload.labels)
            status = "executed"
            update_agent_task_status(alert_id, status)

        elif severity == "MEDIUM":
            # Treo task lại, chờ Admin vào Dashboard duyệt
            status = "pending"
            update_agent_task_status(alert_id, status)

        elif severity == "CRITICAL":
            # Không sửa tự động, gửi cảnh báo khẩn cấp kèm phân tích AI
            send_telegram_alert(payload, ai_analysis=decision_reason)
            notified_at = datetime.now(timezone.utc)
            status = "notified"
            update_agent_task_status(alert_id, status)
            execution_output = f"Notification dispatched at {notified_at.isoformat()}"

        # BƯỚC 4: GHI NHẬN AUDIT LOG & ĐO LƯỜNG SLA
        # Nếu là CRITICAL, tính thời gian chính xác tới khi gửi xong notify
        end_measure_time = notified_at.timestamp() if notified_at else time.time()
        processing_time_ms = int((end_measure_time - start_time) * 1000)

        # Lưu log hoàn chỉnh vào bảng audit_logs
        insert_audit_log(
            task_id=alert_id,
            rag_context_used=rag_context,
            rag_context_refs=rag_refs,
            decision_reason=decision_reason,
            execution_result="SUCCESS" if status in ["executed", "pending", "notified"] else status,
            execution_output=execution_output,
            processing_time_ms=processing_time_ms,
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens,
        )

        print(f"[{alert_id}] Processed successfully. Severity: {severity}. Status: {status}")

    except Exception as e:
        err_msg = f"Error processing alert: {str(e)}"
        print(f"[{alert_id}] {err_msg}")
        try:
            # UPDATE trạng thái của task thành failed khi có Exception
            update_agent_task_status(alert_id, "failed")
            # Ghi log chuỗi str(e) vào trường execution_output của bảng audit_logs
            processing_time_ms = int((time.time() - start_time) * 1000)
            insert_audit_log(
                task_id=alert_id,
                rag_context_used="N/A",
                rag_context_refs=[],
                decision_reason="Workflow Exception",
                execution_result="FAILED",
                execution_output=err_msg,
                processing_time_ms=processing_time_ms,
            )
        except Exception as db_err:
            print(f"[{alert_id}] Fatal DB logging error: {str(db_err)}")


@app.post("/api/v1/alerts/webhook")
def ingest_grafana_webhook(
    payload: GrafanaWebhookPayload,
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_api_key),
) -> dict:
    # 1. Ghi nhận thời gian T0 ngay lập tức để sau này tính SLA < 30s
    received_at = datetime.now(timezone.utc)

    # 2. Tạo ID duy nhất cho cảnh báo này để dễ dàng tracking trong DB
    alert_id = f"ALT-{received_at.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"

    # 3. Đẩy tác vụ nặng (RAG + LLM + Script) vào background
    background_tasks.add_task(process_alert_workflow, alert_id, payload, received_at)

    # 4. Phản hồi Grafana ngay lập tức
    return {
        "received": True,
        "alert_id": alert_id,
        "title": payload.title,
        "message": "Alert is being triaged by AI Agent in the background.",
    }



