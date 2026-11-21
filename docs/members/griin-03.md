# griin-03 — Lê Thanh Tùng

Bản ghi công việc thực tế của Lê Thanh Tùng (MSSV: 2A202603819).

- Phần được phân công: `sim/quan`, Phase 1.
- Module phụ trách: `chonoi/sim/quan.py`, kiểm thử tại `tests/test_quan_units.py`.
- Các việc đã thực hiện:
  - Triển khai toàn diện Lát 3 (Khách hàng & Vòng đời): khách đến theo lịch `first_customer_tick`, chu kỳ `customer_interval_s`, tìm bàn trống, chọn món đủ nguyên liệu khả dụng (`stock - reserved`), giữ chỗ nguyên liệu `reserved`, đếm ngược kiên nhẫn `patience_ticks_left`, nếu hết kiên nhẫn thì rời bàn (`customer_left`) kèm phạt uy tín `left_reputation_delta`. Khi không đủ món thì phát `no_dish`.
  - Triển khai toàn diện Lát 4 (Bếp, Bàn & Kinh tế): tương tác bếp nấu theo `cook_s`, chuyển trạng thái `ready` (`dish_ready`), bốc món lên tay (`dish_picked`), bưng món phục vụ khách tại bàn (`served`), tính tiền tip theo `tip_rate` khi kiên nhẫn còn lại $\ge 50\%$, khách ăn xong trả tiền (`paid`), thưởng uy tín `tip_reputation`.
  - Xử lý kết thúc ca khi hết giờ (`quan_end`): dọn sạch khách và chốt doanh thu, uy tín, điểm số theo đúng Test Contract v1.0.
- Kiểm chứng:
  - Viết bộ unit test `tests/test_quan_units.py` đạt 4/4 test (100%).
  - Chạy toàn bộ 61 test của repo, đảm bảo không phá vỡ bất kỳ hợp đồng Test Contract nào của team.
