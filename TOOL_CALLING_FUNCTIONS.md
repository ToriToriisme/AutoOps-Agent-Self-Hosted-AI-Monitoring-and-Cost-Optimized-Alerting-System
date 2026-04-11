# Định nghĩa các Tool (Function Calling)

Các hàm Python thực tế mà AI có quyền gọi:

```python
def restart_docker_container(container_id: str):
    """Khởi động lại một Docker container bị treo."""
    # Logic dùng thư viện docker-py

def clear_memory_cache():
    """Giải phóng cache RAM hệ thống."""
    # Logic chạy lệnh: sync; echo 3 > /proc/sys/vm/drop_caches
```
