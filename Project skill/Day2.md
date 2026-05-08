# Day 2 — Dựng Observability Stack (Docker Compose) trên Windows

## Mục tiêu của ngày 2 (Definition of Done)

- Chạy được **Prometheus + Grafana** bằng đúng **1 lệnh**: `docker compose up -d`
- Có **persist data** (restart máy/containers không mất cấu hình Grafana và dữ liệu Prometheus)
- Truy cập được:
  - Grafana: `http://localhost:3000`
  - Prometheus: `http://localhost:9090`
- Grafana đã có sẵn **Prometheus datasource** (tự provision), vào Explore query được.
- Chạy được **windows_exporter** trên Windows và trong Prometheus Targets thấy `windows` = **UP**.

> Ghi chú: `cadvisor` và `ai_agent_backend` có thể để **tắt** trong Day 2 nếu bạn muốn đi đúng thứ tự; nhưng mình vẫn để sẵn trong compose để bạn bật lên khi cần.

---

## Chuẩn bị (Windows)

### Yêu cầu tối thiểu

- Windows 10/11
- Docker Desktop (khuyến nghị bản mới)
  - Bật **Use WSL 2** (Settings → General) nếu có
- PowerShell
- Go (để build `windows_exporter` từ source bạn đã gửi)

### Kiểm tra nhanh Docker chạy ổn

Mở PowerShell tại thư mục repo của bạn, chạy:

```powershell
docker version
docker compose version
```

Nếu ra version bình thường là OK.

---

## Bước 1 — Tạo cấu trúc thư mục cho Day 2

Trong repo, tạo một thư mục stack (đặt tên rõ ràng để không lẫn với code backend sau này). Khuyến nghị:

```text
observability/
  docker-compose.yml
  prometheus/
    prometheus.yml
  grafana/
    provisioning/
      datasources/
        datasource.yml
```

Bạn có thể tạo bằng PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path .\observability\prometheus | Out-Null
New-Item -ItemType Directory -Force -Path .\observability\grafana\provisioning\datasources | Out-Null
```

---

## Bước 2 — Tạo file `observability/docker-compose.yml`

Tạo file `observability/docker-compose.yml` với nội dung sau:

```yaml
version: "3.8"

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: autoops-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"
      - "--storage.tsdb.path=/prometheus"
      - "--web.enable-lifecycle"
    restart: unless-stopped
    networks:
      - autoops-net

  grafana:
    image: grafana/grafana:latest
    container_name: autoops-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    depends_on:
      - prometheus
    restart: unless-stopped
    networks:
      - autoops-net

  # Tuỳ chọn (dùng khi bạn muốn demo metric container; không bắt buộc Day 2)
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: autoops-cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    restart: unless-stopped
    networks:
      - autoops-net
    profiles: ["optional"]

volumes:
  prometheus_data:
  grafana_data:

networks:
  autoops-net:
    driver: bridge
```

**Giải thích nhanh (để bạn khỏi nhầm khi debug)**

- Persist:
  - Prometheus data: volume `prometheus_data`
  - Grafana data: volume `grafana_data`
- Grafana provisioning mount read-only: `./grafana/provisioning:/etc/grafana/provisioning:ro`
- `profiles: ["optional"]` giúp `cadvisor` không chạy mặc định.

---

## Bước 3 — Tạo file `observability/prometheus/prometheus.yml`

Tạo `observability/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus tự scrape chính nó
  - job_name: "prometheus"
    static_configs:
      - targets: ["prometheus:9090"]

  # Grafana không export metrics Prometheus mặc định (không cần scrape)

  # Tuỳ chọn: cAdvisor (chỉ có khi bạn bật profile optional)
  - job_name: "cadvisor"
    static_configs:
      - targets: ["cadvisor:8080"]

  # Placeholder cho Day 3 (windows_exporter)
  # Vì bạn đã có source `windows_exporter-master/`, Day 2 có thể build + chạy luôn exporter.
  # Target này thường chạy được trên Docker Desktop để scrape exporter chạy trên máy host.
  - job_name: "windows"
    static_configs:
      - targets: ["host.docker.internal:9182"]
```

> Nếu bạn đã chạy `windows_exporter` đúng, target `windows` sẽ **UP** ngay trong Day 2.

---

## Bước 4 — Provision Prometheus datasource cho Grafana

Tạo file `observability/grafana/provisioning/datasources/datasource.yml`:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
```

Provisioning giúp bạn “lên là có datasource ngay”, tránh thao tác tay khi demo.

---

## Bước 5 — Build + chạy `windows_exporter` (từ source bạn đã gửi)

> Hiện tại trong repo của bạn không có sẵn `.msi`/`.exe` release, nên Day 2 sẽ chạy theo cách **build từ source**.

### 5.1 Cài Go và kiểm tra

Mở PowerShell và kiểm tra:

```powershell
go version
```

Nếu chưa có Go, cài Go (bản mới) rồi chạy lại lệnh trên.

### 5.2 Build `windows_exporter.exe`

Từ repo root:

```powershell
cd .\windows_exporter-master\windows_exporter-master
go build -o windows_exporter.exe .\cmd\windows_exporter
```

Sau khi build xong, bạn sẽ có file:

- `windows_exporter-master/windows_exporter-master/windows_exporter.exe`

### 5.3 Chạy exporter (port 9182) và kiểm tra endpoint `/metrics`

Chạy exporter (giữ cửa sổ PowerShell này mở để xem log):

```powershell
.\windows_exporter.exe --web.listen-address=":9182"
```

Mở trình duyệt và kiểm tra:

- `http://localhost:9182/metrics`

Nếu trang trả về metrics text là OK.

### 5.4 (Nếu bị chặn) mở firewall inbound cho port 9182

Chạy PowerShell (Run as Administrator):

```powershell
New-NetFirewallRule -DisplayName "windows_exporter 9182" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 9182
```

---

## Bước 6 — Chạy stack (Prometheus + Grafana)

Chạy từ repo root:

```powershell
cd .\observability
docker compose up -d
```

Kiểm tra containers:

```powershell
docker compose ps
```

Nếu bạn muốn bật `cadvisor` (tuỳ chọn):

```powershell
docker compose --profile optional up -d
```

---

## Bước 7 — Verify (rất quan trọng để “chắc chắn DoD”)

### 7.1 Kiểm tra Prometheus UI

- Mở `http://localhost:9090`
- Vào **Status → Targets**
  - `prometheus` phải **UP**
  - `windows` phải **UP** (nếu bạn đã chạy `windows_exporter` ở bước 5)
  - `cadvisor` chỉ **UP** nếu bạn bật profile optional

Test query nhanh:

- Vào **Graph** và query:
  - `up`

### 7.2 Kiểm tra Grafana UI

- Mở `http://localhost:3000`
- Login:
  - user: `admin`
  - pass: `admin`
- Vào **Connections → Data sources**
  - thấy datasource **Prometheus** và trạng thái OK
- Vào **Explore**, chọn Prometheus và chạy query:
  - `up`

Nếu query `up` trả về series là OK.

---

## Bước 8 — Những lỗi hay gặp trên Windows (Troubleshooting)

### Grafana/Prometheus không lên (container Exit)

Chạy:

```powershell
docker compose logs --tail 200 prometheus
docker compose logs --tail 200 grafana
```

Các nguyên nhân phổ biến:

- **Sai đường dẫn mount**: bạn phải chạy lệnh trong thư mục `observability/` (để `./prometheus/...` đúng).
- **YAML sai format**: thụt dòng/quote sai → container báo lỗi parse.

### Port bị chiếm (3000 hoặc 9090)

Nếu thấy lỗi “port is already allocated”, đổi port mapping trong `docker-compose.yml`, ví dụ:

- Grafana: `"3001:3000"`
- Prometheus: `"9091:9090"`

Rồi chạy lại:

```powershell
docker compose up -d
```

### `host.docker.internal` không hoạt động

Trường hợp hiếm. Workaround:

- Thay `host.docker.internal:9182` bằng **IP LAN** của máy Windows đang chạy exporter, ví dụ: `192.168.1.10:9182`.

### Muốn “reset sạch” và chạy lại

Nếu bạn muốn xoá containers + volumes (mất data Grafana/Prometheus):

```powershell
docker compose down -v
docker compose up -d
```

---

## Output cuối ngày 2 (bạn nên có trong repo)

- `observability/docker-compose.yml`
- `observability/prometheus/prometheus.yml`
- `observability/grafana/provisioning/datasources/datasource.yml`
- Ảnh chụp/ghi chú xác minh:
  - Prometheus Targets: `prometheus` UP
  - Grafana datasource OK và query `up` chạy được

---

## Chuẩn bị cho Ngày 3 (nhẹ, không bắt buộc làm hôm nay)

- Chốt máy/VM Windows nào sẽ cài `windows_exporter`
- Ghi lại port dự kiến (mặc định `9182`) và rule firewall nếu cần
