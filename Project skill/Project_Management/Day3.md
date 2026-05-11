# Day 3 — Thu thập metric Windows (Windows Exporter)

## 1) Mục tiêu của Day 3

Sau khi hoàn thành Day 2 (đã dựng thành công Prometheus và Grafana qua Docker Compose), mục tiêu cốt lõi của Day 3 là **mang dữ liệu giám sát của máy chủ Windows vào trong Prometheus**.
Máy chủ của bạn (hay máy tính cá nhân đang dùng làm Server) sẽ không tự động gửi số liệu cấu hình CPU/RAM cho Prometheus. Chúng ta cần cài đặt một **Exporter**.

**Mục tiêu MVP cho hôm nay:**
- Cài đặt thành công `windows_exporter` trên máy tính Windows.
- Đảm bảo `windows_exporter` mở port `:9182/metrics` và trả về số liệu.
- Cấu hình Prometheus (file `prometheus.yml`) để nhận diện (scrape) metrics từ máy Windows này.
- Kiểm tra trạng thái Target trong Prometheus chuyển thành **UP**.

---

## 2) Những thứ cần học trước

### 2.1 Prometheus Exporter là gì?
- **Exporter** là một phần mềm trung gian. Nó lấy thông tin của phần mềm hoặc hệ điều hành (ở đây là Windows) và dịch chúng sang định dạng văn bản (text format) mà Prometheus có thể đọc hiểu.
- **Pull-based**: Prometheus sẽ chủ động "định kỳ" (thường là mỗi 15 giây) gọi đến địa chỉ `http://<IP-Windows>:9182/metrics` để lấy (pull) dữ liệu về.

### 2.2 Windows Exporter
- Là một agent chạy dưới dạng Windows Service.
- Nó có rất nhiều "collectors" (bộ thu thập). Tuy nhiên để tối ưu tài nguyên, chúng ta chỉ kích hoạt các collector cần thiết cho MVP: `cpu, memory, logical_disk, net, os, service, process`.

---

## 3) Việc cần làm trong Day 3 (Checklist)

### 3.1 Tải và Cài đặt Windows Exporter
- Truy cập kho lưu trữ GitHub của `prometheus-community/windows_exporter` (phần Releases).
- Tải file `.msi` mới nhất (ví dụ: `windows_exporter-1.27.x-amd64.msi`).
- Mở Command Prompt (với quyền **Administrator**) và chạy lệnh cài đặt để chỉ định các collectors cần thiết.
  *Ví dụ lệnh cài đặt:*
  ```cmd
  msiexec /i windows_exporter-1.27.1-amd64.msi ENABLED_COLLECTORS="cpu,cs,logical_disk,net,os,system,memory,service"
  ```
- **Lưu ý:** Lệnh này sẽ cài đặt `windows_exporter` như một Service tự động khởi chạy cùng Windows.

### 3.2 Kiểm tra Exporter hoạt động
- Mở trình duyệt trên máy Windows vừa cài, truy cập: `http://localhost:9182/metrics`
- Nếu bạn thấy một trang hiển thị rất nhiều dòng text kiểu như `windows_cpu_time_total{...} 12345`, nghĩa là exporter đã chạy thành công.

### 3.3 Cấu hình Tường lửa (Firewall)
- Mặc định Windows Firewall có thể chặn kết nối đến port `9182`.
- Bạn cần mở port 9182 Inbound (Inbound Rule) trong Windows Defender Firewall để container Prometheus (đang chạy qua Docker) có thể truy cập được.
- Có thể dùng PowerShell (Run as Administrator):
  ```powershell
  New-NetFirewallRule -DisplayName "Windows Exporter" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 9182
  ```

### 3.4 Cấu hình Prometheus Scrape
- Mở file `prometheus.yml` (bạn đã tạo ở Day 2).
- Thêm job mới vào phần `scrape_configs` để chỉ định Prometheus đi lấy dữ liệu từ máy Windows:
  ```yaml
  scrape_configs:
    - job_name: 'windows_host'
      static_configs:
        - targets: ['<IP_CỦA_MÁY_WINDOWS>:9182']
  ```
  *(Lưu ý: Thay `<IP_CỦA_MÁY_WINDOWS>` bằng IP thật trong mạng LAN, ví dụ `192.168.1.10`. Đừng dùng `localhost` vì Prometheus đang nằm trong Docker container, `localhost` của nó không phải là máy Windows của bạn).*
- Khởi động lại container Prometheus: `docker compose restart prometheus`

---

## 4) Kiểm tra và Nghiệm thu (Definition of Done - DoD)

- [ ] Truy cập `http://localhost:9182/metrics` hiển thị dữ liệu thành công.
- [ ] Truy cập Prometheus UI (`http://localhost:9090`).
- [ ] Vào menu **Status** -> **Targets**.
- [ ] Tìm mục `windows_host`. Trạng thái phải hiển thị là **`UP`** màu xanh lá.
- [ ] Vào menu **Graph** của Prometheus, gõ `windows_cpu_time_total` và ấn Execute, bạn phải thấy dữ liệu dạng đồ thị (Graph) hoặc bảng (Table).

---

## 5) Timebox gợi ý trong Day 3

- **30 phút**: Tải và cài đặt `windows_exporter` qua CMD.
- **15 phút**: Test trình duyệt và mở port tường lửa.
- **30 phút**: Chỉnh sửa file `prometheus.yml` và restart Docker container.
- **15 phút**: Check Status "UP" trên Prometheus và gõ thử các query PromQL cơ bản.

## Bước tiếp theo (Preview Day 4)
Sau khi có dữ liệu thô trong Prometheus, ngày mai chúng ta sẽ kết nối Grafana để vẽ các Dashboard đẹp mắt (Biểu đồ CPU, RAM, Disk) nhằm phục vụ việc giám sát trực quan!
