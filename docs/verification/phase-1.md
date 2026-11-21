# Ma trận truy vết Phase 1

| AC | Cách kiểm chứng | Bằng chứng (link `docs/proof/phase-1/...`) | Kết quả (đạt / chưa đạt — ghi trung thực) |
|---|---|---|---|

## Đánh giá ngắn
- Yêu cầu nào đạt / chưa đạt:
- Điều cần chỉnh cho phase sau:

## Phần Cấn Xuân Nghĩa / xuannghia2 — sim/gather (21/11/2026)

Mã G bên dưới là nhãn kiểm thử nội bộ; chưa gán mã AC chính thức do chưa đọc được PRD trên lab board.

| Nhãn | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| G-OXY | Mặt nước, cạn oxy, chuyển vùng, ngạt/ngất, ưu tiên kết thúc | [test luật](../proof/phase-1/xuannghia2/gather-tests.txt), [ngất](../proof/phase-1/xuannghia2/faint.log) | Đạt theo TODO repo |
| G-NODE | Gần nhất, hòa id, mọc lại, bán kính, cạnh lên input | [test luật](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt theo TODO repo |
| G-FISH | Dưới nước, hồi chiêu, yield, xóa đúng đàn | [log bắt cá](../proof/phase-1/xuannghia2/fishing.log) | Đạt theo giả định đã ghi |
| G-HOLD | Sức chứa, thứ tự nhặt, không nhận lô thiếu chỗ | [test luật](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt theo giả định đã ghi |
| G-INV | Hái → cập bến → file kho → quan, ngất → kho rỗng, tick limit giữ kho cũ | [test headless](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt |
| G-DET | Cùng seed/input, so byte JSONL và file kho sau bắt cá | [test headless](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt |
| G-REG | Smoke/starter/live và test gather | [50/50](../proof/phase-1/xuannghia2/gather-tests.txt) | Đạt |
| REPO | Chạy toàn bộ unittest discover | [53/54](../proof/phase-1/xuannghia2/all-tests.txt) | Chưa đạt toàn repo: lỗi test TEAM có sẵn |

Không xác nhận phần quan/UI/QA của thành viên khác đã hoàn thành. Chi tiết và lệnh demo:
[phần Xuân Nghĩa](../gather-xuannghia2.md). Phase 2–4 chờ đề.
