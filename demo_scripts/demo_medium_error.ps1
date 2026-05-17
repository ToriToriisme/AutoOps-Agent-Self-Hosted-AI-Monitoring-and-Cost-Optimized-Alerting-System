$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = "MatKhauCuaToi123" }

$body = @{ 
    status = "firing"
    title = "Windows CPU High"
    message = "Tieu thu CPU vuot muc 90% do tien trinh w3wp.exe (IIS Web Server)." 
} | ConvertTo-Json

Write-Host ">>> Đang bắn Webhook cảnh báo MEDIUM tới AutoOps Agent..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/alerts/webhook" -Method Post -Headers $headers -Body $body

Write-Host "`n>>> HOÀN TẤT! Đã gửi thành công. Hãy kiểm tra Database (bảng agent_tasks) xem task đã được đưa vào trạng thái 'pending' chờ duyệt chưa." -ForegroundColor Green
