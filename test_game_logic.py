"""
test_game_logic.py
-------------------
"""

import unittest

from game_logic import HangmanGame, WordBank, normalize

class TestHangmanGame(unittest.TestCase):

    def test_correct_guess_reveals_letter_and_keeps_attempts(self):
        game = HangmanGame("cat", max_wrong=6)
        outcome = game.guess("a")
        self.assertEqual(outcome.status, "correct")
        self.assertEqual(game.display_word, "_ A _")
        self.assertEqual(game.remaining_attempts, 6)  # không bị trừ lượt

    def test_wrong_guess_deducts_one_attempt(self):
        game = HangmanGame("cat", max_wrong=6)
        outcome = game.guess("z")
        self.assertEqual(outcome.status, "wrong")
        self.assertEqual(game.remaining_attempts, 5)
        self.assertIn("Z", game.wrong_letters)

    def test_duplicate_guess_does_not_deduct_attempt(self):
        game = HangmanGame("cat", max_wrong=6)
        game.guess("z")  # sai lần 1 -> còn 5 lượt
        outcome = game.guess("z")  # đoán lại chữ đã sai
        self.assertEqual(outcome.status, "already_guessed")
        self.assertEqual(game.remaining_attempts, 5)  # không bị trừ thêm

    def test_win_when_all_letters_revealed(self):
        game = HangmanGame("cat", max_wrong=6)
        for letter in "cat":
            game.guess(letter)
        self.assertTrue(game.is_won)
        self.assertTrue(game.is_over)
        self.assertFalse(game.is_lost)

    def test_lose_when_out_of_attempts(self):
        game = HangmanGame("cat", max_wrong=2)
        game.guess("x")
        game.guess("y")
        self.assertTrue(game.is_lost)
        self.assertTrue(game.is_over)
        self.assertFalse(game.is_won)

    def test_invalid_inputs_do_not_crash_or_deduct_attempts(self):
        game = HangmanGame("cat", max_wrong=6)
        cases = ["", "ab", "1", "!", None]
        for case in cases:
            outcome = game.guess(case)
            self.assertEqual(outcome.status, "invalid")
        self.assertEqual(game.remaining_attempts, 6)

    def test_case_insensitive_matching(self):
        game = HangmanGame("Cat", max_wrong=6)
        outcome = game.guess("A")
        self.assertEqual(outcome.status, "correct")
        outcome2 = game.guess("a")
        self.assertEqual(outcome2.status, "already_guessed")

    def test_hint_reveals_letter_and_costs_one_attempt(self):
        game = HangmanGame("cat", max_wrong=6)
        outcome = game.use_hint()
        self.assertEqual(outcome.status, "correct")
        self.assertEqual(game.remaining_attempts, 5)
        self.assertTrue(game.hint_used)

    def test_hint_can_only_be_used_once(self):
        game = HangmanGame("cat", max_wrong=6)
        game.use_hint()
        outcome = game.use_hint()
        self.assertEqual(outcome.status, "invalid")

    def test_no_actions_allowed_after_game_over(self):
        game = HangmanGame("cat", max_wrong=1)
        game.guess("z")  # thua ngay
        self.assertTrue(game.is_over)
        outcome = game.guess("c")
        self.assertEqual(outcome.status, "invalid")

    def test_normalize_strips_vietnamese_accents(self):
        self.assertEqual(normalize("đường"), "DUONG")
        self.assertEqual(normalize("Á"), "A")


class TestWordBank(unittest.TestCase):

    def setUp(self):
        self.words = [
            {"word": "cat", "category": "animal", "difficulty": "easy"},
            {"word": "elephant", "category": "animal", "difficulty": "hard"},
            {"word": "chef", "category": "job", "difficulty": "easy"},
        ]
        self.bank = WordBank(self.words)

    def test_filter_by_category(self):
        result = self.bank.filter(category="animal")
        self.assertEqual(len(result), 2)

    def test_filter_by_difficulty(self):
        result = self.bank.filter(difficulty="easy")
        words = {w["word"] for w in result}
        self.assertEqual(words, {"cat", "chef"})

    def test_filter_no_match_raises(self):
        with self.assertRaises(ValueError):
            self.bank.filter(category="plant")

    def test_pick_random_returns_valid_word(self):
        picked = self.bank.pick_random(category="job")
        self.assertEqual(picked, "chef")

    def test_empty_word_list_raises(self):
        with self.assertRaises(ValueError):
            WordBank([])


if __name__ == "__main__":
    unittest.main()
