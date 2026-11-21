# Clarify — câu hỏi và câu trả lời (PO ghi, cả nhóm dùng chung)

| # | Ngày giờ | Câu hỏi | Trả lời / giả định | Ai quyết |
|---|---|---|---|---|
| XN-01 | 21/11/2026 | Giỏ thiếu chỗ cho toàn bộ yield thì nhận một phần hay từ chối? | Đã đối chiếu: từ chối toàn lượt; không đổi cá/nút/giỏ. | PRD-0 mục F, Gather 3–4 |
| XN-02 | 21/11/2026 | Bắt hụt/đầy giỏ có tốn hồi chiêu không? | Đã đối chiếu: chỉ hồi chiêu khi bắt thành công, không thử đàn khác khi thiếu chỗ. | PRD-0 mục F, Gather 4 |
| XN-03 | 21/11/2026 | Payload chính xác của các sự kiện gather? | Đã sửa amount/yield, hold_full(action, required, free), oxygen_ticks:0 và faint(cause, lost LIFO, hp:0); xem docs/gather-xuannghia2.md. | PRD-0 mục E |
| XN-04 | 21/11/2026 | Phần gather của Phase 2–4 đã có yêu cầu chưa? | Người dùng xác nhận chưa được phát hành, sẽ bổ sung sau. Chỉ chốt Phase 1. | Xuân Nghĩa |

Nguồn đối chiếu XN-01 đến XN-03: [PRD-0](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-1), đọc sau khi Xuân Nghĩa đăng nhập ngày 21/11/2026. Phase 2–4 cũng được kiểm tra, vẫn chưa phát hành tại thời điểm đọc.

## Phase 2 — xuannghia2

- Ticket-02 được đọc khi tab mở lúc 10:19 ngày 21/11/2026; từ đây áp số chuẩn thay lựa chọn P1.
- Không đổi shape file kho; chỉ mở rộng danh sách kind nhận ca_keo và keo_neo theo đề. Dữ liệu v1.1 và thay đổi shared được công khai trong commit tích hợp để các module khác dùng.
- Hook gather nhận `day` và `active_upgrades`; phần điều phối phải truyền cấp có hiệu lực từ ngày kế, không cấp vừa mua cùng ngày.
- Đã hỏi người dùng về người phụ trách day/Shop/pause; chưa có phản hồi tại lúc ghi. Tiếp tục hoàn thiện gather độc lập; day/Shop/HUD còn chờ tích hợp, không gắn tag thay nhóm.
