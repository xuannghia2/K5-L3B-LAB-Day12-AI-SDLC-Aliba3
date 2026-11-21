# Hợp đồng tích hợp (nên chốt sớm; hình thức do nhóm chọn)

Điền trong 15 phút kickoff (hoặc thay bằng một mục trong README / một bảng trên giấy, miễn cả nhóm cùng thống nhất):
1. **Schema file kho** — khớp mục G của PRD-0 (kho ghi khi `gather_end`) + một file kho mẫu hợp lệ: `inventory.sample.json`.
2. **Giao diện giữa `sim/*` và `client/ui`** — trạng thái nào UI được đọc, lệnh nào UI gửi vào.
3. **Danh sách sự kiện** — tên, `data`, ai phát, ai nghe (gather: `gather`, `node_regrown`, `hold_full`, `fish_caught`, `gather_end`...; quan: theo mục E của PRD-0).

Khi đổi hợp đồng sau này: báo cả nhóm và ghi lại lý do (ADR hoặc ghi chú, tùy chọn).

## Migration v1.2 — Ticket-03

Adapter/gather mới và thứ tự bật được ghi ở [ADR-0001](../adr/0001-fresh-inventory-migration.md).
Schema cá thể: `{"items":[{"id":"I1","kind":"ca_linh","fresh":100}]}`; kho rỗng `{"items":[]}`.
Bản mẫu kho đếm phía trên vẫn dành cho v1.1 đang chạy; không dùng nó làm fixture v1.2.
Chưa ghi nhận nhóm đã tích hợp hai đầu v1.2; xem [bàn giao](../gather-phase-3-xuannghia2.md).
