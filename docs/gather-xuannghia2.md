# Phần Xuân Nghĩa — sim/gather, Phase 1

Chủ sở hữu: **Cấn Xuân Nghĩa / xuannghia2**, theo TEAM.md.
Ngày thực hiện: **21/11/2026 (Asia/Saigon)**.

## Phạm vi hoàn thành

- Bơi/chặn biên và tăng tốc dùng khung có sẵn.
- Phát `dive` / `surface` khi đổi vùng; oxy dựa vào vị trí cuối tick.
- Mặt nước hồi oxy và xóa bộ đếm ngạt; dưới nước giảm oxy, phát `oxygen_empty` đúng cạnh dương → 0.
- Ngạt theo `choke_interval_ticks`, trừ một HP; HP = 0 xóa giỏ, phát `faint` và kết thúc `fainted` trước tương tác.
- Hái một nút sẵn sàng gần nhất trên mặt nước; nút mọc lại theo tuning.
- Bắt một đàn cá gần nhất dưới nước, giới hạn bán kính và hồi chiêu.
- Hòa khoảng cách chọn id tự nhiên (N2 trước N10, F2 trước F10).
- Giỏ lưu theo thứ tự nhặt; phần tử cuối là mới nhất (LIFO); không vượt sức chứa.
- Cập bến trước hái; hết giờ xét sau tương tác; kho do runner ghi khi kết thúc.
- Headless và live dùng cùng GatherSim; không sửa quan, UI, tuning, schema kho hoặc contract khóa.

## Chạy trên máy hiện tại (PowerShell)

Tại thư mục repo `D:\Vin\K5-L3B-LAB-Day12-AI-SDLC-Aliba3`:

```powershell
.\tools\gather.ps1 test
.\tools\gather.ps1 play -Seed 1 -Port 8000
```

Lệnh `play` in URL để mở trình duyệt. WASD/mũi tên để bơi, E hái/cập bến, Space bắt cá, R chơi lại.
Môi trường riêng ở `D:\Vin\.tools\python`, không cần sửa PATH hệ thống.
Máy Windows khác có thể đặt `$env:CHONOI_PYTHON` thành đường dẫn Python 3;
để chạy smoke test phải có `python3` trong cùng thư mục executable hoặc trên PATH theo contract hiện hành.
Linux/macOS: `PYTHONPATH=tests:. python3 -m unittest test_gather_rules test_gather_headless test_smoke_p1 test_python_starter_units test_live -v`.

## Kết quả kiểm chứng thật

- 18 test luật và 7 test headless: **25/25 đạt** sau khi đối chiếu PRD-0.
- Bộ lệnh kiểm tra gather + smoke + starter + live: **53/53 đạt**.
- Toàn bộ repo: **56/57 đạt**, còn lỗi có sẵn `test_team_check.TeamCheck.test_template_is_rejected`.
  Test này đọc TEAM.md thật và đòi nó bị từ chối dù nhóm đã điền đủ 4 người.
  `python3 tools/check_team.py` trả mã 0, xác nhận danh sách hợp lệ.
  Không sửa test của phần QA để giữ phạm vi công việc; nhóm QA cần thay bằng fixture bảng mẫu riêng.
- Kiểm chứng kho: bắt F2 rồi F10 cho `ca_loc: 1, ca_linh: 3`; ngất xuất kho rỗng.
- Kiểm thử tích hợp xác nhận kho hái/cập bến được quan đọc và chạy lại cùng seed cho output giống từng byte.

Bằng chứng: [kết quả gather](proof/phase-1/xuannghia2/gather-tests.txt),
[toàn bộ test](proof/phase-1/xuannghia2/all-tests.txt),
[log bắt cá](proof/phase-1/xuannghia2/fishing.log),
[log ngất](proof/phase-1/xuannghia2/faint.log).

## Đối chiếu PRD-0 sau khi đăng nhập lab board

Ngày 21/11/2026 đã đọc trực tiếp [PRD-0 trên lab board](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1).
Mục F xác nhận nhận đủ yield hoặc từ chối nguyên lượt; bắt hụt/thiếu chỗ không khởi tạo hồi chiêu.
Hai lựa chọn ban đầu khớp đề. Mục E cho thấy payload ban đầu có lỗi; đã sửa như sau:

| Sự kiện | Payload đúng PRD-0 mục E |
|---|---|
| `gather` | `node_id`, `kind`, `amount` |
| `node_regrown` | `node_id` |
| `fish_caught` | `fish_id`, `kind`, `yield` |
| `hold_full` | `action` (`gather`/`catch`), `node_id`/`fish_id`, `required`, `free` |
| `dive`, `surface` | `pos` sau di chuyển |
| `oxygen_empty` | `oxygen_ticks: 0` |
| `choke` | `hp` sau trừ |
| `faint` | `cause: "choke"`, `lost` theo thứ tự LIFO, `hp: 0` |
| `gather_end` | `reason`, `inventory` theo schema kho |

Kiểm thử CLI kiểm tra chính xác các payload đã sửa, ngạt lần đầu ở tick 60 nếu oxy chạm 0 ở tick 1,
và không thử đàn khác khi đàn gần nhất vượt số ô trống. File kho vẫn giữ nguyên schema mục G.
Bằng chứng đã chạy lại trên bản tích hợp các commit UI của đồng đội đến `c69d61b`.

Phase 2–4 được kiểm tra trực tiếp sau đăng nhập và vẫn hiển thị chưa phát hành tại thời điểm đối chiếu.
Chỉ xác nhận phần gather đã kiểm chứng theo PRD-0; không xác nhận toàn bộ DoD Phase 1 của nhóm
hoặc kết quả test ẩn. Tag/release chung cần chờ kiểm chứng các module còn lại.

## Gợi ý demo cho Xuân Nghĩa

1. Chạy `play`, bơi sang nút hái, nhấn E, kiểm giỏ và trạng thái mọc lại.
2. Lặn tới cá, nhấn Space; giữ nút không bắt lặp, nhả/bấm lại sau hồi chiêu.
3. Lên mặt nước kiểm oxy hồi, quay về bến nhấn E.
4. Mở hai log bằng chứng để xem bắt cá/hết giờ và ngất/xuất kho rỗng.

Đây là kịch bản demo đề xuất; không phải tuyên bố người dùng đã tự demo hoặc review.

## Bản Phase 2

Các số và log trên là kết quả bàn giao Phase 1. Bản hiện tại đã chuyển dữ liệu v1.1; xem [gather Phase 2](gather-phase-2-xuannghia2.md) cho kiểm chứng mới và các phần chờ tích hợp.
