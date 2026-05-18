$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = "MatKhauCuaToi123" }

$body = @{ 
    status = "firing"
    title = "Windows CPU High"
    message = "Tieu thu CPU vuot muc 90% do tien trinh w3wp.exe (IIS Web Server)." 
} | ConvertTo-Json

Write-Host ">>> Dang ban Webhook canh bao MEDIUM toi AutoOps Agent..." -ForegroundColor Yellow
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/alerts/webhook" -Method Post -Headers $headers -Body $body

Write-Host "`n>>> HOAN TAT! Da gui thanh cong. Hay kiem tra Database (bang agent_tasks) xem task da duoc dua vao trang thai 'pending' cho duyet chua." -ForegroundColor Green
