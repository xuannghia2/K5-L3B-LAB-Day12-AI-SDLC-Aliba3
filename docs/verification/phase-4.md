# Kiểm chứng Phase 4 — xuannghia2

| Yêu cầu | Kiểm và bằng chứng | Kết luận |
|---|---|---|
| Render gather, seed 42, đứng bến, cá/quái/freshness | [Metadata](../proof/phase-4/xuannghia2/bench-sized-metadata.json), browser headless=false, player [2,0] | Đạt cảnh benchmark; freshness là profile riêng, chưa phải manifest 1.3 mặc định |
| 1280×720 | Canvas và native window trong metadata; sửa DPI Windows, kiểm trước/suốt phép đo | Đạt tại lần đo mới; số đo cũ giữ làm lịch sử |
| Warmup 3s, đo >=30s, 5 trường JSON | [Kết quả](../proof/phase-4/xuannghia2/bench-sized.json); bench.py/bench.js; test_bench | Có bằng chứng thực, không tính FPS headless simulation |
| Ngưỡng avg≥60, low≥30, load≤10000ms | So kết quả JSON với ngưỡng; 1% low tính từ mean các frame chậm nhất | Đạt trên máy đo, không khái quát máy khác |
| Không nhận kết quả sai kích thước/ẩn | 3 ca BenchRenderConditions, [suite](../proof/phase-4/xuannghia2/supplement-tests.txt) | Đạt; lỗi kích thước trả nonzero, không tạo kết quả mới |
| Ba cảnh báo và tương phản cao | [Quan sát UI](../proof/phase-4/xuannghia2/warning-observations.json) | Đã kiểm fixture pause; chưa phải người dùng chơi một ngày |
| Hồi quy sau ghép UI 3e326c1 | 137 test: 136 đạt + 1 expected failure, source 61fffb9 + bổ sung đặt foreground cửa sổ benchmark riêng | Lỗi đã biết thuộc fixture quán, không báo toàn bộ đạt |
| GUI <=3 lệnh, môi trường/điều khiển | README + bàn giao P4 | Đã có hướng dẫn; macOS/Linux chưa thực chạy |
| Contract 1.3/soak 10 ngày/release/tag | Quán cá thể và day/Shop chưa có | Chưa đạt tích hợp nhóm; chưa tạo release/tag |

Tái tạo: `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`; `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` trên macOS/Linux, `.\tools\gather.ps1 test` trên Windows.
