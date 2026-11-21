# justcoffeee — Phạm Hoàng Huy — phản tư cá nhân (≤ 200 từ)

Module `qa` (QA lead đề xuất).

- Tôi đã làm:
  - [2d809cc](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/2d809cc): test TEAM dùng fixture bảng mẫu.
  - [beee0a3](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/beee0a3): 12 test kho v1.2 (ngưỡng 30, roundtrip, schema, id).
  - [df8f204](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/df8f204), [5ca8212](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/5ca8212), [6494f1d](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/6494f1d): 15 test quán P2 (làm muộn) và QA bổ sung P1 tại `f9477e3`.
  - [296bc10](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/296bc10): 10 test quán P3 kho cá thể; suite 152 test OK. [P1](../verification/phase-1.md) · [P2](../verification/phase-2.md) · [P3](../verification/phase-3.md).
- Tôi đã review: gather/adapter P3 (đạt); `sim/quan`: QA-P2-01..04 (lỗi fixture, có từ P1) đã được griin-03 sửa ở 139b2b8, tôi chuyển thành test hồi quy; QA-P3-01..03 sửa ở 537c88d.
- AI sai ở đâu và tôi phát hiện thế nào: (1) 39 lỗi do thiếu `python3`. (2) AI viết sai test bàn đầy (khách T1 rời đúng tick lượt 5); tính lại kiên nhẫn rồi sửa test, không sửa luật.
- Điều tôi học được: Test xanh chưa chắc luật đúng: expectedFailure giữ suite xanh nhưng lỗi vẫn còn; phải đọc kỹ kết quả. Trước khi kết luận lỗi, đọc kĩ log: 39 test fail chỉ vì thiếu python3, không phải luật sai.
