import json
import tempfile
import unittest
from pathlib import Path

from proofdesk import Register
from proofdesk.cli import main


class RegisterTests(unittest.TestCase):
    def test_add_assigns_incrementing_ids(self):
        reg = Register()
        self.assertEqual(reg.add("a").id, 1)
        self.assertEqual(reg.add("b").id, 2)
        reg.remove(1)
        self.assertEqual(reg.add("c").id, 3)

    def test_empty_claim_rejected(self):
        with self.assertRaises(ValueError):
            Register().add("   ")

    def test_status_must_be_known(self):
        reg = Register()
        reg.add("x")
        with self.assertRaises(ValueError):
            reg.set_status(1, "maybe")

    def test_verified_needs_evidence(self):
        reg = Register()
        reg.add("x")
        reg.set_status(1, "verified")
        messages = [i.message for i in reg.validate()]
        self.assertEqual(len(messages), 3)

    def test_verified_with_evidence_is_clean(self):
        reg = Register()
        reg.add("x", "https://example.com", "2026-11-07", "shots/x.png")
        reg.set_status(1, "verified")
        self.assertEqual(reg.validate(), [])

    def test_reported_needs_source(self):
        reg = Register()
        reg.add("x")
        reg.set_status(1, "reported")
        self.assertEqual(len(reg.validate()), 1)

    def test_json_round_trip(self):
        reg = Register()
        reg.add("hindi ok: मुफ़्त?", "https://example.com")
        again = Register.from_json(reg.to_json())
        self.assertEqual(again.claims[0].text, "hindi ok: मुफ़्त?")

    def test_markdown_escapes_pipes(self):
        reg = Register()
        reg.add("a | b")
        self.assertIn("a \\| b", reg.to_markdown())

    def test_summary_counts(self):
        reg = Register()
        reg.add("a")
        reg.add("b")
        reg.set_status(2, "false")
        self.assertEqual(reg.summary()["false"], 1)
        self.assertEqual(reg.summary()["unverified"], 1)


class CliTests(unittest.TestCase):
    def test_add_then_check_fails_for_weak_verified(self):
        with tempfile.TemporaryDirectory() as d:
            f = str(Path(d) / "r.json")
            self.assertEqual(main(["-f", f, "add", "Pro is free"]), 0)
            self.assertEqual(main(["-f", f, "status", "1", "verified"]), 0)
            self.assertEqual(main(["-f", f, "check"]), 1)
            data = json.loads(Path(f).read_text(encoding="utf-8"))
            self.assertEqual(data[0]["status"], "verified")

    def test_unknown_id_returns_error_code(self):
        with tempfile.TemporaryDirectory() as d:
            f = str(Path(d) / "r.json")
            self.assertEqual(main(["-f", f, "status", "9", "verified"]), 2)


if __name__ == "__main__":
    unittest.main()
