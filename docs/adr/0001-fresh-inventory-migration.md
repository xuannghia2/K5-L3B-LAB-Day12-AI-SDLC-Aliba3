# ADR-0001 — Kho cá thể v1.2, tích hợp hai bước

- Ngày: 21/11/2026; phần triển khai xuannghia2 theo Ticket-03.
- Trạng thái: adapter/gather triển khai; bật mặc định v1.2 chờ quán tương thích.

Ticket-03 bắt buộc đổi kho đếm sang cá thể. Giữ đường chạy v1.1 trong khi đưa adapter vào,
tránh bật một đầu v1.2 khiến quán đang dùng dict bị hỏng. Adapter chọn schema qua tham số version;
v1.2 phải từ chối kho đếm, không tự chuyển dữ liệu đầu vào cũ.

FreshnessLedger dùng phân số cho hao tươi và nhánh ngưỡng; giao diện chỉ có dict JSON id/kind/fresh.
Khôi phục lưới tick sau roundtrip chỉ khi giá trị lưới có cùng biểu diễn float với số đã đọc.
JSON/file không được làm tròn fresh còn ba chữ số vì sẽ làm lệch tick ươn sau bàn giao.

| Module | Tác động | Kiểm thử/phụ thuộc |
|---|---|---|
| inventory/freshness — xuannghia2 | Đọc/ghi hai schema rõ version, kiểm id/kind/fresh, id tăng tiếp | schema, ngưỡng 30, roundtrip, ghi nguyên tử |
| gather — xuannghia2 | Hold cá thể, hao đầu tick, nhặt fresh đầy, lost LIFO cá thể | pause, spoil, ngất, bàn giao không hao thêm |
| quan — theo TEAM.md | Stock cá thể, giữ id tươi nhất, giữ lại/giá theo tươi | Chủ module cần tích hợp trước bật v1.2 |
| day/UI — cần nhóm tích hợp | Dùng chung IdAllocator xuyên pha/ngày, đọc fresh | Chưa xác nhận module này đã hoàn thành |

Thứ tự: push adapter tương thích cũ → push gather có kiểm thử với tuning freshness →
kiểm tra quán trên GitHub, smoke hai đầu → mới bật contract_version 1.2, cập nhật fixture và log.
Bản kiểm tra GitHub đầu phiên: main 2fd97cc, chưa thấy commit quán P3.
