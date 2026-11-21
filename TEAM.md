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
- Git: mỗi người dùng nhánh ngắn theo module và tài khoản riêng; mỗi người có ít nhất 3 commit có nội dung; làm cặp ghi `Co-authored-by:`.
- Tích hợp: chạy toàn bộ test trước khi đẩy/gộp; ghi rõ lỗi có sẵn và lỗi mới, không đánh dấu đạt khi còn lỗi.
- Hợp đồng: không tự đổi `game.contract.json`, schema kho hoặc `docs/contracts/`; thông báo cả nhóm và ghi lại quyết định trước khi đổi.
- Tag/release: trưởng nhóm gắn `phase-1` đến `phase-4` theo mốc lab board sau khi đọc bằng chứng; chỉ tạo `v1.0.0` khi đủ điều kiện Phase 4.
- Ghi chép: mỗi người cập nhật nhật ký AI, kiểm chứng và `docs/members/<handle>.md`; Phase 2–4 chờ đề được bổ sung.
