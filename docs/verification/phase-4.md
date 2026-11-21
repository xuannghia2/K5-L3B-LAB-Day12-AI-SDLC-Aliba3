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

## Kết quả cuối sau đồng bộ quán

Đã ghép 139b2b8 (quán cá thể/validation) và QA 5ca8212/6494f1d: [suite mới](../proof/phase-4/xuannghia2/post-quan-merge-tests.txt) **142/142 đạt, không expected failure**. Nhận xét lỗi fixture ở các log trước là lịch sử. Hỗ trợ quán P3 đã được push; shared manifest vẫn 1.1, chưa xác nhận smoke mặc định v1.3 hoặc day/Shop/soak. Benchmark gather phía trên không bị đổi code/dữ liệu bởi các commit quán.

## QA Phase 4 — justcoffeee (21/11/2026, main `ba75b01`)

Ticket-04 suy ra từ ma trận trên, kế hoạch và bàn giao P4 của xuannghia2; QA chưa đọc trực tiếp văn bản ticket. Windows 11, Python 3.14 qua venv tạm có `python3`.

| Nhãn QA | Cách kiểm | Bằng chứng | Kết quả |
|---|---|---|---|
| QA4-REG | Toàn bộ unittest trên main | [all-tests](../proof/phase-4/justcoffeee/all-tests.txt) | 154/154 đạt |
| QA4-BENCH | Chạy lại độc lập `python3 -m chonoi.bench --seed 42 --duration 30`, Chrome không headless | [bench](../proof/phase-4/justcoffeee/bench.json), [metadata](../proof/phase-4/justcoffeee/bench-metadata.json) | Đạt ngưỡng: avg 143.6 FPS (≥60), 1% low 88.9 (≥30), load 1924 ms (≤10000); canvas và cửa sổ 1280×720, tab không ẩn. Chỉ trên máy này |
| QA4-CLONE | Clone sạch từ GitHub, làm đúng 3 lệnh README (thêm `--port`), GET / = 200; chạy suite trong clone | [clean-clone](../proof/phase-4/justcoffeee/clean-clone.txt) | Đạt trên Windows; server GUI lên, 154/154 trong clone. macOS/Linux chưa chạy |
| QA4-DET | Qua `headless_cmd`: gather và quan seed 42, 1800 tick, chạy 2 lần cùng sha256; seed 43 khác output | [integration-release](../proof/phase-4/justcoffeee/integration-release.txt) | Đạt |
| QA4-BAD | Kho JSON hỏng và `--mode shop` → exit 2 | [integration-release](../proof/phase-4/justcoffeee/integration-release.txt) | Đạt |
| QA4-V13 | Profile 1.3 trong tiến trình: gather cập bến ghi kho cá thể, quán nạp và có khách | [integration-release](../proof/phase-4/justcoffeee/integration-release.txt) | Đạt profile; **manifest chung vẫn 1.1** nên chưa bật mặc định |
| **QA4-DAY** | `--mode day` | [integration-release](../proof/phase-4/justcoffeee/integration-release.txt) | **Chưa đạt**: exit 2 "chờ module vòng ngày"; không có `soak_cmd`; không thể kiểm 10 ngày/Shop |
| QA4-UI-CONTRAST | justcoffeee tự mở GUI gather (`py -3 -m chonoi.live --mode gather --seed 42`) và bấm nút Tương phản cao | Quan sát thủ công của justcoffeee, không có ảnh chụp | Đạt: nút hoạt động đúng |
| QA4-UI-WARN | justcoffeee tự chơi GUI và quan sát ba cảnh báo chữ (oxy thấp, quái gần, khách sắp hết kiên nhẫn) | Quan sát thủ công của justcoffeee, không có ảnh chụp; bổ sung cho quan sát fixture pause của xuannghia2 | Đạt: cả ba cảnh báo hiển thị đúng |

### Cổng phát hành (QA)

| Điều kiện trước tag `phase-4` / Release `v1.0.0` | Trạng thái |
|---|---|
| Suite xanh trên main, clone sạch chạy được | Đạt |
| Headless tất định, input sai exit 2 | Đạt |
| Benchmark đạt ngưỡng | Đạt (máy QA và máy xuannghia2) |
| Contract 1.3 bật trên manifest chung | **Chưa** |
| Vòng ngày / Shop / soak 10 ngày | **Chưa có module**, chưa có người nhận |
| Tag `phase-4`, Release `v1.0.0` | Chưa có (repo có `phase-1`..`phase-3`) |
| `LICENSE` | Không có file trong repo |

Kết luận QA: phần đã có chạy đúng và tất định, nhưng **chưa đủ điều kiện gọi là v1.0.0 đầy đủ theo Ticket-04** khi thiếu vòng ngày/soak và manifest 1.3. Nếu hết giờ vẫn gắn tag thì ghi trung thực các dòng "Chưa" ở trên trong mô tả release.
