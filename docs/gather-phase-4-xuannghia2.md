# Gather Phase 4 — xuannghia2

Đã push code tại 802f7c1. Phạm vi: benchmark render gather, cảnh báo chữ/tương phản cao, adapter version 1.3 dùng cùng schema cá thể v1.2. Không xác nhận hoàn thành quán/ngày/Shop hoặc release toàn nhóm.

## Tái tạo

Cần Python 3.12+, Chrome/Chromium/Edge cài sẵn. Không có thư viện Python bên thứ ba. `python3` phải nằm trên PATH để headless_cmd chạy được; trên Windows dùng môi trường có launcher python3, hoặc tools/gather.ps1 với CHONOI_PYTHON.

```sh
python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json
```

Có thể chỉ định `--browser <path>`. Không dùng --headless khi lấy bằng chứng render cửa sổ. Warmup cố định 3s; JSON có avg_fps, p1_low_fps, frames, measured_s, load_ms. 1% low dùng nghịch đảo trung bình thời gian của ceil(1% frame) chậm nhất. Metadata ghi cấu hình/dimensions thực. Browser dùng profile tạm riêng.

Kết quả clean clone: avg 143.22, low 80.27, load 1050.65ms, 4297 frame trong 30.0029s. Canvas 1280×720 nhưng native window 1920×1080; phần kích thước cửa sổ chưa đạt nguyên văn yêu cầu. Freshness chỉ inject riêng trong benchmark, không thay shared manifest 1.1.

Trong GUI có nút Tương phản cao; cảnh báo chữ cho oxy thấp, quái gần, khách sắp hết kiên nhẫn. Công cụ `python3 tools/preview_warnings_p4.py` cung cấp fixture pause có thời hạn để kiểm, không phải gameplay tự nhiên. [Bằng chứng](proof/phase-4/xuannghia2/warning-observations.json).

122/122 test đạt trên clone sạch Windows; macOS/Linux chưa thực chạy. [Review toàn repo](review/github-2026-11-21.md) ghi các blocker trước release: quán P3, day/Shop/soak, UI freshness/pause, LICENSE/phản tư và tags. Không tạo v1.0.0/phase-4 khi chưa đủ bằng chứng.

## Bổ sung hoàn thiện phần Xuân Nghĩa

Đã sửa DPI Windows: restore, đặt đúng kích thước và hiển thị cửa sổ của riêng PID browser benchmark. Renderer đợi kích thước ổn định rồi warmup 3s; sai kích thước hoặc tab ẩn bị từ chối. Không tác động profile Chrome người dùng.

Lần đo sau ghép UI 3e326c1: avg 143.38 FPS, 1% low 81.35 FPS, load 473.81ms, 4302 frame trong 30.0037s. Native window và canvas đều 1280×720. [Kết quả](proof/phase-4/xuannghia2/bench-sized.json), [metadata](proof/phase-4/xuannghia2/bench-sized-metadata.json). Hai lần thử sau merge đã bị hủy do tab ẩn/timeout, không dùng làm kết quả; lần hợp lệ mới được lưu. Profile freshness riêng vẫn được ghi rõ.

[Ma trận P4](verification/phase-4.md), [kế hoạch](plan/phase-4.md), [phản tư dưới 200 từ](members/xuannghia2.md), [credits](../CREDITS.md). Sau bổ sung có 137 test: 136 đạt, 1 expected failure fixture quán. UI P/freshness đã có commit mới của Hùng; Esc và tích hợp stock/reserved cá thể còn chờ. Không tự nhận day/Shop/soak/release đã hoàn tất.

### Đồng bộ cuối — quán và QA mới

Đã ghép 139b2b8 cùng QA 5ca8212/6494f1d. Quán đã thêm hỗ trợ kho cá thể và sửa các lỗi fixture được review; suite sau ghép đạt **142/142, không expected failure** ([log](proof/phase-4/xuannghia2/post-quan-merge-tests.txt)). Các nhận xét chưa có quán P3/lỗi fixture/expected failure phía trên là lịch sử lần kiểm trước. Manifest vẫn 1.1, chưa có xác nhận tích hợp mặc định v1.3/day/Shop/soak hay release toàn nhóm.
