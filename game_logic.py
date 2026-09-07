"""
game_logic.py
--------------
Toàn bộ luật chơi Hangman được đặt ở đây.
"""

from __future__ import annotations

import json
import random
import unicodedata
from dataclasses import dataclass
from typing import Optional


# =========================================================
# 1. Đọc & lọc dữ liệu từ vựng
# =========================================================

def load_words(path: str) -> list[dict]:
    """Đọc danh sách từ vựng từ file JSON.
    Mỗi phần tử có dạng: {"word": str, "category": str, "difficulty": str}
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    """Chuẩn hóa chuỗi: viết hoa toàn bộ + bỏ dấu tiếng Việt.
    Dùng để so khớp không phân biệt hoa/thường (F4) và làm nền tảng sẵn
    cho việc hỗ trợ tiếng Việt có dấu sau này (A5) mà không cần sửa logic chính.
    """
    text = text.upper()
    decomposed = unicodedata.normalize("NFD", text)
    no_accent = "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")
    # unicodedata không tách rời Đ/đ thành D + dấu, nên xử lý riêng
    no_accent = no_accent.replace("\u0110", "D")
    return no_accent


DIFFICULTY_RULES = {
    "easy":   {"max_wrong": 8},
    "medium": {"max_wrong": 6},
    "hard":   {"max_wrong": 5},
}


class WordBank:
    """Chọn từ bí mật theo chủ đề / độ khó.
    Nhận sẵn list đã load (không tự đọc file) để dễ test mà không phụ thuộc ổ đĩa.
    """

    def __init__(self, words: list[dict]):
        if not words:
            raise ValueError("Danh sách từ vựng rỗng")
        self.words = words

    def categories(self) -> list[str]:
        return sorted({w["category"] for w in self.words if "category" in w})

    def filter(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> list[dict]:
        result = self.words
        if category:
            result = [w for w in result if w.get("category") == category]
        if difficulty:
            result = [w for w in result if w.get("difficulty") == difficulty]
        if not result:
            raise ValueError("Không tìm thấy từ nào khớp với bộ lọc đã chọn")
        return result

    def pick_random(
        self,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> str:
        candidates = self.filter(category, difficulty)
        return random.choice(candidates)["word"]


# =========================================================
# 2. Trạng thái & luật chơi
# =========================================================

@dataclass
class GuessOutcome:
    """Kết quả trả về sau mỗi hành động (đoán chữ / dùng gợi ý)."""
    status: str            # "correct" | "wrong" | "already_guessed" | "invalid"
    message: str = ""      # mô tả thêm (đặc biệt hữu ích khi status = "invalid")


class HangmanGame:
    """Một ván chơi Hangman. Không chứa bất kỳ I/O nào."""

    def __init__(self, secret_word: str, max_wrong: int = 6):
        if not secret_word or not secret_word.isalpha():
            raise ValueError("Từ bí mật phải là chuỗi chữ cái, không được rỗng")
        if max_wrong <= 0:
            raise ValueError("Số lượt đoán sai tối đa phải > 0")

        self.secret_word: str = normalize(secret_word)
        self.max_wrong: int = max_wrong
        self.correct_letters: set[str] = set()
        self.wrong_letters: set[str] = set()
        self.hint_used: bool = False
        self._hint_penalty: int = 0

    # ---------- Hành động ----------

    def guess(self, letter: Optional[str]) -> GuessOutcome:
        """Xử lý một lượt đoán 1 chữ cái.
        Theo yêu cầu F3: input không hợp lệ KHÔNG được trừ lượt và KHÔNG được
        làm chương trình crash -> luôn trả GuessOutcome, không bao giờ raise.
        """
        if self.is_over:
            return GuessOutcome("invalid", "Ván chơi đã kết thúc, không thể đoán thêm")

        if letter is None or len(letter) != 1:
            return GuessOutcome("invalid", "Vui lòng nhập đúng 1 ký tự")

        norm = normalize(letter)
        if not norm.isalpha():
            return GuessOutcome("invalid", "Ký tự phải là một chữ cái")

        if norm in self.correct_letters or norm in self.wrong_letters:
            return GuessOutcome("already_guessed", f"Chữ '{norm}' đã được đoán trước đó")

        if norm in self.secret_word:
            self.correct_letters.add(norm)
            return GuessOutcome("correct")

        self.wrong_letters.add(norm)
        return GuessOutcome("wrong")

    def use_hint(self) -> GuessOutcome:
        """A2: lộ ngẫu nhiên 1 chữ cái chưa đoán được, đổi lại mất 1 lượt.
        Chỉ dùng được 1 lần mỗi ván.
        """
        if self.is_over:
            return GuessOutcome("invalid", "Ván chơi đã kết thúc")
        if self.hint_used:
            return GuessOutcome("invalid", "Mỗi ván chỉ được dùng gợi ý 1 lần")

        remaining = [c for c in set(self.secret_word) if c not in self.correct_letters]
        if not remaining:
            return GuessOutcome("invalid", "Không còn chữ cái nào để gợi ý")

        letter = random.choice(remaining)
        self.hint_used = True
        self._hint_penalty += 1
        self.correct_letters.add(letter)
        return GuessOutcome("correct", f"Gợi ý: chữ '{letter}'")

    # ---------- Trạng thái (chỉ đọc) ----------

    @property
    def remaining_attempts(self) -> int:
        used = len(self.wrong_letters) + self._hint_penalty
        return max(self.max_wrong - used, 0)

    @property
    def display_word(self) -> str:
        return " ".join(c if c in self.correct_letters else "_" for c in self.secret_word)

    @property
    def is_won(self) -> bool:
        return all(c in self.correct_letters for c in self.secret_word)

    @property
    def is_lost(self) -> bool:
        return self.remaining_attempts <= 0 and not self.is_won

    @property
    def is_over(self) -> bool:
        return self.is_won or self.is_lost

    def get_state(self) -> dict:
        """Gói toàn bộ trạng thái hiện tại thành dict — tiện cho bất kỳ giao diện
        nào (console/web/GUI) hiển thị mà không cần biết chi tiết bên trong lớp này.
        """
        return {
            "display_word": self.display_word,
            "wrong_letters": sorted(self.wrong_letters),
            "remaining_attempts": self.remaining_attempts,
            "is_won": self.is_won,
            "is_lost": self.is_lost,
            "is_over": self.is_over,
            "secret_word": self.secret_word if self.is_over else None,
            "hint_used": self.hint_used,
        }
