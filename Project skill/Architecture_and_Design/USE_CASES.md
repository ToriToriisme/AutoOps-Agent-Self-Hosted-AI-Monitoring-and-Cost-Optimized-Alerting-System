# Đặc tả Kịch bản Sử dụng (Use Cases)

## Tác nhân (Actors)

Để “nhìn dễ” và phù hợp MVP, actor được gom tối giản (giống các sơ đồ CRUD trước đây):
1. **Operator/Admin:** Người vận hành, xem trạng thái và duyệt tác vụ.
2. **Grafana Alerting (Unified Alerting):** Đánh giá rule và gửi webhook cảnh báo.
3. **Kênh cảnh báo khẩn (Telegram/Email/SMS):** Nhận thông báo khi sự cố Critical.

> Ghi chú: Prometheus/Exporters là **hạ tầng dữ liệu nền** cho Grafana Alerting, không nhất thiết phải vẽ như actor trong sơ đồ use case MVP.

## Các Use Case cốt lõi [9]

Các use case được rút gọn theo đúng “xương sống” Closed-loop AIOps (MVP-first):
- **UC-01:** Nhận cảnh báo từ Grafana Alerting (webhook).
- **UC-02:** Phân loại cảnh báo (Triage) → SMALL / MEDIUM / CRITICAL.
- **UC-03:** Tự khắc phục lỗi SMALL (Auto-fix bằng tool/script whitelist).
- **UC-04:** Tạo tác vụ MEDIUM và chờ duyệt (Pending Approval).
- **UC-05:** Operator/Admin duyệt hoặc từ chối tác vụ MEDIUM.
- **UC-06:** Xử lý CRITICAL và gửi cảnh báo khẩn (Notify).
- **UC-07:** Audit/giám sát: xem tool calls & token usage.

## Use Case bổ sung

### UC-00: Luồng tổng quan Closed-loop AIOps (MVP)

- **Mục tiêu:** Nhận alert → triage → auto-fix/approve/notify → audit.
- **Tác nhân:** Grafana Alerting, Operator/Admin, Kênh cảnh báo khẩn.
- **Tiền điều kiện:** Grafana Alerting đã cấu hình rule + webhook; AI Agent có tool/script whitelist.
- **Luồng chính (tối đa 8 bước, dễ đưa vào báo cáo):**
  1. Grafana Alerting gửi webhook cảnh báo đến AI Agent.
  2. AI Agent chuẩn hóa payload và lấy thêm context tối thiểu (metrics liên quan).
  3. AI Agent triage và gán mức: SMALL/MEDIUM/CRITICAL.
  4. Nếu SMALL: gọi tool/script whitelist và ghi kết quả.
  5. Nếu MEDIUM: tạo task `pending` hiển thị trên Grafana Dashboard.
  6. Operator/Admin duyệt hoặc từ chối.
  7. Nếu duyệt: AI Agent thực thi tool/script và cập nhật trạng thái.
  8. Nếu CRITICAL: gửi cảnh báo khẩn qua Telegram/Email/SMS.
- **Hậu điều kiện:** Task được xử lý, chờ duyệt, hoặc đã cảnh báo; mọi bước được audit.

### UC-05: Operator/Admin duyệt tác vụ MEDIUM (chi tiết)

- **Mục tiêu:** Hành động mức MEDIUM chỉ chạy khi có con người duyệt.
- **Tác nhân:** Operator/Admin.
- **Tiền điều kiện:** Có task `pending` trên Dashboard.
- **Luồng chính:**
  1. Operator/Admin mở bảng “Pending Approvals”.
  2. Xem đề xuất (nguyên nhân, tool sẽ gọi, tham số, rủi ro).
  3. Chọn **Approve** hoặc **Reject**.
  4. Hệ thống cập nhật trạng thái `approved/rejected` và lưu audit.
- **Hậu điều kiện:** Task được duyệt/từ chối; nếu duyệt thì chuyển sang thực thi.

## Use Case Diagram (MVP) – bố cục đơn giản như hình mẫu

> Nếu bạn dùng PlantUML online/app: **chỉ copy phần từ `@startuml` đến `@enduml`** (đừng copy các dấu ``` của Markdown), rồi export PNG/SVG (300dpi) đưa vào báo cáo.

```
@startuml
title Use Case Diagram (MVP) - Self-Hosted AI Agent Monitor System

left to right direction
skinparam packageStyle rectangle

actor "Operator/Admin" as OP
actor "Grafana Alerting" as GA
actor "Telegram/Email/SMS" as NOTI

rectangle "AI Agent Monitor System" {
  usecase "Nhận cảnh báo\n(Webhook)" as U1
  usecase "Triage cảnh báo\n(SMALL/MEDIUM/CRITICAL)" as U2
  usecase "Auto-fix SMALL\n(whitelist tools)" as U3
  usecase "Tạo MEDIUM pending" as U4
  usecase "Duyệt/Từ chối MEDIUM" as U5
  usecase "Notify CRITICAL" as U6
  usecase "Audit/Quan sát\n(tool calls, tokens)" as U7
}

GA --> U1
U1 .> U2 : <<include>>
U2 .> U3 : <<extend>>
U2 .> U4 : <<extend>>
U2 .> U6 : <<extend>>

OP --> U5
OP --> U7
U4 .> U5 : <<include>>

U6 --> NOTI
U3 .> U7 : <<include>>
U5 .> U7 : <<include>>
U6 .> U7 : <<include>>

@enduml
```
