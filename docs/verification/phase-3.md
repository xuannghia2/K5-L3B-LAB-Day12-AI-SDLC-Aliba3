# Kiểm chứng Phase 3 — phần xuannghia2

Nhãn G3 là mã nội bộ dẫn luật Ticket-03, không tự nhận mã AC chính thức của lớp.

| Nhãn / luật | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| G3-SCHEMA — kho cá thể | Phân biệt version; từ chối kho đếm, id trùng, kind/fresh sai; ghi nguyên tử | [test](../proof/phase-3/xuannghia2/gather-tests.txt) | Đạt adapter v1.2 |
| G3-DECAY — hao/ươn | Hao đầu tick, ngưỡng đúng 30 sau 8400 bước; đọc lại file rồi hao kho; spoiled một lần theo id | [test](../proof/phase-3/xuannghia2/gather-tests.txt), [threshold](../proof/phase-3/xuannghia2/threshold.log) | Đạt |
| G3-NEW — nhặt/id | Nhặt fresh đầy, hao bước sau, mỗi yield một id; allocator tăng tiếp | [pickup](../proof/phase-3/xuannghia2/pickup.log), [test](../proof/phase-3/xuannghia2/gather-tests.txt) | Đạt |
| G3-LOSS — LIFO | Spoil trước ngất; hit/faint mang cá thể đúng thứ tự nhặt ngược | [faint](../proof/phase-3/xuannghia2/faint.log), [test](../proof/phase-3/xuannghia2/gather-tests.txt) | Đạt |
| G3-PAUSE | Pause không hao; resume chạy tick đó | [test](../proof/phase-3/xuannghia2/gather-tests.txt) | Đạt |
| G3-EXPORT | Kho sorted id, fresh đủ precision khớp event/snapshot; tick limit giữ file cũ | [dock](../proof/phase-3/xuannghia2/dock.log), [kho](../proof/phase-3/xuannghia2/dock-inventory.json) | Đạt profile kiểm thử gather v1.2 |
| G3-DET | Cùng seed so byte output | [sha256](../proof/phase-3/xuannghia2/verification-report.json) | Đạt |
| G3-REG | 17 test P3; 100 test có phạm vi; suite 104 test | [scope](../proof/phase-3/xuannghia2/gather-tests.txt), [suite](../proof/phase-3/xuannghia2/gather-stage-tests.txt) | 17/17 và 100/100 đạt; toàn repo 103/104, lỗi TEAM cũ |
| V1.2-MAIN / QUAN / DAY / HUD / TAG | Bật mặc định và smoke hai tiến trình/day, giữ chỗ/giá, HUD, tag | Chưa có | Chưa đạt tích hợp nhóm; chờ module quán/ngày/UI |

[ADR](../adr/0001-fresh-inventory-migration.md) và [bàn giao API](../gather-phase-3-xuannghia2.md).
