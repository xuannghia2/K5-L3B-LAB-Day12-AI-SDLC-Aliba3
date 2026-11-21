# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật.

## Lệnh
- Test: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Headless: `python3 -m chonoi.headless --mode gather|quan --seed 1 --ticks 600 --out out.jsonl`
- Chơi thử trên trình duyệt: `python3 -m chonoi.live --mode gather|quan` (mở địa chỉ in ra; WASD, E, Space, R)

## Cấu trúc & quy ước
- (Starter Python là TÙY CHỌN; nhóm có thể dùng ngôn ngữ khác nếu giữ Test Contract.) Khung do giảng viên cấp: `chonoi/{headless,inputs,scenario,contract,rng,ids,jsonl,inventory,runner,live}.py` và `chonoi/web/`. Hạn chế sửa; nếu phải sửa thì báo cả nhóm và ghi lại lý do.
- Luật chơi của nhóm: `chonoi/sim/gather.py`, `chonoi/sim/quan.py` (tìm `TODO(nhóm)`).
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase và hợp đồng kho trước.
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit hoặc `docs/proof/`; người đọc lại thay đổi trước khi đẩy.
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm
- (Ghi tên và khi nào dùng; tối thiểu 2 skill/hook/command nhóm tự viết, đặt ở `.agents/skills/` hoặc tương đương.)

### Hai command cho phần gather (xuannghia2, Phase 1)
- `.\tools\gather.ps1 test`: chạy toàn bộ unittest discover; dùng trước khi bàn giao/push.
- `.\tools\gather.ps1 play -Seed 1 -Port 8000`: mở server chơi thử gather; dùng để người review kiểm bơi, oxy, hái/bắt và cập bến.
- Windows: script ưu tiên môi trường riêng `.tools/python` cạnh repo hoặc `CHONOI_PYTHON`, chỉ đổi biến môi trường trong thời gian chạy. Smoke test vẫn dùng `python3` theo contract.
- Lỗi TEAM lịch sử trong log P1 đã được QA sửa bằng fixture riêng tại 2d809cc; suite hiện tại 122/122 đạt trên clone sạch Windows.

### Phase 2 — gather và phụ thuộc shared (xuannghia2)
- `game.contract.json` đã chuyển dữ liệu v1.1; cá mặc định là số 8 thay danh sách sáu đàn. Dữ liệu gather chuẩn tham chiếu thêm ở `data/gather-p2.json`.
- `fish.py` giữ bơi/sinh, `monsters.py` giữ Cá Sấu; vẫn dùng Streams và IdAllocator. Fixture `random_fish:false` tắt bơi/sinh; `monsters:[]` tắt quái mặc định.
- Sửa có lý do ở framework: contract/scenario/inventory để nhận dữ liệu mới, inputs/headless/runner/live để pause dừng gameplay. Hai lệnh gather phía trên đã bao gồm test P2 và quan.
- Điểm tích hợp ngày: `GatherSim(..., day=1, active_upgrades=None)`; xem `docs/gather-phase-2-xuannghia2.md`. Không coi dữ liệu day_plan/shop đã có là bộ điều phối ngày đã hoàn thành.
- Các test P1 đổi do Ticket-02 được giải thích trong tài liệu bàn giao; lỗi QA mẫu TEAM vẫn giữ bằng chứng riêng.

### Phase 3 — kho cá thể trong thời gian migration
- Main giữ v1.1 trước khi quán sẵn sàng. P3 dùng `tuning.freshness` và adapter với `version="1.2"`; không tự biến kho đếm thành cá thể ở đầu đọc v1.2.
- `FreshnessLedger` trả item dict JSON, giữ nhịp hao chính xác bên trong. Dùng cùng IdAllocator xuyên pha/ngày; sao item khi đưa vào snapshot/lost.
- `fresh` không làm tròn trong JSONL. Chạy `.\tools\gather.ps1 test`; tái tạo ca P3: `python3 tools/verify_gather_p3.py --out docs/proof/phase-3/xuannghia2`.
- Lệnh verify dùng profile riêng trong tiến trình, không phải smoke quán v1.2 mặc định. Xem ADR-0001 và docs/gather-phase-3-xuannghia2.md trước khi bật manifest.

### Phase 4 — benchmark và review
- `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`: render thật, warmup 3s; cần Chrome/Chromium/Edge. Đọc metadata trước kết luận về kích thước native/profile.
- Manifest vẫn 1.1, chưa có day/soak; không gắn tag/release toàn nhóm dựa riêng vào suite xanh. Xem docs/review/github-2026-11-21.md.

- Cập nhật QA df8f204: suite 134 test, 133 đạt và 1 expected failure (khách fixture thiếu order_status). Không báo 134/134 đạt hoặc coi expectedFailure là đã sửa.

- P4 bổ sung 61fffb9: benchmark kiểm native window/canvas 1280×720, Windows restore/resize chỉ PID browser riêng và xử lý DPI. Ghép UI 3e326c1: suite 137 test, 136 đạt + 1 expected failure. Bằng chứng mới ở bench-sized*.json và supplement-tests.txt; log cũ giữ nguyên lịch sử.
