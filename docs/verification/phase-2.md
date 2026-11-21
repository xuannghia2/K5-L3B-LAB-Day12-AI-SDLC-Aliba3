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

Chi tiết giao diện và lý do cập nhật test P1: [bàn giao](../gather-phase-2-xuannghia2.md).
