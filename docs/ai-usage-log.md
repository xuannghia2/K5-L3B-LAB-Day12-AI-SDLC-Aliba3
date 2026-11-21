# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|

| 1 | Cấn Xuân Nghĩa / xuannghia2 | Codex (phiên 21/11/2026) | Đọc TEAM/AGENTS, hoàn thiện oxy/ngạt/ngất và 5 test luật | Không có số đo token/chi phí | Thiếu Python mặc định; dùng môi trường riêng D:\Vin\.tools; commit 943e86b. Mô tả commit ghi nhầm 6, số chạy thật là 5. |
| 1 | Cấn Xuân Nghĩa / xuannghia2 | Codex (cùng phiên) | Hái/bắt cá, giỏ, thêm 13 test luật | Không có số đo token/chi phí | Tổng 18 test luật đạt; giỏ thiếu chỗ và cooldown là giả định chờ PRD; commit 41d4186. |
| 1 | Cấn Xuân Nghĩa / xuannghia2 | Codex (cùng phiên) | Thêm 4 test headless, 2 lệnh test/play, lưu log, bàn giao và bản nháp phản tư | Không có số đo token/chi phí | 50 test phạm vi liên quan đạt; toàn repo 53/54 do test mẫu TEAM có sẵn. Người dùng xác nhận Phase 2–4 chưa có đề. Chưa có người review thủ công/push. |
| Phase 1 | Nguyễn Mạnh Hùng (Hunglunnn) | GitHub Copilot / MAI Code 2 Flash | Khảo sát trách nhiệm client/UI, bổ sung khung responsive và điều khiển cảm ứng cho `chonoi/web/index.html`; chưa thiết kế asset hay dữ liệu mới | Không ước tính | Giữ snapshot và API hiện có; không tự bịa dữ liệu sim mới |
| Phase 1 | Nguyễn Mạnh Hùng (Hunglunnn) | GitHub Copilot / MAI Code 2 Flash | Củng cố trạng thái kết nối, điều khiển cảm ứng, nút semantic và test HTML/API hiện có | Không ước tính | Chưa thiết kế màn hình quán/menu hoặc dữ liệu khách mới vì `sim/quan.py` chưa có vòng đời khách/bếp hoàn chỉnh |
