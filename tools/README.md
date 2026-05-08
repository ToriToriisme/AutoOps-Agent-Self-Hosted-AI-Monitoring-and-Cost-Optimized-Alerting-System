# tools

Thư mục chứa các tool/script đã được **whitelist** để AutoOps Agent có thể gọi một cách an toàn.

## Nguyên tắc

- Chỉ chạy script trong `tools/powershell/`
- Input phải được validate theo allowlist/blocklist
- Script trả về **1 dòng** theo chuẩn:
  - `SUCCESS: <tool> completed on <target>.`
  - `ERROR: <short reason>.`

