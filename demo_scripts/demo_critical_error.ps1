$ErrorActionPreference = "SilentlyContinue"
$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = "MatKhauCuaToi123" }

# 1. Ghi một log lỗi giả lập vào hệ thống Windows để AI đọc
# Lệnh này có thể yêu cầu quyền Admin, nếu không có quyền nó sẽ tự bỏ qua (không báo lỗi đỏ)
Write-Host ">>> [1/2] Đang tạo log lỗi hệ thống giả định..." -ForegroundColor Cyan
Write-EventLog -LogName System -Source "Service Control Manager" -EventId 7031 -EntryType Error -Message "The Core Database service terminated unexpectedly due to a fatal crash."

# 2. Đóng giả Grafana bắn Webhook
$body = @{ 
    status = "firing"
    title = "Windows Server Down"
    message = "Canh bao: He thong mat ket noi voi Database Server. Vui long kiem tra." 
} | ConvertTo-Json

Write-Host ">>> [2/2] Đang bắn Webhook cảnh báo CRITICAL tới AutoOps Agent..." -ForegroundColor Red
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/alerts/webhook" -Method Post -Headers $headers -Body $body

Write-Host "`n>>> HOÀN TẤT! Đã gửi thành công. Hãy kiểm tra điện thoại xem có tin nhắn Telegram tới chưa nhé!" -ForegroundColor Green
