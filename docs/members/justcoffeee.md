# justcoffeee — Phạm Hoàng Huy — phản tư cá nhân (≤ 200 từ)

Module `qa` (QA lead đề xuất). Bản nháp do Claude Code soạn theo phiên làm việc; cần tự đọc và bổ sung trước khi nộp.

- Tôi đã làm:
  - [2d809cc](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/2d809cc): test TEAM dùng fixture bảng mẫu; hết lỗi nền.
  - [beee0a3](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/beee0a3): 12 test QA kho v1.2 (ngưỡng 30, roundtrip, schema, id).
  - [df8f204](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/df8f204): 12 test QA quán P2 (2 bếp, 4 bàn, 6 món), làm muộn; cả suite 134 test OK.
  - QA bổ sung P1 tại `f9477e3`: 61/62, probe quán. [P1](../verification/phase-1.md) · [P2](../verification/phase-2.md) · [P3](../verification/phase-3.md).
- Tôi đã review: adapter/FreshnessLedger P3 (đạt); `sim/quan` P1–P2: phát hiện **QA-P2-01** (khách nạp từ scenario không được bếp nhận đơn, có từ P1); quán chưa có P3 nên chưa bật v1.2.
- AI sai ở đâu và tôi phát hiện thế nào: (1) cả suite báo 39 lỗi; traceback cho thấy thiếu `python3`, không phải lỗi luật. (2) AI viết sai test bàn đầy, quên khách T1 rời đúng tick lượt 5; tính lại kiên nhẫn 3600 tick rồi sửa test, không sửa luật.
- Điều tôi học được: (cần tự bổ sung)
