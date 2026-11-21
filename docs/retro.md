# Retro nhóm

## Phase 2 (nhanh)
- Điều tốt:
- Điều tệ:
- 1 hành động cho Phase 3:

## Phase 4 (cuối)
- Rà lại hành động Phase 2: đã làm chưa? vì sao?
- Điều tốt / điều tệ:
- Số liệu: số commit theo người, cách đọc code của nhau, token theo người:
- Một lần AI sai và cách nhóm phát hiện:
- Nếu làm lại, đổi gì:

## Ghi nhận riêng — xuannghia2, Phase 1 (21/11/2026)

- Có hiệu quả: chia luật gather thành oxy/ngạt và hái/bắt, kiểm thử mỗi lát trước khi lưu commit; kiểm chứng lại qua CLI/file kho.
- Vướng thực tế: lệnh Python mặc định chưa chạy được, cần môi trường riêng; test mẫu TEAM phụ thuộc bảng thật nên lỗi sau khi nhóm đã điền.
- Cần cải thiện: QA nên dùng fixture riêng cho bảng mẫu; PO cần đối chiếu cách xử lý yield thiếu chỗ, cooldown và payload sự kiện với PRD.
- Bước tiếp theo: Xuân Nghĩa đọc lại code, chạy demo; tiếp tục Phase 2–4 khi đề được bổ sung.
- Giới hạn: đây là ghi nhận từ phiên AI, không đại diện ý kiến retro của các thành viên khác.

### Cập nhật sau đối chiếu PRD-0 — xuannghia2

Đã mở lab board sau khi người dùng đăng nhập. Giả định yield/cooldown khớp mục F; payload ban đầu không khớp mục E nên đã sửa và bổ sung 3 test CLI (25 test gather tổng cộng). Bài học từ phiên AI: smoke test xanh chưa chứng minh đúng schema sự kiện; phải kiểm payload và thứ tự mất giỏ bằng tình huống cụ thể. Phase 2–4 vẫn khóa khi kiểm tra.

### Phase 2 — xuannghia2

Cá và Cá Sấu được tách khỏi GatherSim, push sau từng lát có test. Fixture khóa actor giúp giữ test P1 khi bản mặc định đổi sang cá chuyển động. Nguy cơ tích hợp là số chuẩn làm đổi test quán (thêm bàn tạo thêm lượt khách), nên ca kiểm một đơn dùng đúng kho một đơn. Bước tiếp theo của nhóm là nối day/Shop/UI vào hook gather và chạy benchmark, không nhầm dữ liệu cấu hình đã đủ với gameplay toàn ngày đã đủ.
