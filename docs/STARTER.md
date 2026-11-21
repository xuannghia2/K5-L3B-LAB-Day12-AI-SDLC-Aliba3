# Chi tiết khung kỹ thuật (starter Python)

> Starter chỉ là **gợi ý**: công nghệ không ràng buộc. Trang này giải thích cái gì đã có sẵn và cách chơi thử.

## Chạy thử

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v     # smoke test (phải xanh; nếu dùng starter Python)
python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl
```

Hai chế độ của contract v1.0: `gather` (buổi sáng: lặn và hái, nhìn ngang, vị trí `[x, d]`, `d` là độ sâu) và `quan` (buổi tối: mở quán, nhìn từ trên xuống, vị trí `[x, z]`). Chế độ `day` có từ phase sau.

## Chơi thử trực tiếp trên trình duyệt

Xem phần **Chơi thử trực tiếp trên trình duyệt (Windows)** ở cuối tài liệu để chạy buổi sáng, buổi tối, nối kho hai buổi và điều khiển bàn phím.

## Công nghệ: tự chọn (starter chỉ là gợi ý, KHÔNG bắt buộc)

Nhóm được dùng **bất kỳ ngôn ngữ/engine nào**. Thứ duy nhất bắt buộc là **Test Contract** (chế độ headless theo tài liệu phase) và `game.contract.json` khai đúng `build_cmd`, `headless_cmd`.

`chonoi/` là một khung **Python 3** (chỉ thư viện chuẩn) giảng viên làm sẵn để tiết kiệm thời gian: đọc tham số, đọc inputs/scenario/kho, kiểm lỗi (mã thoát 2), vòng tick 60 Hz, RNG có seed, cấp/sắp id, ghi JSONL tất định, ghi file kho an toàn. **Luật chơi do nhóm viết** (tìm `TODO(nhóm)`). Dùng hay không tùy nhóm.

| Khung Python đã có | Nhóm viết |
|---|---|
| CLI + kiểm lỗi, mã thoát 0/1/2 | `chonoi/sim/gather.py`: oxy, ngạt, Máu, ngất, hái nút, bắt cá, giỏ (LIFO) |
| Đọc inputs, cạnh lên, chuẩn hóa vector | `chonoi/sim/quan.py`: khách, giữ chỗ, bếp, bưng, phục vụ, tiền, uy tín |
| Bơi, tăng/giảm tốc, chặn mép (`d` không âm), cập bến, hết giờ | Điều chỉnh nút hái / bầy cá mặc định (dữ liệu ở `game.contract.json`) |
| Đọc/ghi file kho, ghi nguyên tử | Kiểm mâu thuẫn scenario mức luật (`scenario.py`) |
| JSONL tất định, làm tròn 3 chữ số, sắp id | Hiển thị / HUD thật (khung chỉ có cửa sổ thử `chonoi.live` bằng hình khối tạm) |
| Cửa sổ thử trên trình duyệt (`python3 -m chonoi.live`) | Đồ họa, âm thanh, menu, HUD hoàn chỉnh theo PRD |

### Nếu nhóm đổi sang ngôn ngữ khác
1. Sửa `build_cmd`, `run_cmd` (hiện là `python3 -m chonoi.live --mode gather`), `headless_cmd` trong `game.contract.json` cho ngôn ngữ của nhóm.
2. Nếu nhóm dùng CI: sửa bước **Build** và **Test** trong `.github/workflows/ci.yml` (cài runtime cần thiết); không dùng CI thì xóa file đó.
3. **Giữ** `tests/test_smoke_p1.py`: đây là test **hộp đen**, chỉ chạy `headless_cmd` rồi đọc JSONL/file kho, nên dùng nguyên cho mọi ngôn ngữ. **Xóa** `chonoi/`, `tests/test_python_starter_units.py` và `tests/test_live.py` nếu không dùng; viết unit test bằng ngôn ngữ của nhóm.
4. Vẫn phải qua cùng Test Contract: cùng seed → output giống từng byte.

Lưu ý: `tools/check_team.py` (kiểm danh sách thành viên) là script Python độc lập, không liên quan tới ngôn ngữ của game.

## Quy tắc vàng

- Số liệu chỉ nằm trong `game.contract.json`; luật chỉ đọc từ đó.
- Ngẫu nhiên chỉ qua `Streams`; không dùng đồng hồ hệ thống. Cùng seed → output giống từng byte.
- Nhánh chính luôn **chạy được** (nhất là lúc gắn tag). Cách đạt điều đó do nhóm chọn.
- Cùng commit vào một repo chung; mỗi người có dấu vết của mình.

## Tài liệu trong repo

[`TEAM.md`](../TEAM.md) (vai + thỏa thuận nhóm) · [`AGENTS.md`](../AGENTS.md) · `docs/contracts/` (hợp đồng tích hợp: nên chốt sớm, hình thức tự chọn) · `docs/{plan,verification,proof,adr,members}/` (gợi ý) · `docs/{clarify,standup,retro,ai-usage-log}.md`.

## Chơi thử trực tiếp trên trình duyệt (Windows)

Hai buổi là hai tiến trình riêng và được nối bằng file kho `kho.json`.

### Chạy buổi sáng

```powershell
py -3 -m chonoi.live --mode gather --seed 1 --port 8000 --inventory-out kho.json
```

Mở `http://127.0.0.1:8000/`. Dùng `WASD/mũi tên` để bơi, `E` để hái/cập bến, `Space` để bắt cá và `R` để chơi lại.

Chỉ khi buổi sáng kết thúc hợp lệ thì `kho.json` mới được ghi. Ngất hoặc hết tick theo cách chưa cập bến có thể không ghi kho mới; xem thông báo kết thúc trong game.

### Chạy buổi tối

Sau khi buổi sáng đã tạo `kho.json`, mở tiến trình thứ hai:

```powershell
py -3 -m chonoi.live --mode quan --seed 1 --port 8001 --inventory kho.json
```

Mở `http://127.0.0.1:8001/`. Dùng `WASD/mũi tên` để đi, `E` để tương tác bếp/bàn và `R` để chơi lại.

### Nếu chỉ muốn thử buổi tối

Có thể dùng kho mẫu không phụ thuộc buổi sáng:

```powershell
py -3 -m chonoi.live --mode quan --seed 1 --port 8001 --inventory docs/contracts/inventory.sample.json
```

Kho trống thì khách sẽ không gọi món nấu được và sẽ phát `no_dish`.

### Quy trình nấu và phục vụ

1. Chờ khách xuất hiện tại bàn `T1`.
2. Đến gần bếp `B1` và nhấn `E` để nấu đơn cũ nhất được giữ nguyên liệu.
3. Chờ bếp chuyển sang `ready`.
4. Nhấn `E` tại bếp để bốc món lên tay.
5. Mang món đến bàn `T1`, nhấn `E` để phục vụ.
6. Chờ khách ăn xong; tiền, tip và uy tín được cập nhật theo contract.

Nhấn `Ctrl+C` trong từng terminal để dừng server tương ứng.
