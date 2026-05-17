# Day 4 — Xây dựng Dashboard Grafana cho Windows (MVP)

## 1) Mục tiêu của Day 4

Trong Day 3, dữ liệu giám sát của Windows đã chảy thành công vào Prometheus (target trạng thái `UP`). Tuy nhiên, Prometheus chỉ chứa dữ liệu thô (chuỗi thời gian) rất khó đọc.
Hôm nay, mục tiêu cốt lõi của bạn là **trực quan hóa dữ liệu đó thành các biểu đồ đẹp mắt trên Grafana**.

**Mục tiêu MVP cho hôm nay:**

- Kết nối thành công Prometheus làm Data Source cho Grafana.
- Tạo một Dashboard giám sát sức khỏe của máy Windows (tối thiểu gồm: CPU, RAM, Disk, Trạng thái Up/Down).
- Thêm được Biến (Variables) vào Dashboard để có thể chọn máy chủ linh hoạt.
- Xuất (Export) Dashboard ra file `.json` để lưu trữ mã nguồn cho lúc đi nộp bài.

---

## 2) Những thứ cần học trước

### 2.1 Mối quan hệ giữa Prometheus và Grafana

- **Prometheus** đóng vai trò là "Backend lưu trữ", chuyên thu thập và lưu giữ các con số.
- **Grafana** đóng vai trò là "Frontend hiển thị", nó sẽ truy vấn (query) vào Prometheus và biến các con số khô khan đó thành đồ thị.
- Bạn cần khai báo Prometheus là **Data Source** (Nguồn dữ liệu) bên trong Grafana thì hai bên mới nói chuyện được với nhau.

### 2.2 Dashboard và PromQL

- Mỗi một biểu đồ (Panel) trên Grafana đều được vẽ ra dựa trên một câu lệnh **PromQL** (Prometheus Query Language).
- Ví dụ:
  - Xem máy chủ còn sống hay chết: `up{job="windows_host"}`
  - Xem RAM đang dùng: Gõ công thức tính toán lượng RAM tiêu thụ dựa vào các số liệu trả về từ `windows_exporter`.

---

## 3) Việc cần làm trong Day 4 (Checklist)

### 3.1 Thiết lập Prometheus làm Data Source

- Truy cập vào giao diện Grafana của bạn: `http://localhost:3001` (Tài khoản/Mật khẩu mặc định là `admin`/`admin`).
- Từ menu bên trái, chọn biểu tượng bánh răng **(Configuration)** hoặc **Connections** -> **Data Sources**.
- Bấm **Add data source** và chọn **Prometheus**.
- Ở mục **URL**, nhập địa chỉ của Prometheus. Do Grafana và Prometheus đang chạy chung mạng Docker, bạn có thể điền: `http://prometheus:9090`.
- Kéo xuống dưới cùng và bấm **Save & Test**. Nếu hiện thông báo "Data source is working" màu xanh lá là thành công.

### 3.2 Nhập (Import) Dashboard Windows dựng sẵn
Thay vì phải cặm cụi tự vẽ từng biểu đồ bằng tay rất mất thời gian, chúng ta có thể sử dụng Dashboard do cộng đồng thiết kế sẵn:

- Chọn dấu **+** ở menu bên trái -> **Import**.
- Nhập ID của Dashboard Windows Exporter chuẩn: **`14694`** hoặc **`10467`** (đây là 2 mẫu Dashboard cực đẹp và chuẩn xác trên thư viện Grafana).
- Bấm **Load**.
- Ở phần cấu hình phía dưới, chọn **Prometheus** (Data source bạn vừa tạo ở bước 3.1) cho mục Prometheus Data Source.
- Bấm **Import**. Bạn sẽ ngay lập tức nhìn thấy bảng điều khiển giám sát máy chủ Windows của mình sáng rực rỡ!

### 3.3 Tùy biến Dashboard theo MVP
Dù đã import Dashboard có sẵn, bạn nên tối ưu lại theo yêu cầu MVP của đồ án để loại bỏ các Panel rườm rà không cần thiết:

- Xóa bớt các biểu đồ không nằm trong scope. Chỉ giữ lại đúng 5 biểu đồ trọng tâm:
  - CPU Usage (%).
  - Memory Usage (RAM đã dùng / Trống).
  - Logical Disk Space (Dung lượng ổ C/D).
  - Network Traffic (Tốc độ mạng tải Lên/Xuống).
  - Uptime (Thời gian máy tính hoạt động).
- Ở góc trên cùng của Dashboard, kiểm tra xem đã có biến (Variables) tên là `instance` hoặc `job` để cho phép chọn máy tính chưa (thường dashboard có sẵn đã tự làm cho bạn).

### 3.4 Export Dashboard để lưu trữ

- Ở góc trên màn hình Dashboard, bấm vào biểu tượng **Share dashboard** (hoặc hình bánh răng Settings).
- Chuyển sang tab **Export**.
- Chọn **Export for sharing externally** và bấm **Save to file**.
- Một file `.json` sẽ được tải về. Hãy copy file này bỏ vào thư mục dự án của bạn (ví dụ thư mục `observability/grafana/dashboards/`) để sau này làm minh chứng và backup cấu hình.

---

## 4) Kiểm tra và Nghiệm thu (Definition of Done - DoD)

- [ ] Cấu hình thành công Prometheus làm Data Source.
- [ ] Màn hình Dashboard hiện đầy đủ các chỉ số: CPU, RAM, Disk, Net, System Up.
- [ ] Số liệu trên biểu đồ khớp (hoặc xấp xỉ) với số liệu bạn xem trong Task Manager của Windows.
- [ ] Đã có sẵn file xuất bản `.json` của Dashboard nằm trong thư mục code.

---

## 5) Timebox gợi ý trong Day 4

- **15 phút**: Add Data source và test kết nối thành công.
- **20 phút**: Tìm kiếm và Import Windows Dashboard có sẵn từ cộng đồng (ID: 14694).
- **25 phút**: Xóa bớt các panel không cần thiết để tạo thành một Dashboard MVP tinh gọn và rõ ràng.
- **10 phút**: Export file JSON, đổi tên (ví dụ: `windows-mvp-dashboard.json`) và lưu vào source code.

## Bước tiếp theo (Preview Day 5)

Bạn đã có Dashboard giám sát xịn xò. Nhưng không ai có thể ngồi nhìn màn hình Grafana 24/7 cả. Ngày mai chúng ta sẽ cấu hình **Grafana Alerting**, đặt ra các ranh giới "nguy hiểm" (ví dụ: ổ cứng đầy 90%) và tự động bắn ra cảnh báo (Alert) để gửi về hệ thống AutoOps Agent!
