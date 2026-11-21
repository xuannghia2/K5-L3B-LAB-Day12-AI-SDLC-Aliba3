# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Bắt đầu nhanh

```bash
git clone <fork-của-nhóm> && cd <fork-của-nhóm>
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v        # smoke test
python3 -m chonoi.live --mode gather                                # chơi thử trên trình duyệt (tùy chọn)
```

Game cần chế độ **headless** theo Test Contract (`python3 -m chonoi.headless --mode gather|quan …`) để được chạy và chấm tự động. **Công nghệ không ràng buộc**: khung Python trong `chonoi/` chỉ là gợi ý, chi tiết ở [`docs/STARTER.md`](docs/STARTER.md).

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.

### Chơi hai buổi trên Windows

Lệnh dưới dùng launcher `py -3` của Windows. Hai tiến trình chạy trên hai cổng riêng để mở đồng thời trong trình duyệt.

**1. Buổi sáng — thu thập và xuất kho**

```powershell
py -3 -m chonoi.live --mode gather --seed 1 --port 8000 --inventory-out kho.json
```

Mở `http://127.0.0.1:8000/`.

- `WASD` hoặc mũi tên: bơi.
- `E`: hái hoặc cập bến.
- `Space`: bắt cá.
- `R`: chơi lại.
- `P`: tạm dừng/tiếp tục.
- Khi cập bến hoặc buổi kết thúc hợp lệ, giỏ được ghi vào `kho.json`.

**2. Buổi tối — nạp kho rồi phục vụ**

Chỉ mở sau khi buổi sáng đã tạo `kho.json`:

```powershell
py -3 -m chonoi.live --mode quan --seed 1 --port 8001 --inventory kho.json
```

Mở `http://127.0.0.1:8001/`.

- `WASD` hoặc mũi tên: đi.
- `E`: tương tác với bếp/bàn.
- `R`: chơi lại.
- `P`: tạm dừng/tiếp tục.

Luồng nấu: đến bếp `B1`, nhấn `E` để lấy đơn đủ nguyên liệu → chờ bếp chuyển `ready` → nhấn `E` tại bếp để lấy món → mang đến bàn `T1` rồi nhấn `E` để phục vụ.

Nếu chưa có kho hoặc thử chạy quan độc lập, có thể dùng kho mẫu:

```powershell
py -3 -m chonoi.live --mode quan --seed 1 --port 8001 --inventory docs/contracts/inventory.sample.json
```

Chạy test live:

```powershell
$env:PYTHONPATH='tests;.'
py -3 -m unittest test_live -v
```

Nhấn `Ctrl+C` trong terminal để dừng server. Đóng trình duyệt không dừng server; mỗi server phải dừng ở terminal tương ứng.

## Bàn giao Phase 4 hiện tại

Cần Python 3.12+ (`python3` trên PATH); Python chỉ dùng thư viện chuẩn. Trên macOS/Linux, từ thư mục muốn lưu repo, ba lệnh mở GUI gather:

```sh
git clone https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3.git
cd K5-L3B-LAB-Day12-AI-SDLC-Aliba3
python3 -m chonoi.live --mode gather --seed 42
```

Mở địa chỉ server in ra; WASD/mũi tên di chuyển, E tương tác, Space bắt cá, R chơi lại. Phím P và nút pause đã được Hùng bổ sung tại 3e326c1; Esc chưa nối. Nút Tương phản cao hỗ trợ đọc cảnh báo. Lệnh trên được đối chiếu cú pháp; clean clone thực chạy trên Windows, chưa xác minh macOS/Linux.

Benchmark: `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json` (cần Chrome/Chromium/Edge). Test macOS/Linux: `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`. Windows: `.\tools\gather.ps1 test`.

[Bàn giao gather P4](docs/gather-phase-4-xuannghia2.md) và [review toàn GitHub](docs/review/github-2026-11-21.md) ghi kết quả và giới hạn. Main vẫn contract 1.1; chưa có day/Shop/soak hay release v1.0.0.

[Bảng kiểm chứng Phase 4](docs/verification/phase-4.md) ghi lần đo mới với native window và canvas đều 1280×720. [Credits](CREDITS.md) ghi nguồn và tình trạng cấp phép.
