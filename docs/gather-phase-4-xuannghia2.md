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
