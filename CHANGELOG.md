# Changelog
## Unreleased

### Phase 3 — chuẩn bị schema v1.2 (chưa bật mặc định)

- **Breaking khi chọn v1.2:** `items` đổi từ map số lượng sang mảng `{id,kind,fresh}`; hold và lost dùng cá thể. Kho đếm bị từ chối ở đầu đọc v1.2.
- Thêm FreshnessLedger, hao giỏ đầu tick, spoiled theo id và cấp I liên tục; fresh trong JSONL/file không còn làm tròn ba chữ số.
- Fixture v1.2 phải cấp id duy nhất, fresh hữu hạn trong [0,100]. Fixture count/string cũ tiếp tục dành cho đường v1.1 trong thời gian chuyển.
- Manifest chung vẫn v1.1 đến khi quán tương thích; chưa có smoke hai tiến trình/day v1.2. Xem docs/adr/0001-fresh-inventory-migration.md.
