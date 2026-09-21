import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_batch import solve, validate, make_board, component


class BatchTests(unittest.TestCase):
    def test_known_shortest_route_with_detour_for_key(self):
        board = ["#######", "#S.A.E#", "#.#.###", "#a....#", "#######"]
        states = solve(board)
        self.assertEqual(len(states) - 1, 8)
        keys = [i for i, (x, y, mask) in enumerate(states) if board[y][x] == "a"]
        door = next(i for i, (x, y, mask) in enumerate(states) if board[y][x] == "A")
        self.assertLess(keys[0], door)

    def test_key_behind_its_own_door_is_unsolvable(self):
        self.assertEqual(solve(["#######", "#SAa.E#", "#######"]), [])

    def test_unreachable_exit(self):
        self.assertEqual(solve(["#######", "#S.#.E#", "#######"]), [])

    def test_all_public_samples_and_family_constraints(self):
        batch = json.loads((ROOT / "site/data/batch.json").read_text(encoding="utf-8"))
        self.assertEqual(batch["count"], 24)
        fingerprints = set()
        for metadata in batch["samples"]:
            with self.subTest(sample=metadata["id"]):
                sample = json.loads((ROOT / "site" / metadata["json"]).read_text(encoding="utf-8"))
                self.assertTrue(validate(sample))
                board = sample["board"]
                fingerprints.add(tuple(board))
                start = next((x, y) for y, r in enumerate(board) for x, c in enumerate(r) if c == "S")
                doors = {(x, y) for y, r in enumerate(board) for x, c in enumerate(r) if c in "AB"}
                keys = {(x, y) for y, r in enumerate(board) for x, c in enumerate(r) if c in "ab"}
                before_any_door = component(board, start, doors)
                if sample["family"] == "parallel":
                    self.assertTrue(keys.issubset(before_any_door))
                if sample["family"] == "sequence":
                    key_b = next((x, y) for y, r in enumerate(board) for x, c in enumerate(r) if c == "b")
                    self.assertNotIn(key_b, before_any_door)
        self.assertEqual(len(fingerprints), 24, "Batch repeats an identical board")

    def test_seed_is_reproducible(self):
        self.assertEqual(make_board(1101, "single"), make_board(1101, "single"))

    def test_validator_rejects_illegal_jump(self):
        sample = json.loads((ROOT / "site/data/samples/EX-017.json").read_text(encoding="utf-8"))
        broken = copy.deepcopy(sample)
        broken["solution"][1][0] = broken["solution"][0][0] + 4
        with self.assertRaises(AssertionError):
            validate(broken)

    def test_validator_rejects_wrong_visual_frame(self):
        sample = json.loads((ROOT / "site/data/samples/EX-017.json").read_text(encoding="utf-8"))
        sample["steps"][-1]["visual"]["frame"] = 0
        with self.assertRaises(AssertionError):
            validate(sample)


if __name__ == "__main__":
    unittest.main()
