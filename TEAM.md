# TEAM

**Tên nhóm:** Aliba3 (theo tên repo)
**Số người:** 4 — khớp `team_size` trong `game.contract.json`.

Tên thành viên, GitHub handle và module chính giữ theo phân công đã có.
Các vai quy trình bổ sung và người dự phòng dưới đây là **đề xuất để trưởng nhóm thống nhất với các thành viên**.

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Cấn Xuân Nghĩa | xuannghia2 | `sim/gather` | Trưởng nhóm; đề xuất kiêm PO / Integrator | Lê Thanh Tùng — `sim/quan` (đề xuất) |
| Lê Thanh Tùng | griin-03 | `sim/quan` | Thành viên; đề xuất phụ trách Scrum / Release | Cấn Xuân Nghĩa — `sim/gather` (đề xuất) |
| Nguyễn Mạnh Hùng | Hunglunnn | `client/ui` | Thành viên; đề xuất phụ trách demo / trải nghiệm người chơi | Phạm Hoàng Huy — `qa` (đề xuất) |
| Phạm Hoàng Huy | justcoffeee | `qa` | Thành viên; đề xuất phụ trách QA lead | Nguyễn Mạnh Hùng — `client/ui` (đề xuất) |

**Vai quy trình:** PO làm đầu mối hỏi giảng viên và ghi `docs/clarify.md`; Integrator kiểm hợp đồng và tích hợp; QA lead tổng hợp kiểm thử/bằng chứng; Scrum / Release theo dõi tiến độ và chuẩn bị phát hành. Có thể kiêm nhiệm.

**Người dự phòng cho:** người ở mỗi dòng hỗ trợ thành viên được ghi trong cột cuối khi thành viên đó bị vướng; không tự nhận thay toàn bộ module.

## Thỏa thuận làm việc nhóm (≤ 10 dòng)

Kênh Zalo là thông tin đã có. Các quy tắc còn lại là **bản đề xuất, chưa ghi nhận cả nhóm đã thông qua**.

- Kênh liên lạc: Zalo; báo tiến độ, vướng mắc và thay đổi ảnh hưởng module khác tại đây.
- Bất đồng thiết kế: trao đổi tối đa 2 phút; nếu chưa thống nhất, trưởng nhóm chốt hướng tạm thời và ghi lý do; câu hỏi về đề chuyển giảng viên/PO.
- Vướng quá 10 phút: báo ngay trên Zalo, nêu lỗi và cách đã thử; trưởng nhóm điều phối người dự phòng hỗ trợ.
- Standup: 5 phút trước khi kết thúc mỗi phase; mỗi người báo phần xong, phần còn vướng và phụ thuộc; mốc phase theo lab board.
- Đọc code: cặp gather/quan và UI/QA review chéo; kiểm tra giao diện tích hợp, test và bằng chứng trước khi gộp.
- Git: dùng tài khoản riêng, mỗi người ít nhất 3 commit có nội dung; làm cặp ghi `Co-authored-by:`. Phần xuannghia2 theo yêu cầu trưởng nhóm: hoàn thành, kiểm tra rồi push từng phần lên main; cách làm của thành viên khác do nhóm thống nhất.
- Tích hợp: chạy toàn bộ test trước khi đẩy/gộp; ghi rõ lỗi có sẵn và lỗi mới, không đánh dấu đạt khi còn lỗi.
- Hợp đồng: không tự đổi `game.contract.json`, schema kho hoặc `docs/contracts/`; thông báo cả nhóm và ghi lại quyết định trước khi đổi.
- Tag/release: trưởng nhóm gắn `phase-1` đến `phase-4` theo mốc lab board sau khi đọc bằng chứng; chỉ tạo `v1.0.0` khi đủ điều kiện Phase 4.
- Ghi chép: mỗi người cập nhật nhật ký AI, kiểm chứng và `docs/members/<handle>.md`; Phase 1–3 đã có đề, cập nhật phạm vi theo ticket mới thay vì suy diễn yêu cầu.

## Phạm vi và bàn giao qua các phase

Cập nhật **21/11/2026 (Asia/Saigon)** theo phân công gốc và commit đã có trên GitHub.
Bảng này ghi phạm vi module và điểm cần phối hợp; không tự xác nhận thành viên đã làm xong công việc chưa có bằng chứng.

| Thành viên | Phase 1 | Phase 2 | Phase 3 / phụ thuộc tích hợp |
|---|---|---|---|
| Cấn Xuân Nghĩa — xuannghia2 | Bơi, oxy/ngạt/ngất, giỏ, hái/bắt, cập bến/xuất kho | Cá bơi/sinh, Cá Sấu, rơi hàng, bất tử/recoil, số chuẩn và hook nâng cấp | Adapter kho cá thể, hao tươi gather, spoiled, lost LIFO, id liên tục, precision và bằng chứng; chờ quán để bật v1.2 chung |
| Lê Thanh Tùng — griin-03 | Luật quán: khách/giữ chỗ, bếp/bưng/phục vụ, tiền/uy tín | Kiểm thử quán với 2 bếp, 4 bàn, 6 món | Điểm nối thuộc sim/quan: nhận cá thể, giữ theo id tươi nhất, hao kho/giữ lại, giá theo tươi; chưa thấy commit P3 tại lần kiểm này |
| Nguyễn Mạnh Hùng — Hunglunnn | Giao diện trình duyệt theo client/ui | Các cập nhật UI responsive, điều khiển và menu/HUD đã push | Điểm nối thuộc client/ui: hiển thị item.fresh/hàng ươn và đọc hold/stock cá thể; chưa xác nhận đã tích hợp schema P3 |
| Phạm Hoàng Huy — justcoffeee | QA theo phân công gốc | Kiểm hồi quy và bằng chứng theo phạm vi QA | Kiểm migration schema/ngưỡng 30 và lỗi test mẫu TEAM; QA độc lập 12 test P3 đã push, cùng sửa lỗi test TEAM |

## Tiến độ có bằng chứng

| Phần | Bằng chứng | Trạng thái ghi nhận |
|---|---|---|
| Gather Phase 1 | [Bàn giao](docs/gather-xuannghia2.md), [kiểm chứng](docs/verification/phase-1.md) | Đã push; số liệu P1 giữ theo log lịch sử |
| Gather Phase 2 | [Bàn giao](docs/gather-phase-2-xuannghia2.md), [kiểm chứng](docs/verification/phase-2.md) | Đã push; cá/Cá Sấu/kho mới và pause backend đã kiểm |
| Adapter + gather Phase 3 | [ADR-0001](docs/adr/0001-fresh-inventory-migration.md), [bàn giao API](docs/gather-phase-3-xuannghia2.md), [kiểm chứng](docs/verification/phase-3.md) | Đã push; 17 test P3 và 100 test có phạm vi đạt với profile kiểm thử rõ ràng |
| Quán Phase 2 | Commit [d180783](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/d180783), [ghi chép griin-03](docs/members/griin-03.md) | Có commit kiểm thử và ghi chép; không suy ra quán đã chuyển v1.2 |
| UI đã push | Commit [9ea49c2](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/9ea49c2) | Có cập nhật UI; cần kiểm thực tế phần đọc freshness P3 |
| Vòng ngày / Shop / tích hợp chung | [Kế hoạch P2](docs/plan/phase-2.md), [kế hoạch P3](docs/plan/phase-3.md) | Chưa có xác nhận người phụ trách và kết quả tích hợp đầy đủ |

Lần kiểm GitHub mới nhất: main ở `df8f204`, chưa thấy commit quán P3. Clone sạch 802f7c1 đạt 122/122; sau ghép QA df8f204, 134 test gồm 133 đạt và 1 expected failure cho lỗi fixture quán. QA đã sửa lỗi TEAM cũ. Xem [review toàn repo](docs/review/github-2026-11-21.md).
Đây là ảnh chụp tiến độ tại lúc ghi, không phải trạng thái tự cập nhật theo GitHub.

## Các điểm nhóm cần chốt tiếp

- Xác nhận người phụ trách bộ điều phối `day`, Shop và chuyển pha; không mặc định giao thêm module cho thành viên khi chưa thống nhất.
- Chủ sim/quan dùng adapter/ledger đã push để hoàn thiện đầu nhận v1.2; client/ui đọc trực tiếp fresh của từng cá thể.
- Giữ manifest chung v1.1 trong thời gian chuyển. Sau khi hai đầu sẵn sàng, kiểm file kho và day, cập nhật fixture rồi mới bật v1.2 và gắn tag.
- Dùng cùng IdAllocator xuyên pha/ngày; không tái sử dụng id đã dùng hoặc bỏ. File kho v1.2 là `items` dạng mảng, không nhận kho đếm.
- QA đã sửa test mẫu TEAM bằng fixture riêng (2d809cc); log fail các phase cũ giữ làm lịch sử. Cần bổ sung ca hồi quy lỗi fixture quán đã ghi trong review.
- Trước khi chốt phase, từng thành viên tự đọc lại phần của mình và bổ sung phản tư/review/demo thực tế; không coi nội dung AI soạn là bằng chứng người đã review.

## Phase 4 — trạng thái đã kiểm

- Xuân Nghĩa đã push benchmark render gather và cảnh báo/tương phản cao ở 802f7c1; [bàn giao](docs/gather-phase-4-xuannghia2.md).
- Chưa đủ DoD toàn nhóm: quán cá thể, day/Shop/soak, UI fresh/pause, quyền cấp phép, phản tư Hùng và phát hành. Không đánh dấu hoàn thành thay thành viên khác.

- QA mới: Huy đã push df8f204 với 12 test quán P2, trong đó 1 expectedFailure tái hiện lỗi fixture thiếu order_status; chưa phải lỗi đã sửa.
