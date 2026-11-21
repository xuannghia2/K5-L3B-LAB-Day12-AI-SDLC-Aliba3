# Phase 3 — phân tích tác động phần xuannghia2

| Phần | File / phụ thuộc | Trạng thái |
|---|---|---|
| Adapter/freshness | inventory.py, freshness.py, data/freshness-p3.json | Đã push 350f1fd |
| Gather cá thể | sim/gather.py, scenario.py, runner.py, jsonl.py, headless.py, live.py, contract.py | Đã push d255988 |
| Bằng chứng/API migration | tools/verify_gather_p3.py, docs/proof/phase-3, ADR/CHANGELOG | Bàn giao trong commit tài liệu |
| Quán cá thể/giữ chỗ/giá | Chủ sim/quan theo TEAM.md | Chưa thấy commit P3 khi kiểm GitHub trong phiên |
| day/HUD + bật v1.2/tag | Tích hợp nhóm sau khi quán sẵn sàng | Chưa xác nhận hoàn thành |

Giữ main v1.1 trong lúc migration; các test P3 chọn profile riêng.
Không ghi đạt smoke quán/ngày khi chỉ adapter nhận được file. Xem ADR-0001 cho thứ tự.
