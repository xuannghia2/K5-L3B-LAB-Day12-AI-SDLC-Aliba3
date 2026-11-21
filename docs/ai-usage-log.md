# Nhật ký dùng AI (theo phase và theo người)

| Phase | Người | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|---|

| 1 | Cấn Xuân Nghĩa / xuannghia2 | Codex (phiên 21/11/2026) | Đọc TEAM/AGENTS, hoàn thiện oxy/ngạt/ngất và 5 test luật | Không có số đo token/chi phí | Thiếu Python mặc định; dùng môi trường riêng D:\Vin\.tools; commit 943e86b. Mô tả commit ghi nhầm 6, số chạy thật là 5. |
| 1 | Cấn Xuân Nghĩa / xuannghia2 | Codex (cùng phiên) | Hái/bắt cá, giỏ, thêm 13 test luật | Không có số đo token/chi phí | Tổng 18 test luật đạt; giỏ thiếu chỗ và cooldown là giả định chờ PRD; commit 41d4186. |
| 1 | Cấn Xuân Nghĩa / xuannghia2 | Codex (cùng phiên) | Thêm 4 test headless, 2 lệnh test/play, lưu log, bàn giao và bản nháp phản tư | Không có số đo token/chi phí | 50 test phạm vi liên quan đạt; toàn repo 53/54 do test mẫu TEAM có sẵn. Người dùng xác nhận Phase 2–4 chưa có đề. Chưa có người review thủ công/push. |
| Phase 1 | Nguyễn Mạnh Hùng (Hunglunnn) | GitHub Copilot / MAI Code 2 Flash | Khảo sát trách nhiệm client/UI, bổ sung khung responsive và điều khiển cảm ứng cho `chonoi/web/index.html`; chưa thiết kế asset hay dữ liệu mới | Không ước tính | Giữ snapshot và API hiện có; không tự bịa dữ liệu sim mới |
| Phase 1 | Nguyễn Mạnh Hùng (Hunglunnn) | GitHub Copilot / MAI Code 2 Flash | Củng cố trạng thái kết nối, điều khiển cảm ứng, nút semantic và test HTML/API hiện có | Không ước tính | Chưa thiết kế màn hình quán/menu hoặc dữ liệu khách mới vì `sim/quan.py` chưa có vòng đời khách/bếp hoàn chỉnh |

| 1 | Cấn Xuân Nghĩa / xuannghia2 | Codex (đối chiếu PRD sau đăng nhập, 21/11/2026) | Sửa payload gather/hold_full/fish_caught/oxygen_empty/faint theo PRD-0 mục E, ghi lost LIFO, thêm 3 test CLI và làm mới bằng chứng | Không có số đo token/chi phí | Giả định yield/cooldown khớp mục F. Payload qty ban đầu sai; đã sửa. 25/25 test gather, 53/53 test phạm vi liên quan đạt; toàn repo 56/57, còn lỗi mẫu TEAM có sẵn. Giữ các commit UI của đồng đội đến c69d61b. Phase 2–4 vẫn chưa phát hành. |
| 1 | Lê Thanh Tùng / griin-03 | Antigravity (Google DeepMind) | Triển khai hoàn thiện sim/quan (Lát 3 khách & vòng đời, Lát 4 bếp & phục vụ & kinh tế theo PRD-0 mục E, F), bổ sung test unit | Không có số đo token/chi phí | Chuẩn hóa toàn bộ thứ tự tick, payload event dish_ready, cook_started, served, paid, customer_left, quan_end theo đúng Test Contract v1.0 |
