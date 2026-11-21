# Hunglunnn — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm: phụ trách module `client/ui`; thêm điều khiển bàn phím/cảm ứng, HUD gather/quán, bảng thực đơn, trạng thái kết nối, pause P, hiển thị Cá Sấu và tương thích giỏ v1.1/v1.2. Commit UI và tài liệu được ghi trong lịch sử nhánh `main`.
- Tôi đã review: đối chiếu `chonoi/live.py`, snapshot quan/gather, `game.contract.json`, test live và tài liệu P2/P3; không lấy dữ liệu UI từ số hay trường chưa có trong snapshot.
- AI sai ở đâu và tôi phát hiện thế nào: AI từng hiểu nhầm rằng freshness/pause đã nối nhưng còn thiếu xác nhận test; tôi phát hiện bằng việc kiểm `snap.state`, `snap.hold`, nút P, hàm `itemKind/itemFresh` và chạy test live/P2/P3/freshness.
- Điều tôi học được: UI không được tự suy đoán luật; cần nối qua snapshot/API, giữ tương thích v1.1/v1.2, thêm test cho trạng thái thực và ghi rõ phần chưa tích hợp thay vì tuyên bố DoD toàn nhóm.
