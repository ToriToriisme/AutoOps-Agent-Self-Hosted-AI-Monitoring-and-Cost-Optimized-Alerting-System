# Tích hợp Lõi AI Google Gemini (gemini-1.5-flash) bằng LangChain

Tài liệu này tổng hợp toàn bộ kiến trúc, mã nguồn mẫu, phân tích ưu nhược điểm và lộ trình mở rộng quy mô giám sát khi sử dụng **Google Gemini** làm "bộ não" phân tích sự cố (Triage) cho AutoOps Agent Backend.

---

## 1. Tổng quan Kiến trúc

Thay vì gọi trực tiếp các LLM nội bộ hoặc tốn chi phí sử dụng OpenAI API, hệ thống tận dụng sức mạnh của **Google Gemini 1.5 Flash** thông qua framework **LangChain**. Quá trình này được đặt hoàn toàn trong `BackgroundTasks` của FastAPI nhằm đảm bảo phản hồi tức thì (SLA < 30s) cho Grafana Webhook.

### Quy trình Xử lý Khép kín (LangChain Pipeline)

1. **Tiếp nhận (Ingest):** Ghi nhận `received_at`, tạo `alert_id` và trả về HTTP `200 OK` cho Grafana.
2. **Trích xuất (Extract):** Lấy `alert_name`, `status`, và `description` từ chuỗi JSON Payload.
3. **Suy luận (Invoke):** Đẩy dữ liệu qua chuỗi Pipeline `chain = prompt_template | llm`.
4. **Phân luồng (Dispatch):** Dựa vào từ điển định tuyến `TRIAGE_POLICY` để xác định mức độ `SMALL`, `MEDIUM`, hay `CRITICAL`.
5. **Lưu vết (Audit):** Ghi nhận kết quả phân tích của Gemini (`ai_analysis`) vào Database.

---

## 2. Phân tích Ưu & Nhược điểm chuyên sâu

### 🟢 Ưu điểm vượt trội (Pros)

* **Tốc độ suy luận (Low Latency):** Model `gemini-1.5-flash` được thiết kế tối ưu cho tốc độ. Thời gian hoàn thành chuỗi LangChain và sinh ra văn bản phân tích chuyên sâu chỉ mất **1 - 2 giây**.
* **Chi phí tối ưu (Free Tier Hào phóng):** Google AI Studio cung cấp hạn mức miễn phí cực kỳ lớn: **15 RPM (Requests Per Minute)** và **1 triệu token/phút**, hoàn toàn đáp ứng trọn vẹn dải tải của hệ thống MVP/Demo mà không tốn chi phí.
* **Cửa sổ Ngữ cảnh Khổng lồ (1M Tokens Context Window):** Cho phép nạp toàn bộ lịch sử lỗi, file log hệ thống hoặc các tài liệu Playbook RAG cực dài vào Prompt mà không bị cắt xén dữ liệu.
* **Mã nguồn Chuẩn hóa:** Việc sử dụng cú pháp `chain = prompt_template | llm` giúp tách bạch hoàn toàn phần giao tiếp API ra khỏi logic nghiệp vụ, dễ dàng mở rộng hoặc hoán đổi sang các LLM khác sau này.

### 🔴 Điểm cần lưu ý & Giải pháp khắc phục (Gotchas)

* **Phụ thuộc Kết nối Mạng:** Vì Gemini là dịch vụ Cloud, Backend yêu cầu kết nối Internet ổn định. *(Giải pháp: Tích hợp sẵn Fallback tĩnh bám sát rule Day 1 để tự động gán nhãn nếu API Google bị timeout hoặc rớt mạng).*
* **Định dạng Đầu ra Tự do (Unstructured Output):** Thuộc tính `.content` trả về dạng chuỗi văn bản tự do. *(Giải pháp tương lai: Cấu hình thêm tham số `response_mime_type="application/json"` vào lớp `ChatGoogleGenerativeAI` hoặc dùng `StructuredOutputParser` của LangChain để ép AI trả về chuẩn JSON).*
* **Biến Môi trường trên Windows:** Khi thiết lập trên Terminal PowerShell, cần sử dụng cú pháp chuẩn của PowerShell để tránh lỗi không nhận diện API Key:

  ```powershell
  $env:GOOGLE_API_KEY="AIzaSy..."
  ```

---

## 3. Hướng dẫn Cài đặt & Thiết lập

### Bước 1: Cài đặt Thư viện

Mở Terminal PowerShell tại thư mục `agent_api` và chạy lệnh:

```powershell
pip install langchain-google-genai langchain-core
```

### Bước 2: Thiết lập Biến Môi trường

Lấy API Key từ [Google AI Studio](https://aistudio.google.com/) và cấu hình vào hệ thống:

* **Trên Windows PowerShell (Khuyến nghị):**

  ```powershell
  $env:GOOGLE_API_KEY="Điền_API_Key_Của_Bạn_Vào_Đây"
  ```

* **Trên Linux / macOS:**

  ```bash
  export GOOGLE_API_KEY="Điền_API_Key_Của_Bạn_Vào_Đây"
  ```

---

## 4. Mã nguồn Tích hợp Mẫu (`main.py`)

Dưới đây là cấu trúc lõi tích hợp Gemini bằng LangChain dùng cho `BackgroundTasks`:

```python
import os
import time
import uuid
from datetime import datetime, timezone

from fastapi import BackgroundTasks, Depends, FastAPI, Header
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# Import Schema thực tế của dự án
from .schemas.grafana_webhook import GrafanaWebhookPayload

app = FastAPI(title="AutoOps Agent API", version="0.1.0")

# 1. Khởi tạo LLM Gemini 1.5 Flash
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2, # Nhiệt độ thấp đảm bảo tính logic và chuẩn xác kỹ thuật
)

# 2. Định nghĩa Prompt Template chuyên nghiệp
prompt_template = PromptTemplate.from_template(
    "Hệ thống tôi vừa có cảnh báo [{alert_name}], trạng thái [{status}].\n"
    "Mô tả chi tiết: {description}\n\n"
    "Hãy đóng vai một DevOps Senior, giải thích ngắn gọn nguyên nhân có thể xảy ra "
    "và đề xuất hướng giải quyết."
)

# 3. Bảng định tuyến O(1) Triage Policy
TRIAGE_POLICY = {
    "Windows Server Down": "CRITICAL",
    "Windows CPU High": "MEDIUM",
    "Windows C: Drive Low Space": "SMALL" # Low disk map về SMALL để kích hoạt Auto-remediation
}

def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    _ = x_api_key

def process_alert_workflow(
    alert_id: str, payload: GrafanaWebhookPayload, received_at: datetime
) -> None:
    start_time = time.time()
    try:
        # BƯỚC 1: Trích xuất thông tin
        alert_name = payload.title
        status = payload.status
        description = ""
        if payload.alerts and len(payload.alerts) > 0:
            description = payload.alerts.annotations.get("description", "Không có mô tả.")
            alert_name = payload.alerts.labels.get("alertname", payload.title)

        # BƯỚC 2: Gọi Gemini phân tích qua LangChain Pipeline
        print(f"[{alert_id}] Đang nhờ Gemini phân tích lỗi: {alert_name}...")
        chain = prompt_template | llm
        ai_response = chain.invoke({
            "alert_name": alert_name,
            "status": status,
            "description": description
        })
        ai_analysis = ai_response.content
        print(f"[{alert_id}] Gemini (DevOps Senior) phản hồi:\n{ai_analysis}\n")

        # BƯỚC 3: Phân loại Severity từ từ điển O(1)
        severity = TRIAGE_POLICY.get(alert_name, "MEDIUM")

        # BƯỚC 4 & 5: Phân luồng và lưu Database (Lắp ghép các module DB/Script/Telegram)
        # ... logic thực thi tương ứng ...

    except Exception as e:
        print(f"[{alert_id}] Lỗi xử lý Gemini workflow: {str(e)}")
```

---

## 5. Lộ trình Mở rộng Quy mô lên 6 Cảnh báo Tiêu chuẩn

Để hệ thống đạt độ hoàn thiện cao nhất, danh sách giám sát sẽ được mở rộng theo cấu trúc cân bằng **2 CRITICAL, 2 MEDIUM, 2 SMALL**.

Bảng `TRIAGE_POLICY` dạng Dictionary đóng vai trò là một **Router O(1)**. Việc mở rộng hoàn toàn không làm phức tạp hóa mã nguồn (không tăng các khối `if/else`), chỉ cần bổ sung các cặp Key-Value tương ứng:

| Tên Cảnh báo (AlertName) | Phân loại (Severity) | Luồng Xử lý của Agent | Mục tiêu Tự động hóa |
| :--- | :---: | :--- | :--- |
| **`Windows C: Drive Low Space`** | **`SMALL`** | Auto-remediation | Gọi `cleanup_temp_files` dọn rác thư mục Temp. |
| **`Windows Memory Warning`** | **`SMALL`** | Auto-remediation | Tự động chạy lệnh giải phóng bộ nhớ đệm (Clear Cache). |
| **`Windows CPU High`** | **`MEDIUM`** | Treo `pending` | Đề xuất `restart_service`, chờ Admin bấm duyệt trên Dashboard. |
| **`Non-Core Service Hung`** | **`MEDIUM`** | Treo `pending` | Đề xuất khởi động lại Windows Service phụ bị treo/lỗi. |
| **`Windows Server Down`** | **`CRITICAL`** | Chỉ Notify Khẩn | Bắn thông báo ngay lập tức qua Telegram/Discord. |
| **`Core Database / Interface Down`** | **`CRITICAL`** | Chỉ Notify Khẩn | Báo động đỏ kèm theo bản phân tích nguyên nhân chuyên sâu từ Gemini. |
