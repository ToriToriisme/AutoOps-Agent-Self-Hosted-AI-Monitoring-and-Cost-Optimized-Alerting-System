$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = "MatKhauCuaToi123" }

$body = @{ 
    status = "firing"
    title = "Windows C: Drive Low Space"
    message = "O dia C: hien chi con duoi 10% dung luong trong do cac file rac tai temp." 
} | ConvertTo-Json

Write-Host ">>> Dang ban Webhook canh bao SMALL toi AutoOps Agent..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/alerts/webhook" -Method Post -Headers $headers -Body $body

Write-Host "`n>>> HOAN TAT! Da gui thanh cong. Kich ban SMALL (an toan) nay se duoc AutoOps Agent TU DONG fix ma khong can doi Telegram." -ForegroundColor Green
