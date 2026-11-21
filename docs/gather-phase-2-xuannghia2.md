# Xuân Nghĩa — gather Phase 2 / Ticket-02

Nguồn: [Ticket-02 trên lab board](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-2),
được quan sát phát hành lúc 10:19 ngày 21/11/2026 (Asia/Saigon).
Phạm vi: module `sim/gather` theo TEAM.md và các thay đổi shared cần cho đầu vào/đầu ra của module này.

## Đã triển khai và kiểm chứng

- Cá bơi, phản xạ quãng đường còn lại tại mép/corner, đổi hướng theo tuổi; RNG dùng Streams.
- Sinh 8 đàn ban đầu, tăng theo lịch dưới trần 12; kiểm điểm sinh/clearance và trọng số theo loài còn chỗ.
- Fixture `random_fish:false` giữ cá đứng yên, không sinh; cá mới chưa di chuyển trong bước sinh.
- Cá Sấu tuần tra/chase, một hit gần nhất mỗi bước, mất hàng LIFO, bất tử/recoil đúng nhịp; ngạt xét trước hit.
- Ngất do hit ghi phần rơi do hit rồi phần giỏ còn lại trong faint; kho bàn giao rỗng.
- Nút kèo nèo N5/N6 và yield cá kèo; file kho vẫn là object `items`, nhận đủ 6 kind.
- Pause backend tách tick ngoài và sim_tick, không chạy timer/actor khi pause; resume chạy ngay bước đó.
- Fixture kiểm id, độ sâu Cá Sấu, waypoint, recoil/timer/vector, tuổi cá và số hữu hạn; lỗi đầu vào thoát 2 trước ghi.
- Manifest nâng lên v1.1, thêm dữ liệu chuẩn gather, 2 bếp/4 bàn, 6 món, kế hoạch 5 ngày và nâng cấp.
  Dữ liệu chuẩn không đồng nghĩa toàn bộ vòng ngày đã triển khai.

## Giao diện để tích hợp vòng ngày

```python
sim = GatherSim(tuning, gather_scenario, streams, ids,
                day=day_number, active_upgrades=active_upgrades)
```

- `day` mặc định 1 ở lượt độc lập; M2 xuất hiện từ ngày 3. `monsters:[]` thay toàn bộ quái mặc định bằng rỗng.
- `active_upgrades` lấy cấp có hiệu lực ở đầu ngày, không lấy cấp vừa mua trong Shop cùng ngày.
  Gather đọc `tuning.shop.upgrades.oxygen/hp`, hồi đầy mặc định và không sửa tuning gốc.
- Sau `sim.done`, đọc `sim.inventory_items()` hoặc `gather_end.inventory.items` để dựng QuanSim.
- Tiền/earned/uy tín xuyên ngày và chuyển pha thuộc bộ điều phối ngày; GatherSim độc lập vẫn bắt đầu tiền bằng 0.
- Pause hiện nằm trong Session, input có `buy` chỉ có giá trị tại frame khai báo. Lượt gather/quan độc lập bỏ qua buy/shop_done.

**Chưa tích hợp trong phần việc này:** `--mode day`, luồng Shop/mua hàng, chuyển pha qua các ngày và HUD/menu mới.
Cần người phụ trách vòng ngày/UI nối các giao diện trên; không gắn tag Phase 2 hay xác nhận DoD toàn nhóm khi còn các phần này.
Không triển khai các mở rộng tùy chọn (weapon/net/snake/burn/vendor/ca_ho).

## Chạy và bằng chứng

```powershell
.\tools\gather.ps1 test
.\tools\gather.ps1 play
```

- Test gather P1/P2: **48/48 đạt** (25 test trước và 23 test P2).
- Lệnh test có phạm vi gather + smoke + starter + quan + live: **81/81 đạt**.
- Toàn repo: **84/85 đạt**. Lỗi còn lại là test mẫu TEAM.md có sẵn; không sửa test QA trong phạm vi này.
- [Test tổng](proof/phase-2/xuannghia2/all-tests.txt), [test có phạm vi](proof/phase-2/xuannghia2/gather-tests.txt).
- [Hai tiến trình và kho](proof/phase-2/xuannghia2/integration-gather.log), [kho](proof/phase-2/xuannghia2/integration-inventory.json), [quán tick 0](proof/phase-2/xuannghia2/integration-quan.log).
- [Cá Sấu/ngất](proof/phase-2/xuannghia2/monster-faint.log), [cá bơi/sinh](proof/phase-2/xuannghia2/swim.log).

Chưa chạy benchmark một Ngày vì bộ điều phối ngày chưa tích hợp; không tự ghi đạt mục hiệu năng đó.

## Vì sao sửa một số test P1

- Sáu cá đứng yên mặc định đã đổi thành tám đàn theo seed; assertion đọc số đàn đã khai trong manifest.
- Test luật P1 của gather khóa cá/quái bằng fixture để vẫn kiểm cùng tình huống cũ.
- Số bếp/bàn thành 2/4; test vòng phục vụ dùng kho đúng một đơn để không sinh thêm khách ở bàn mới.
- `attack` là input hợp lệ v1.1 dù mở rộng chưa bật (bỏ qua), nên không còn nằm trong danh sách tên nút sai.
- Không bỏ kiểm sức chứa, thời điểm ngạt, xuất kho hay thứ tự xử lý để làm test xanh.
