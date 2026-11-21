# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt:
- Điều cần chỉnh cho phase sau:

## Phần Cấn Xuân Nghĩa / xuannghia2 — sim/gather (21/11/2026)

Mã G bên dưới là nhãn kiểm thử nội bộ, đối chiếu PRD-0 mục E/F/G sau khi đăng nhập lab board; không tự đặt mã AC chính thức.

| Nhãn | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| G-OXY | Mặt nước, cạn oxy, chuyển vùng, ngạt/ngất, ưu tiên kết thúc | [test luật](../proof/phase-1/xuannghia2/gather-tests.txt), [ngất](../proof/phase-1/xuannghia2/faint.log) | Đạt theo PRD-0 mục F |
| G-NODE | Gần nhất, hòa id, mọc lại, bán kính, cạnh lên input | [test luật](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt theo PRD-0 mục F |
| G-FISH | Dưới nước, hồi chiêu, yield, xóa đúng đàn | [log bắt cá](../proof/phase-1/xuannghia2/fishing.log) | Đạt theo PRD-0 mục E/F |
| G-HOLD | Sức chứa, thứ tự nhặt, không nhận lô thiếu chỗ | [test luật](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt theo PRD-0 mục E/F |
| G-INV | Hái → cập bến → file kho → quan, ngất → kho rỗng, tick limit giữ kho cũ | [test headless](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt |
| G-DET | Cùng seed/input, so byte JSONL và file kho sau bắt cá | [test headless](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt |
| G-EVENT | Kiểm payload amount/yield, hold_full, oxygen_empty, faint/lost LIFO qua CLI | [test headless](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt theo PRD-0 mục E |
| G-REG | Smoke/starter/live và test gather | [53/53](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt |
| REPO | Chạy toàn bộ unittest discover | [56/57](../proof/phase-1/xuannghia2/all-tests.txt) | Chưa đạt toàn repo: lỗi test TEAM có sẵn |

Không xác nhận phần quan/UI/QA của thành viên khác đã hoàn thành. Chi tiết và lệnh demo:
[phần Xuân Nghĩa](../gather-xuannghia2.md). Phase 2–4 chờ đề.

## QA bổ sung — justcoffeee (21/11/2026, làm muộn sau mốc Phase 1)

Chạy lại trên commit cuối Phase 1 `f9477e3` (contract v1.0: 1 bếp B1, 1 bàn T1, 3 món) — commit cuối trước khi nhóm đọc Ticket-02 lúc 10:19 (xem `docs/clarify.md`). Repo chưa có tag `phase-1` nên mốc này là suy ra từ lịch sử commit. Kiểm theo thứ tự xử lý trong docstring `chonoi/sim/quan.py` (PRD-0 mục F).

| Nhãn QA | Cách kiểm | Bằng chứng | Kết quả |
|---|---|---|---|
| QA1-REG — toàn repo | Toàn bộ unittest tại `f9477e3`, có `python3` trên PATH | [all-tests](../proof/phase-1/justcoffeee/all-tests-f9477e3.txt) | 61/62; lỗi duy nhất `test_template_is_rejected`, đã sửa ở [2d809cc](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/2d809cc) |
| QA1-CYCLE — quán | Khách đến → nấu → ready → bốc → phục vụ → trả; tiền 72 = 60 + floor(60·0.2) | [probe](../proof/phase-1/justcoffeee/quan-probe-f9477e3.txt) | Đạt |
| QA1-LEFT | Hết kiên nhẫn: `customer_left` reason patience, uy tín 3.0 → 2.5 | [probe](../proof/phase-1/justcoffeee/quan-probe-f9477e3.txt) | Đạt |
| QA1-NODISH | Kho rỗng: `no_dish` payload `{}` | [probe](../proof/phase-1/justcoffeee/quan-probe-f9477e3.txt) | Đạt |
| QA1-CLOSE | Hết ca: khách chờ rời reason closing không trừ uy tín, rồi `quan_end` | [probe](../proof/phase-1/justcoffeee/quan-probe-f9477e3.txt) | Đạt |
| QA1-DET | Headless quán seed 3, 2000 tick, chạy 2 lần: cùng sha256 | [probe](../proof/phase-1/justcoffeee/quan-probe-f9477e3.txt) | Đạt |
| QA1-UI | `test_live` (snapshot menu quán, input và dừng server) | [all-tests](../proof/phase-1/justcoffeee/all-tests-f9477e3.txt) | Đạt test tự động; chưa chơi thử thủ công |
| **QA1-FIXTURE (QA-P2-01)** | Khách nạp từ scenario không được bếp nhận đơn | [probe](../proof/phase-1/justcoffeee/quan-probe-f9477e3.txt) | Chưa đạt tại f9477e3 (lỗi có từ Phase 1); đã sửa trên main ở 139b2b8, xem [phase-2](phase-2.md) |
