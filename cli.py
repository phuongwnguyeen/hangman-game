"""
cli.py
------
Giao diện dòng lệnh cho trò chơi Hangman.
"""

import os

from game_logic import DIFFICULTY_RULES, HangmanGame, WordBank, load_words

WORDS_FILE = os.path.join(os.path.dirname(__file__), "words.json")


def choose_from_list(prompt: str, options: list[str]) -> str:
    """Hàm phụ trợ cho CLI: hiện danh sách lựa chọn, bắt người chơi chọn hợp lệ."""
    print(prompt)
    for i, opt in enumerate(options, start=1):
        print(f"  {i}. {opt}")
    while True:
        raw = input("Chọn số tương ứng: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print("Lựa chọn không hợp lệ, thử lại.")


def print_state(game: HangmanGame) -> None:
    state = game.get_state()
    print()
    print("Từ cần đoán :", state["display_word"])
    print("Chữ đoán sai:", ", ".join(state["wrong_letters"]) or "(chưa có)")
    print("Lượt còn lại:", state["remaining_attempts"])


def play_one_round(bank: WordBank) -> None:
    difficulty = choose_from_list("Chọn độ khó:", list(DIFFICULTY_RULES.keys()))
    categories = ["(bất kỳ)"] + bank.categories()
    category_choice = choose_from_list("Chọn chủ đề:", categories)
    category = None if category_choice == "(bất kỳ)" else category_choice

    secret = bank.pick_random(category=category, difficulty=difficulty)
    max_wrong = DIFFICULTY_RULES[difficulty]["max_wrong"]
    game = HangmanGame(secret, max_wrong=max_wrong)

    print(f"\nBắt đầu ván mới! Độ khó: {difficulty} | Số lượt sai tối đa: {max_wrong}")
    hint_available = True

    while not game.is_over:
        print_state(game)
        raw = input(
            "Nhập 1 chữ cái để đoán"
            + (" (hoặc gõ 'hint' để dùng gợi ý)" if hint_available and not game.hint_used else "")
            + ": "
        ).strip()

        if raw.lower() == "hint":
            outcome = game.use_hint()
        else:
            outcome = game.guess(raw)

        if outcome.status == "invalid":
            print(f"-> Không hợp lệ: {outcome.message}")
        elif outcome.status == "already_guessed":
            print(f"-> {outcome.message}")
        elif outcome.status == "wrong":
            print("-> Sai rồi!")
        elif outcome.status == "correct":
            print("-> Đúng!" if not outcome.message else f"-> {outcome.message}")

    print_state(game)
    if game.is_won:
        print("\n*** BẠN ĐÃ THẮNG! ***")
    else:
        print(f"\n*** BẠN ĐÃ THUA! Từ bí mật là: {game.secret_word} ***")


def main() -> None:
    words = load_words(WORDS_FILE)
    bank = WordBank(words)

    print("=== TRÒ CHƠI ĐOÁN CHỮ (HANGMAN) ===")
    while True:
        play_one_round(bank)
        again = input("\nChơi lại không? (y/n): ").strip().lower()
        if again != "y":
            print("Cảm ơn bạn đã chơi!")
            break


if __name__ == "__main__":
    main()
