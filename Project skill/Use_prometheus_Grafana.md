# Tài liệu: Khắc phục lỗi và Khởi chạy Prometheus & Grafana (Ngày 2)

Tài liệu này ghi chú lại quá trình và nguyên nhân của các lỗi đã gặp phải khi thiết lập Docker Compose cho Prometheus và Grafana, cũng như cách chúng ta đã giải quyết chúng.

## 1. Lỗi "docker is not recognized"
**Hiện tượng:** 
Khi chạy lệnh `docker compose up -d`, hệ thống (PowerShell/Terminal) báo lỗi không nhận diện được lệnh `docker`, mặc dù phần mềm Docker Desktop đã được mở và báo trạng thái "Engine running".

**Nguyên nhân:**
Lỗi này thường xảy ra trên Windows do một trong hai nguyên nhân:
1. Cửa sổ Terminal (hoặc VS Code) đã được mở từ **trước** khi Docker Desktop được cài đặt xong. Do đó, Terminal cũ chưa nhận được đường dẫn lệnh mới.
2. Quá trình cài đặt Docker chưa tự động thêm đường dẫn chứa file thực thi (`C:\Program Files\Docker\Docker\resources\bin`) vào biến môi trường (Environment Variables) `PATH` của hệ thống.

**Cách khắc phục:**
* **Tạm thời (Đã áp dụng):** Thêm trực tiếp đường dẫn của Docker vào biến môi trường của phiên PowerShell hiện tại và chạy lại lệnh.
  ```powershell
  $env:PATH += ';C:\Program Files\Docker\Docker\resources\bin'
  docker-compose up -d
  ```
* **Lâu dài:** Khởi động lại VS Code/Terminal. Nếu vẫn không được, cần thêm thủ công thư mục `C:\Program Files\Docker\Docker\resources\bin` vào System Variables (`PATH`) trong cài đặt Windows.

## 2. Xung đột cổng (Port Conflict) của Grafana
**Hiện tượng:** 
Khi Docker cố gắng khởi động container của Grafana, hệ thống báo lỗi không thể mở cổng `3000` (lỗi `ports are not available`).

**Nguyên nhân:**
Cổng `3000` mặc định của Grafana trong Docker đã bị chiếm dụng bởi một tiến trình `grafana.exe` đang chạy nền trực tiếp trên máy tính Windows của bạn (không thông qua Docker). Vì Windows chỉ cho phép một ứng dụng duy nhất sử dụng một cổng tại một thời điểm, Docker không thể gắn cổng 3000 cho container mới.

**Cách khắc phục (Đã áp dụng):**
Để không làm ảnh hưởng đến bản Grafana đang chạy trên Windows của bạn, chúng ta đã chỉnh sửa file `observability/docker-compose.yml`, đổi cổng phơi bày ra bên ngoài (Host port) của Grafana container từ `3000` sang `3001`.

```yaml
  grafana:
    image: grafana/grafana:latest
    container_name: autoops-grafana
    ports:
      - "3001:3000" # <-- Đổi từ 3000:3000 thành 3001:3000
```

## 3. Kết quả và Truy cập
Sau khi áp dụng các cách khắc phục trên, 2 container `autoops-prometheus` và `autoops-grafana` đã khởi động thành công trên nền tảng Docker.

Bạn có thể truy cập hệ thống qua các địa chỉ sau:
* **Prometheus:** [http://localhost:9090](http://localhost:9090)
* **Grafana:** [http://localhost:3001](http://localhost:3001) 
  * Tên đăng nhập mặc định: `admin`
  * Mật khẩu mặc định: `admin` (Sẽ được yêu cầu đổi mật khẩu ở lần đăng nhập đầu tiên)
