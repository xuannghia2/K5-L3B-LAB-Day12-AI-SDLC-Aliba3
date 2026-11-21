# Gather Phase 3 — xuannghia2

Nguồn: [Ticket-03](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg#phase-3), phát hành 10:59 ngày 21/11/2026 (Asia/Saigon).

## Trạng thái bàn giao

Adapter và gather v1.2 đã triển khai, có thể kiểm độc lập bằng tuning freshness.
**Manifest dùng chung vẫn v1.1**: khi kiểm GitHub trong phiên này chưa có commit quán P3,
QuanSim vẫn dùng kho đếm. Không bật một đầu v1.2 để rồi làm hỏng quán trên main.
Chưa xác nhận smoke hai tiến trình v1.2, day/HUD hoặc DoD toàn nhóm; không gắn tag phase-3.

Commit: [adapter](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/350f1fd),
[gather](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/commit/d255988).
Quyết định/thứ tự tích hợp: [ADR-0001](adr/0001-fresh-inventory-migration.md).

## Phần gather đã làm

- Hold cá thể theo thứ tự nhặt; file và inventory trong gather_end sắp id tự nhiên.
- Nhặt cấp id I liên tục, fresh ban đầu theo dữ liệu; chỉ hao từ bước kế.
- Hao hàng có sẵn đầu tick trước di chuyển/ngạt/hit/tương tác.
- Sự kiện spoiled đúng một lần khi vượt ngưỡng, theo id; hàng ươn vẫn chiếm ô và vẫn được bàn giao.
- Monster hit/faint giữ payload cá thể có độ tươi sau hao, theo thứ tự LIFO.
- Pause không hao tươi. Bến/hết giờ/ngất giữ thứ tự kết thúc; giới hạn tick không ghi đè kho.
- Đọc/ghi chọn schema theo version; v1.2 từ chối kho đếm và cá thể sai kiểu/id/kind/fresh.
- JSONL chỉ tiếp tục làm tròn tọa độ, không làm tròn trường fresh; file kho giữ đủ precision.

## API để quán và ngày sử dụng

```python
from chonoi.freshness import FreshnessLedger, copy_items
from chonoi.inventory import read_inventory, validate_fresh_items, write_inventory

ledger = FreshnessLedger(tuning, ids)  # tuning có freshness
stock = ledger.attach(inventory_items)
events = ledger.decay(stock, "stock")  # giảm theo quan_decay_per_s, trả spoiled
usable = [item for item in stock if not ledger.spoiled(item)]
```

- `attach` trả bản sao; gán lại stock/hold bằng kết quả đó. `decay` cập nhật fresh trên các dict của danh sách.
- Giữ chỗ của quán phải là id và chọn tươi nhất; adapter không tự làm logic giữ chỗ/giá thay QuanSim.
- Dùng **cùng IdAllocator** xuyên pha/ngày. `ledger.new(kind, fresh)` cấp id mới và giữ fresh được truyền;
  khi dựng mẫu ngày sau, cấp lại id bằng thứ tự mảng, không tái dùng id fixture đã dùng ở ngày đầu.
- `copy_items(items, sorted_ids=True)` cho bàn giao/file; không sắp lại hold khi cần LIFO.
- `read_inventory(path, version="1.2")` và `write_inventory(path, items, version="1.2")` dùng kho cá thể.
  Không truyền version thì đường cũ v1.1 được giữ để main trong thời gian migration vẫn chạy.
- Ledger giữ phân số nội bộ. Lưới tick được khôi phục sau file roundtrip chỉ khi cho cùng biểu diễn float,
  giúp tránh sai nhánh ở 30 do chuỗi hao dài. Không thêm trường nội bộ vào schema JSON.

## Bật v1.2 sau khi quán sẵn sàng

1. Chủ module quán tích hợp stock cá thể, giữ id, hao kho, giữ lại và giá theo tươi; kiểm fixture mâu thuẫn.
2. Chạy quán với `tuning.freshness` lấy từ `data/freshness-p3.json`, đọc đúng version và thử kho từ gather.
3. Bật `contract_version:"1.2"`, thêm `tuning.freshness` rồi chạy smoke hai tiến trình/day và migration test.
4. Cập nhật fixture/test P1–P2 bị thay schema, có lý do; giữ kiểm gameplay còn hiệu lực.

Dữ liệu quán/ngày đang tồn tại không chứng minh module đã đổi schema. Chưa làm mở rộng dòng lũ/đặt trước.

## Kiểm chứng và giới hạn

```powershell
.\tools\gather.ps1 test
python3 tools/verify_gather_p3.py --out docs/proof/phase-3/xuannghia2
```

Lệnh thứ hai dùng profile v1.2 **chỉ trong tiến trình kiểm chứng**, không sửa manifest dùng chung.
Nó gọi parser/headless với load_contract chọn profile kiểm thử; không gọi đây là smoke mặc định hai tiến trình.

- 17/17 test Phase 3 đạt (7 adapter, 10 gather/headless).
- 100/100 test trong phạm vi đạt; toàn suite 103/104, lỗi mẫu TEAM có sẵn.
- 5 ca bằng chứng chạy thành công; cùng seed cho byte giống nhau.
- [Test tổng](proof/phase-3/xuannghia2/gather-stage-tests.txt), [test có phạm vi](proof/phase-3/xuannghia2/gather-tests.txt).
- [Báo cáo/sha256](proof/phase-3/xuannghia2/verification-report.json), [spoiled](proof/phase-3/xuannghia2/threshold.log),
  [bàn giao](proof/phase-3/xuannghia2/dock.log), [kho](proof/phase-3/xuannghia2/dock-inventory.json),
  [nhặt mới](proof/phase-3/xuannghia2/pickup.log), [ngất](proof/phase-3/xuannghia2/faint.log).

17 test mới dùng profile rõ ràng; các test cũ vẫn kiểm đường v1.1, không bị đổi để che lỗi migration.
Người phụ trách quán có thể tái sử dụng ledger; chỉ sau khi nối hai đầu mới ghi đạt tích hợp chung.
