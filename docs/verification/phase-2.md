# Kiểm chứng Phase 2 — phần xuannghia2

Chỉ ghi phần gather và phụ thuộc shared đã kiểm chứng, không xác nhận DoD toàn nhóm.
Mã G2 là nhãn nội bộ, dẫn mục tương ứng của Ticket-02.

| Nhãn / nguồn | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| G2-FISH — 1.1, 4.3, 4.5 | 8 đàn, tốc độ, tuổi đổi hướng, phản xạ, lịch/cap/điểm sinh, fixture tĩnh | [test](../proof/phase-2/xuannghia2/gather-tests.txt), [log](../proof/phase-2/xuannghia2/swim.log) | Đạt |
| G2-MONSTER — 1.2, 4.5 | Tuần tra/chase, chọn hit, LIFO, invuln, recoil đủ bước, ngạt trước hit | [test](../proof/phase-2/xuannghia2/gather-tests.txt), [ngất](../proof/phase-2/xuannghia2/monster-faint.log) | Đạt |
| G2-KHO — 1.1, 1.3 | Hai tiến trình, ca_keo/keo_neo qua file items và quán đọc tick 0 | [gather](../proof/phase-2/xuannghia2/integration-gather.log), [quan](../proof/phase-2/xuannghia2/integration-quan.log) | Đạt |
| G2-PAUSE — 4.2 | Pause chỉ tăng tick ngoài, resume chạy gameplay cùng bước | [test CLI](../proof/phase-2/xuannghia2/gather-tests.txt) | Đạt backend lượt độc lập |
| G2-UPGRADE — 2 | Dựng gather theo active_upgrades, M2 từ ngày 3, không sửa tuning gốc | [test](../proof/phase-2/xuannghia2/gather-tests.txt) | Đạt giao diện gather; Shop/day chưa tích hợp |
| G2-INPUT — 4.3 | Fixture mâu thuẫn trả 2 trước tạo output | [test CLI](../proof/phase-2/xuannghia2/gather-tests.txt) | Đạt các trường gather đã kiểm |
| G2-REGRESSION | 81 test có phạm vi; toàn suite 85 test | [scope](../proof/phase-2/xuannghia2/gather-tests.txt), [toàn bộ](../proof/phase-2/xuannghia2/all-tests.txt) | 81/81 đạt; toàn repo 84/85, lỗi TEAM có sẵn |
| DAY/SHOP/UI/benchmark/tag | Chuyển pha, Shop, nhiều ngày, HUD, hiệu năng một Ngày, tag nhóm | Chưa có | Chưa xác nhận, cần tích hợp |
| G2-UI — pause/Cá Sấu/HUD | Client P, overlay paused, hiển thị monsters và giỏ an toàn | Test live P2 | 42 test P2/P3/live/freshness đạt trên Windows |

Chi tiết giao diện và lý do cập nhật test P1: [bàn giao](../gather-phase-2-xuannghia2.md).

## QA bổ sung — justcoffeee (21/11/2026, làm muộn sau mốc Phase 2)

Kiểm trên code hiện tại (main `802f7c1`), **không phải** trạng thái lúc hết giờ Phase 2. Đối chiếu số chuẩn trong `game.contract.json` và thứ tự xử lý ghi ở docstring `chonoi/sim/quan.py` (PRD-0 mục F); chưa đọc trực tiếp văn bản Ticket-02.

| Nhãn QA | Cách kiểm | Bằng chứng | Kết quả |
|---|---|---|---|
| QA2-REG — hồi quy toàn repo | Toàn bộ suite, có `python3` trên PATH (venv tạm) | [all-tests](../proof/phase-2/justcoffeee/all-tests.txt) | 134 test: 133 đạt + 1 lỗi đã biết (QA2-FIX) |
| QA2-LAYOUT | Contract có B1/B2, T1–T4, 6 món, nguyên liệu `ca_keo`/`keo_neo`; hai bếp không cùng trong bán kính tương tác | [quan-tests](../proof/phase-2/justcoffeee/quan-tests.txt) | Đạt |
| QA2-TABLE | Khách vào bàn trống id nhỏ nhất T1→T4; bàn đầy thì bỏ lượt, không `no_dish`; bàn rời do hết kiên nhẫn được dùng lại cùng tick | [quan-tests](../proof/phase-2/justcoffeee/quan-tests.txt) | Đạt |
| QA2-RESERVE | Kho đủ 1 đơn: khách 2 nhận `no_dish`; `lau_mam` thiếu bất kỳ 1 trong 5 nguyên liệu thì không được chọn | [quan-tests](../proof/phase-2/justcoffeee/quan-tests.txt) | Đạt |
| QA2-STOVE | Hai bếp nấu song song hai đơn cũ nhất (B1→T1, B2→T2); trừ đúng công thức, chốt giá, `cook_ticks_left` = cook_s·60 | [quan-tests](../proof/phase-2/justcoffeee/quan-tests.txt) | Đạt |
| QA2-PAY | Chu trình đủ: tip = floor(giá·0.2), `paid.amount` = giá + tip, uy tín +0.2 | [quan-tests](../proof/phase-2/justcoffeee/quan-tests.txt) | Đạt |
| **QA2-FIX (QA-P2-01)** | Khách nạp từ scenario (đang chờ, có món) không có `order_status` nên bếp idle bỏ qua; headless không phát `cook_started` | [scenario](../proof/phase-2/justcoffeee/qa-p2-01-scenario.json), [inputs](../proof/phase-2/justcoffeee/qa-p2-01-inputs.json), [jsonl](../proof/phase-2/justcoffeee/qa-p2-01-fixture-customer.log), `test_qa_p2_quan.FixtureCustomers` (`expectedFailure`) | **Chưa đạt** — báo chủ sim/quan (griin-03); test ẩn dùng fixture khách có thể trượt |

Test mới: [`tests/test_qa_p2_quan.py`](../../tests/test_qa_p2_quan.py) (12 test). Khi sửa QA-P2-01, bỏ `@unittest.expectedFailure` để test thành kiểm hồi quy.
