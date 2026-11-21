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
- `.\tools\gather.ps1 test`: chạy luật gather, headless, smoke, starter và live; dùng trước khi bàn giao thay đổi gather. Lệnh có phạm vi, không thay thế chạy toàn bộ suite trước push.
- `.\tools\gather.ps1 play -Seed 1 -Port 8000`: mở server chơi thử gather; dùng để người review kiểm bơi, oxy, hái/bắt và cập bến.
- Windows: script ưu tiên môi trường riêng `.tools/python` cạnh repo hoặc `CHONOI_PYTHON`, chỉ đổi biến môi trường trong thời gian chạy. Smoke test vẫn dùng `python3` theo contract.
- Lỗi nền đã xác minh: `test_team_check.test_template_is_rejected` phụ thuộc TEAM.md thật nên fail sau khi điền nhóm; xem log `docs/proof/phase-1/xuannghia2/all-tests.txt`. Không sửa luật/team để làm test này xanh.
