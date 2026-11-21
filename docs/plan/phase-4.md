# Phase 4 — phạm vi Xuân Nghĩa

Nguồn: Ticket-04 trên lab board đã mở ngày 21/11/2026. Kế hoạch này theo phân công sim/gather; không tự giao lại module cho các thành viên.

| Việc | Cách thực hiện | Trạng thái |
|---|---|---|
| Benchmark render | Chrome profile tạm, seed 42, đứng bến, warmup 3s + đo 30s, JSON 5 trường | Đã đo thật; có kiểm kích thước native và canvas |
| Cảnh báo/tương phản | Cảnh báo bằng chữ oxy/quái/khách, nút tương phản cao | Đã có bằng chứng fixture UI |
| Tương thích schema | Adapter 1.3 giữ shape cá thể 1.2 | Đã kiểm; shared manifest chưa bật do quán |
| Handoff/kiểm chứng | Bảng luật–bằng chứng, lệnh tái tạo, ghi nhận giới hạn | docs/verification/phase-4.md |
| Phản tư/retro/nguồn | Cá nhân dưới 200 từ, nhật ký AI, credits đúng nguồn | Đã bổ sung; không tự nhận người đã demo/review |
| Tích hợp nhóm/release | Quán P3, day/Shop, soak 10 ngày, contract 1.3, gói phát hành/tag | Phụ thuộc nhóm, chưa ghi đạt |

Chỉ bật schema chung khi đầu nhận quán sẵn sàng và kiểm hai đầu. Không xuất kết quả soak giả hoặc dùng một gather benchmark để thay soak toàn ngày.

Cập nhật cuối: quán cá thể 139b2b8 đã có, QA hồi quy đã bỏ expectedFailure sau khi sửa luật; 142/142 test đạt. Việc còn lại là kiểm hai đầu qua luồng tích hợp, day/Shop/soak và bật manifest, không còn coi quán chưa có commit P3.
