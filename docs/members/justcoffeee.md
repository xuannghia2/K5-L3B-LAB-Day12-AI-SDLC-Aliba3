# justcoffeee — Phạm Hoàng Huy — phản tư cá nhân (≤ 200 từ)

Module `qa` (QA lead đề xuất). Bản nháp do Claude Code soạn theo phiên làm việc; cần tự đọc và bổ sung trước khi nộp.

- Tôi đã làm:
  - [2d809cc](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/2d809cc): `test_template_is_rejected` dùng fixture bảng mẫu riêng thay vì TEAM.md thật; thêm test TEAM.md thật khớp `team_size`. Hết lỗi nền 103/104.
  - [beee0a3](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/beee0a3): 12 test QA độc lập cho kho v1.2 (ngưỡng 30, roundtrip, schema, id); chạy lại `verify_gather_p3.py`, sha256 khớp. [Kiểm chứng P3](../verification/phase-3.md).
- Tôi đã review: adapter/FreshnessLedger P3 của xuannghia2 (đạt); phát hiện `sim/quan.py` chưa xử lý `fresh`, manifest vẫn 1.1 → tích hợp v1.2 chưa đạt.
- AI sai ở đâu và tôi phát hiện thế nào: lần chạy cả suite báo 39 lỗi; xem traceback thì do `headless_cmd` gọi `python3` không có trên Windows, không phải lỗi luật. Không ghi đạt toàn repo.
- Điều tôi học được: (cần tự bổ sung)
