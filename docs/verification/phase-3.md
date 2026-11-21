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
| QA3-INTEG — quán/manifest | `game.contract.json` vẫn `contract_version` 1.1; `chonoi/sim/quan.py` chưa có xử lý `fresh`/cá thể | grep tại commit kiểm | **Chưa đạt**: chờ sim/quan P3 trước khi bật v1.2 |

Giới hạn: suite toàn repo trên máy Windows này lỗi 39 test do `headless_cmd` gọi `python3` (không có trên PATH), lỗi môi trường có sẵn, không do thay đổi P3. Chưa chạy smoke hai tiến trình gather → quan với v1.2 vì đầu quán chưa hỗ trợ.
