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
| G3-UI-HOLD — client cá thể | Giỏ UI nhận chuỗi v1.1 và object {kind,fresh}; vật phẩm dưới ngưỡng ươn đổi màu | Test live/freshness | Chưa bật mặc định v1.2, chưa tích hợp quán/day |
| V1.2-MAIN / QUAN / DAY / HUD / TAG | Bật mặc định và smoke hai tiến trình/day, giữ chỗ/giá, HUD, tag | Chưa có | Chưa đạt tích hợp nhóm; chờ module quán/ngày/UI |

[ADR](../adr/0001-fresh-inventory-migration.md) và [bàn giao API](../gather-phase-3-xuannghia2.md).

## QA độc lập — justcoffeee (21/11/2026)

Kiểm lại migration kho cá thể v1.2 do xuannghia2 bàn giao, bằng test riêng [`tests/test_qa_p3_migration.py`](../../tests/test_qa_p3_migration.py) (12 test, không phụ thuộc gather/quan, chạy được trên Windows không cần `python3`).
Tuning: `data/freshness-p3.json` (initial 100, giỏ 0.5/s, kho 0.25/s, `spoiled_below` 30).

| Nhãn QA | Cách kiểm | Bằng chứng | Kết quả |
|---|---|---|---|
| QA3-T30 — ngưỡng 30 | Giỏ: sau 8400 tick fresh == 30.0, chưa ươn; tick 8401 phát `spoiled` đúng 1 lần. Kho: tick 16801. Sàn 0 | [p3-tests](../proof/phase-3/justcoffeee/p3-tests.txt) | Đạt |
| QA3-RT — roundtrip | Ghi/đọc kho v1.2 ở 5 điểm cắt (1, 777, 1234, 8399, 8400) rồi nạp ledger mới: tick ươn không lệch; ghi sắp id, không làm tròn 29.9999 | [p3-tests](../proof/phase-3/justcoffeee/p3-tests.txt) | Đạt |
| QA3-SCHEMA | Từ chối kho đếm, id trùng/rỗng/không phải chuỗi, thiếu/thừa khóa, kind lạ, fresh âm/>100/NaN/inf/bool/chuỗi, khóa gốc thừa; v1.1 vẫn nhận kho đếm | [p3-tests](../proof/phase-3/justcoffeee/p3-tests.txt) | Đạt |
| QA3-ID | Nạp I7, I2 → id mới I8, I9 | [p3-tests](../proof/phase-3/justcoffeee/p3-tests.txt) | Đạt |
| QA3-REPRO | Chạy lại `tools/verify_gather_p3.py`: 5 ca, cùng seed giống byte, sha256 trùng khớp báo cáo của xuannghia2 | [rerun](../proof/phase-3/justcoffeee/verify-gather-p3-rerun.json) | Đạt |
| QA3-REG | `test_qa_p3_migration` + `test_freshness` + `test_gather_p3` + `test_team_check` | [p3-tests](../proof/phase-3/justcoffeee/p3-tests.txt) | 34/34 đạt |
| QA3-INTEG — quán/manifest | Lần đầu: `sim/quan.py` chưa có `fresh`/cá thể. Kiểm lại sau [139b2b8](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/139b2b8): xem mục "QA quán Phase 3" bên dưới | [quan-p3-tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt) | Quán đã nhận kho cá thể; manifest chung vẫn 1.1 nên **chưa bật v1.2 mặc định** |

Giới hạn: suite toàn repo trên máy Windows này lỗi 39 test do `headless_cmd` gọi `python3` (không có trên PATH), lỗi môi trường có sẵn, không do thay đổi P3. Chưa chạy smoke hai tiến trình gather → quan với v1.2 vì đầu quán chưa hỗ trợ.

## QA quán Phase 3 — justcoffeee (kiểm 139b2b8 của griin-03)

Profile v1.2 dựng trong tiến trình (contract_version 1.2 + `data/freshness-p3.json`), không sửa manifest chung. Giá theo tươi kiểm theo code hiện tại `floor(giá × fresh trung bình / 100)`; **chưa đối chiếu văn bản Ticket-03**. Test: [`tests/test_qa_p3_quan.py`](../../tests/test_qa_p3_quan.py) (10 test).

| Nhãn QA | Cách kiểm | Bằng chứng | Kết quả |
|---|---|---|---|
| QA3Q-2PROC | Gather cập bến ghi kho v1.2 → quán nạp file: snapshot tick 0 có đúng id/kind/fresh đủ chính xác; manifest 1.1 mặc định vẫn từ chối kho cá thể (exit 2) | [tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt), [probe](../proof/phase-3/justcoffeee/quan-p3-probe.txt) | Đạt (profile v1.2) |
| QA3Q-RESERVE | Giữ cá thể tươi nhất; cá thể đã giữ không cho khách sau (`no_dish`) | [tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt) | Đạt |
| QA3Q-COOK | Nấu tiêu đúng id đã giữ, `items` là cá thể; giá = floor(60 × 89.50 / 100) = 53 | [tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt), [probe](../proof/phase-3/justcoffeee/quan-p3-probe.txt) | Đạt theo code (công thức chờ đối chiếu ticket) |
| QA3Q-SPOIL | Kho hao 0.25/s; cá thể đã giữ ươn → `spoiled` location stock, đơn `unfulfillable`, nhả giữ | [tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt) | Đạt |
| **QA-P3-01** | v1.2: khách fixture gọi `lau_mam`, kho chỉ 1 `ca_loc`, nhấn E ở B1 → `cook_started` với `items: []`, giá đủ 200 (nấu không tốn nguyên liệu) | [tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt) | **Chưa đạt** — nặng |
| **QA-P3-02** | v1.1: khách fixture không ghi `order_status`/`reserved`, kho rỗng → validation bỏ qua, nấu được, kho −1 (biến thể QA-P2-02) | [tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt) | **Chưa đạt** |
| **QA-P3-03** | Hòa fresh: chọn `I10` trước `I2` (so chuỗi) thay vì thứ tự tự nhiên `ids.sort_by_id` | [tests](../proof/phase-3/justcoffeee/quan-p3-tests.txt), [probe](../proof/phase-3/justcoffeee/quan-p3-probe.txt) | **Chưa đạt** — nhỏ, ảnh hưởng tất định khi so với đề |
| QA3Q-REG | Toàn bộ suite có `python3` trên PATH | [all-tests](../proof/phase-3/justcoffeee/all-tests-139b2b8.txt) | 152 test OK, 3 expectedFailure (QA-P3-01..03) |

QA-P3-01..03 đánh dấu `expectedFailure` trong lớp `KnownBugsP3`; chủ sim/quan sửa xong thì bỏ đánh dấu. Chưa chạy smoke ngày (`day`) vì bộ điều phối ngày chưa có.
