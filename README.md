# hangman-game
Hangman (Đoán chữ)
## 1. Cách cài đặt & chạy
Yêu cầu: Python 3.10+ (không cần cài thư viện ngoài).
```bash
cd hangman
python3 cli.py
```
Làm theo hướng dẫn trên màn hình: chọn độ khó, chọn chủ đề, sau đó nhập từng
chữ cái để đoán. Gõ `hint` để dùng 1 lần gợi ý mỗi ván (tốn 1 lượt).
## 2. Cách chạy test
```bash
cd hangman
python3 -m unittest test_game_logic -v
```
Có 16 unit test, tất cả chỉ test `game_logic.py` (không đụng tới console),
bao gồm: đoán đúng, đoán sai, đoán trùng, thắng, thua, input không hợp lệ,
không phân biệt hoa/thường, dùng gợi ý, và lọc từ theo chủ đề/độ khó.
## 3. Cấu trúc project
```
hangman/
├── words.json          # Ngân hàng từ vựng (32 từ, có category + difficulty)
├── game_logic.py        # Toàn bộ luật chơi, KHÔNG có print()/input()
├── cli.py                # Giao diện console, chỉ gọi vào game_logic
├── test_game_logic.py    # Unit test cho phần logic
└── README.md
```
## 4. Quyết định thiết kế

- Tách logic khỏi giao diện (yêu cầu quan trọng nhất của đề bài):
`game_logic.py` không import bất kỳ thứ gì liên quan I/O. Mọi hành động
(`guess`, `use_hint`) nhận input thô và trả về một `GuessOutcome` (status +
message), không tự in ra màn hình. `cli.py` chỉ là lớp vỏ đọc `input()` và
gọi vào các hàm/property công khai của `HangmanGame`. Nhờ vậy có thể viết
thêm giao diện web/GUI sau này mà không sửa logic, và test được logic mà
không cần giả lập bàn phím.
Input không hợp lệ (F3): `guess()` không bao giờ raise exception cho
input sai định dạng — trả về `status="invalid"` kèm lý do. Chuỗi rỗng,
nhiều hơn 1 ký tự, ký tự không phải chữ cái, hoặc chữ đã đoán rồi đều
không bị trừ lượt.

- Không phân biệt hoa/thường và có sẵn nền cho tiếng Việt có dấu (F4, A5):
Hàm `normalize()` viết hoa toàn bộ và bỏ dấu tiếng Việt (dùng
`unicodedata.normalize("NFD", ...)` để tách dấu, xử lý riêng `Đ/đ` vì
Unicode không tách rời ký tự này). Từ bí mật và mọi chữ cái đoán đều đi
qua hàm này trước khi so khớp. Vì bộ từ vựng hiện tại là tiếng Anh nên tính
năng bỏ dấu chưa được dùng tới, nhưng nếu đổi `words.json` sang từ tiếng
Việt có dấu thì logic so khớp không cần sửa gì thêm.

- Gợi ý (A2): Cài bằng một biến đếm phạt (`hint_penalty`) tách riêng với
`wrong_letters`, để chữ cái được gợi ý không bị hiển thị lẫn vào danh sách
"đã đoán sai" nhưng vẫn trừ đúng 1 lượt.

- Độ khó & chủ đề (A1, A3): `WordBank` lọc từ theo `category`/`difficulty`
đọc từ `words.json`. Độ khó ảnh hưởng tới số lượt sai tối đa được phép
(`DIFFICULTY_RULES`), còn độ dài từ tự nhiên tăng dần theo `easy → hard` vì
bộ từ vựng được gán nhãn thủ công theo độ dài.
## 5. Giả định
Chương trình chơi bằng từ tiếng Anh (không dấu) để tránh rủi ro hiển thị
sai ký tự có dấu trên các terminal khác nhau; cơ chế `normalize()` đã sẵn
sàng cho tiếng Việt nếu cần.
"Chữ cái" được hiểu là 1 ký tự bảng chữ cái Latin (a-z), không tính số
hoặc ký tự đặc biệt.
## 6. Việc dùng AI
Đa số phần code trong repository được phát triển với sự hỗ trợ của AI, đặc biệt đối với Python do em chưa thành thạo hai ngôn ngữ này. Mình chủ yếu tự đưa ra ý tưởng, hướng giải quyết và sử dụng AI để hỗ trợ implementation, debug và tối ưu code.
## 7. Nếu có thêm thời gian sẽ làm tiếp
- A4 — Điểm số & lưu trữ: tính điểm dựa trên số lượt còn lại khi thắng,
lưu bảng xếp hạng ra file JSON riêng để giữ lại giữa các lần chạy.

- A5 — Hoàn thiện hỗ trợ tiếng Việt có dấu: thêm bộ từ vựng tiếng Việt
vào `words.json` và quyết định rõ có hiển thị lại dấu cho người chơi xem
hay không sau khi đoán đúng (hiện `normalize()` chỉ phục vụ so khớp, chưa
phục vụ hiển thị).

- A6 — Giao diện đồ họa: viết thêm `web.py` (Flask) hoặc GUI (Tkinter)
gọi trực tiếp vào `game_logic.HangmanGame`, không cần sửa file logic.
Thêm test cho `cli.py` bằng cách mock `input()`/`print()`.
