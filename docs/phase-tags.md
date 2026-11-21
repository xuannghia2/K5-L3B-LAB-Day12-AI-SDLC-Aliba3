# Tag các phase — Aliba3

Theo yêu cầu trực tiếp của trưởng nhóm, đã tạo và push ba annotated tag ngày 21/11/2026 (Asia/Saigon). Tagger dùng thời điểm tạo thật, không đặt lùi ngày. Đây là mốc snapshot, không tự xác nhận toàn bộ tiêu chí đã đạt.

| Tag | Commit | Lý do chọn / giới hạn |
|---|---|---|
| [phase-1](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/tree/phase-1) | f9477e32a97ae8b0ce7bfe366fe507577aac6f84 | Snapshot cuối trước Ticket-02. QA hồi cứu 61/62, có lỗi TEAM lịch sử và fixture khách; xem verification/phase-1.md |
| [phase-2](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/tree/phase-2) | 2fd97ccc6c3afba77dcb20f49b8176807719bcb2 | Sau gather v1.1 và test/phản tư quán P2, trước migration; day/Shop chưa hoàn thành |
| [phase-3](https://github.com/xuannghia2/K5-L3B-LAB-Day12-AI-SDLC-Aliba3/tree/phase-3) | bc764b9a197804f7ce6a8bd38910e739012a865d | Snapshot tích hợp và QA P3 mới nhất khi gắn; có cả code P4 do cùng main. Manifest vẫn 1.1; 152 test gồm 149 đạt và 3 expectedFailure QA-P3-01..03; xem verification/phase-3.md |

Đã kiểm bằng `git ls-remote --tags origin`: cả ba tag trỏ đúng commit, push bằng `--atomic`. Không di chuyển hay ghi đè tag có sẵn. [Log kiểm trước gắn tag](proof/phase-4/xuannghia2/pre-phase-tags-tests.txt).

Các ghi chú “repo chưa có tag” trong báo cáo cũ là ảnh chụp lịch sử trước thao tác này. Chưa tạo phase-4 hoặc v1.0.0. Khi sửa lỗi tiếp, giữ nguyên các tag snapshot này; không force-update làm mất dấu mốc đã công bố.
