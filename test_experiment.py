import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch
from experiment import Client, action, information_gain, load_env, run


class BenchmarkTests(unittest.TestCase):
    def test_env_quotes_comments_and_shell_precedence(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"EXISTING": "shell"}, clear=True):
            path = Path(directory) / ".env"
            path.write_text('# comment\nGROQ_API_KEY="fake#key" # comment\nEXISTING=file\nexport GROQ_MODEL=test # comment\n', encoding="utf-8")
            load_env(path)
            self.assertEqual(os.environ["GROQ_API_KEY"], "fake#key")
            self.assertEqual(os.environ["EXISTING"], "shell")
            self.assertEqual(os.environ["GROQ_MODEL"], "test")

    def test_groq_uses_own_key_and_endpoint(self):
        with patch.dict(os.environ, {"GROQ_API_KEY": "fake-groq", "OPENAI_API_KEY": "fake-openai"}, clear=True):
            client = Client("test", 100, "groq")
            self.assertEqual(client.key, "fake-groq")
            self.assertEqual(client.endpoint, "https://api.groq.com/openai/v1/chat/completions")

    def test_information_gain_balanced_split(self):
        self.assertAlmostEqual(information_gain([1, 1, 1, 1], ["yes", "yes", "no", "no"]), 1)
        self.assertEqual(information_gain([1, 1], ["yes", "yes"]), 0)

    def test_invalid_prediction(self):
        with self.assertRaises(ValueError):
            information_gain([1, 1], ["yes"])

    def test_selection_uses_computed_gain(self):
        client = Mock()
        client.ask.return_value = {"kind": "candidates", "hypotheses": [
            {"weight": 1}, {"weight": 1}, {"weight": 2}], "questions": [
            {"text": "uninformative", "answers": ["yes"] * 3},
            {"text": "balanced", "answers": ["yes", "yes", "no"]},
            {"text": "skewed", "answers": ["yes", "no", "no"]}]}
        result, _ = action(client, "information_gain", "statement", [], {})
        self.assertEqual(result["text"], "balanced")

    def test_final_answer_after_budget_and_secret_isolation(self):
        client = Mock()
        client.calls = []
        client.ask.side_effect = [{"kind": "question", "text": "A question?"},
            {"answer": "yes"}, {"kind": "solution", "text": "An explanation"},
            {"correct": True, "checks": [{"criterion": "secret criterion", "passed": True}]}]
        puzzle = {"id": "fixture", "statement": "public", "solution": "SECRET", "rubric": ["secret criterion"]}
        row, _ = run(client, puzzle, "naive", 1, 1)
        self.assertTrue(row["success"])
        self.assertEqual(row["questions"], 1)
        self.assertEqual(row["guesses"], 1)
        for call in client.ask.call_args_list:
            if call.args[2] == "solver":
                self.assertNotIn("SECRET", str(call.args[1]))
                self.assertNotIn("secret criterion", str(call.args[1]))

    def test_referee_errors_are_not_successes(self):
        client = Mock()
        client.calls = []
        client.ask.side_effect = [{"kind": "solution", "text": "guess"}, {"correct": "false"}]
        row, _ = run(client, {"id": "x", "statement": "p", "rubric": ["a"]}, "naive", 1, 2)
        self.assertFalse(row["success"])
        self.assertEqual(row["status"], "error")


if __name__ == "__main__":
    unittest.main()
