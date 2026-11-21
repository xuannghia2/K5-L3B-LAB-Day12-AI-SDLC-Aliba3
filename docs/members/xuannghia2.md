# xuannghia2 — Cấn Xuân Nghĩa

Bản Codex soạn; cần tự đọc, bổ sung phản tư trước khi nộp. Chưa xác nhận review/demo thủ công.

- Phụ trách gather, Phase 1–4: oxy/ngạt/ngất, hái/bắt, cá bơi/sinh, Cá Sấu, kho cá thể, hao tươi, benchmark/cảnh báo.
- Bằng chứng: [P1](../verification/phase-1.md), [P2](../verification/phase-2.md), [P3](../verification/phase-3.md), [P4](../gather-phase-4-xuannghia2.md).
- AI ban đầu dùng payload qty và thiếu lost LIFO. Đọc PRD rồi sửa, kiểm CLI; xem commit 1d9083e.
- P3 đã có adapter/ledger, giữ precision và id. Manifest vẫn 1.1 vì quán chưa nhận cá thể; không gọi profile riêng là tích hợp toàn ngày.
- P4: clean clone 802f7c1 đạt 122/122 test. Benchmark avg 143.22/low 80.27 FPS, load 1.05s; native window chưa đúng kích thước dù canvas đúng.
- Review còn tìm thấy lỗi quán ngoài suite. Bài học từ phiên AI: kiểm bất biến và giao diện module trước khi dựa vào số test xanh.
- Chưa hoàn thành day/Shop/soak/release toàn nhóm; cần phối hợp chủ quán/UI/QA. Không có số token đo được.
