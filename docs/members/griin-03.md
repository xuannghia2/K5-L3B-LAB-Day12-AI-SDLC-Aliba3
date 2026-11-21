# griin-03 — Lê Thanh Tùng

Bản ghi công việc thực tế của Lê Thanh Tùng (MSSV: 2A202603819).

- **Phần phụ trách chính**: `sim/quan` (Quán Ăn Chợ Nổi), xuyên suốt từ Phase 1 đến Phase 4.
- **Module & file phụ trách**: `chonoi/sim/quan.py`, `chonoi/scenario.py`, kiểm thử tại `tests/test_quan_units.py` và phối hợp với `tests/test_qa_p2_quan.py`.
- **Nội dung đã hoàn thành**:
  - **Phase 1 (PRD-0)**: Xây dựng toàn bộ mô phỏng Quán (Lát 3 Vòng đời khách hàng, Lát 4 Bếp & Bàn & Kinh tế), các sự kiện `cook_started`, `dish_ready`, `dish_picked`, `served`, `paid`, `customer_left`, `quan_end` và chốt doanh thu/uy tín chuẩn.
  - **Phase 2 (Ticket-02)**: Mở rộng 2 bếp (`B1`, `B2`), 4 bàn (`T1`–`T4`), 6 món ăn hoàn chỉnh với nguyên liệu mới (`ca_keo`, `keo_neo`).
  - **Phase 3 (Ticket-03)**: Tích hợp kho cá thể v1.2 song song kho đếm v1.1. Tích hợp `FreshnessLedger` cho quán, trừ hao tươi kho `0.25/s`, phát sự kiện `spoiled` khi fresh $< 30$, giữ chỗ nguyên liệu theo ID cá thể tươi nhất. Xử lý re-reserve hoặc chuyển `unfulfillable` khi cá thể đã giữ bị ươn. Tính giá món theo độ tươi trung bình của các cá thể sử dụng.
  - **Phase 4 & Khắc phục lỗi rà soát**:
    - Khắc phục triệt để lỗi QA-P2-01: khách từ scenario được gán `order_status = "reserved"` mặc định giúp bếp idle nhận nấu ngay (đã gỡ `expectedFailure` trong `test_qa_p2_quan.py`).
    - Bổ sung validation kiểm tra tính nhất quán giữa kho và lượng giữ chỗ, từ chối dish lạ và tôn trọng cờ `random_customers: false`.
- **AI sai ở đâu & Bài học**:
  - Khi viết test tính giá theo độ tươi ở tick 1, AI tính nhầm `base_price` do quên mất đầu tick đã diễn ra một bước hao tươi `quan_decay_per_s`. Qua việc đối chiếu kỹ lưỡng chu trình tick trong PRD-0 mục F, tôi đã điều chỉnh kịp thời công thức kiểm thử.
  - Bài học: Khi làm việc với hệ thống mô phỏng phức tạp theo tick, việc đọc và tuân thủ nghiêm ngặt từng bước trong chu kỳ tick là tối quan trọng để tránh sai lệch trạng thái vi mô.
- **Kiểm chứng**:
  - Toàn bộ test suite `PYTHONPATH=tests:. python3 -m unittest discover -s tests` đạt **136/136 test** (100% pass, 0 fail, 0 expectedFailure).


