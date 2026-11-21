# Retro nhóm

## Phase 2 (nhanh)

> QA (justcoffeee) tổng hợp muộn từ lịch sử git tới tag `phase-2` (`2fd97cc`) và các file kiểm chứng; **chưa được cả nhóm thông qua**, mọi người sửa/bổ sung trực tiếp.

- Điều tốt: chia lát nhỏ, mỗi lát push kèm test (gather: cá bơi [ed00b32](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/ed00b32), Cá Sấu [621ce0b](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/621ce0b), dữ liệu v1.1 [2e54f27](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/2e54f27); quán 2 bếp/4 bàn/6 món [d180783](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/d180783)); số chuẩn Ticket-02 gom về `game.contract.json`; cả 3 module có commit trong phase.
- Điều tệ: QA không có commit nào trong Phase 2, không ai kiểm chéo quán; lỗi fixture QA-P2-01 (có từ P1) chỉ lộ ra sau đó. Suite cả phase vẫn lỗi test TEAM nền. day/Shop/benchmark chưa có người nhận; commit quán dồn sát mốc (10:59–11:00).
- 1 hành động cho Phase 3: trước khi gắn tag, QA chạy cả suite và kiểm chéo mỗi module bằng test fixture (scenario dựng sẵn), ghi kết quả vào `docs/verification/`.

## Phase 4 (cuối)

> QA (justcoffeee) soạn nháp từ lịch sử git và file kiểm chứng, trước khi Phase 4 kết thúc; **chưa được cả nhóm thông qua**, mọi người sửa/bổ sung trực tiếp.

- Rà lại hành động Phase 2 ("QA chạy cả suite và kiểm chéo mỗi module bằng test fixture trước tag"): **đã làm, nhưng muộn**. QA vào cuộc từ Phase 3, tìm 7 lỗi quán (QA-P2-01..04, QA-P3-01..03); griin-03 sửa hết ở 139b2b8 và 537c88d. Tag `phase-3` (bc764b9) gắn khi QA-P3-01..03 còn mở; bản sửa vào sau tag.
- Điều tốt: migration kho tách hai bước theo ADR-0001, không làm hỏng main; vòng QA → sửa → test hồi quy nhanh (lỗi tới bản sửa khoảng 10–15 phút); benchmark đạt ngưỡng trên hai máy; suite từ 61/62 tại cuối P1 (f9477e3) lên 154/154.
- Điều tệ: vòng ngày/Shop/soak 10 ngày không có người nhận suốt từ Ticket-02, nên manifest vẫn 1.1 và chưa đủ điều kiện `v1.0.0`; QA vắng Phase 1–2 nên lỗi fixture có từ P1 lộ muộn; chưa ai chơi thử thật để kiểm cảnh báo.
- Số liệu: commit theo tác giả trên main đến lúc ghi: xuannghia2 21, justcoffeee 12, Hunglunnn 6, griin-03 5 (9 commit starter của giảng viên không tính). Đọc code của nhau: xuannghia2 review toàn repo ([review](review/github-2026-11-21.md)); QA viết test độc lập cho quán và gather. Token theo người: không ai đo (nhật ký AI ghi "Không đo").
- Một lần AI sai và cách nhóm phát hiện: luật quán viết cùng AI qua smoke test xanh nhưng khách nạp từ scenario không bao giờ được nấu (QA-P2-01, có từ P1); review của xuannghia2 và test QA độc lập cùng tái hiện qua headless, đánh dấu expectedFailure rồi chủ quán sửa.
- Nếu làm lại, đổi gì: chốt người nhận vòng ngày/Shop ngay khi Ticket-02 mở; QA kiểm chéo từ Phase 1 bằng fixture; chỉ gắn tag khi không còn expectedFailure hoặc ghi rõ trong mô tả tag.

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

### Phase 3 — xuannghia2

Đổi schema ảnh hưởng cả hai đầu, nên tách adapter/gather và ghi rõ chưa bật mặc định trước khi quán hỗ trợ.
Test nhiều tick và roundtrip phát hiện lý do không nên làm tròn fresh trong JSONL/file: số nhìn gần 30 có thể đổi nhánh.
Bằng chứng profile phải ghi rõ cấu hình thay thế, không gọi nhầm là smoke quán/ngày thật. Bước tiếp theo là chủ quán nối ledger, giữ id và giá, rồi chạy migration trên main.

### Phase 4 — ghi nhận từ phiên AI xuannghia2

QA sửa fixture TEAM và thêm 12 ca migration giúp suite đạt 122/122 trên clone sạch. Tuy vậy review thực thi còn tìm ra sinh khách bất chấp cờ tắt, fixture không nấu và nấu từ kho rỗng. Điều cần đổi là kiểm bất biến và giao diện giữa module trước khi chốt schema. Benchmark đo thật có metadata phát hiện cửa sổ native không khớp canvas; không sửa số để đạt. Chưa có số token đo được hay ý kiến retro tập thể. Cần nhóm chốt chủ day/Shop và hoàn tất migration trước release.

### Bổ sung P4 — Xuân Nghĩa

Đã sửa nguyên nhân DPI khiến native window khác canvas và thêm ba ca hồi quy để không nhận phép đo sai. Giữ dữ liệu benchmark cũ làm lịch sử, lần mới lưu riêng. UI mới của Hùng được ghép trước lần kiểm cuối; suite có 136 đạt + một expected failure. Hành động cần tiếp tục: kiểm luồng toàn ngày và thống nhất đầu nhận schema trước bật manifest. Đây là ghi nhận phiên AI, không thay ý kiến retro tập thể.
