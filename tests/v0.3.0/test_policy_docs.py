"""Check the published decision rules, without implementing an operation gate."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/v0.3.0"


class PolicyDocsTest(unittest.TestCase):
    def test_operation_permission_requires_all_six_conditions(self):
        section = (DOCS / "policy.md").read_text(encoding="utf-8").split("## 4. 実運用の許可\n", 1)[1]
        requirements = re.findall(r"^\d+\. (.+)$", section, re.MULTILINE)
        self.assertEqual(len(requirements), 6)
        for requirement, terms in zip(requirements, (
            ("正式採用",),
            ("対象", "契約", "承認範囲"),
            ("実データ", "取得手順", "期限", "停止方式"),
            ("実行主体", "権限"),
            ("独立設計レビュー", "完了"),
            ("実運用条件", "実証"),
        )):
            with self.subTest(terms=terms):
                for term in terms:
                    self.assertIn(term, requirement)
        self.assertIn("必須条件が一つでも未達なら実運用許可を発行しない", section)
        self.assertIn("規約採用や合成試作から実運用許可を発行しない", section)
        for state in ("UNKNOWN", "NOT_TESTED", "FAIL"):
            self.assertIn(state, section)

    def test_classification_outcomes_in_rule_order(self):
        audit = (DOCS / "gates-and-audit.md").read_text(encoding="utf-8")
        section = audit.split("## 分類違反と分類未確定\n", 1)[1].split("\n## ", 1)[0]
        rows = [
            tuple(value.strip() for value in line.strip("|").split("|"))
            for line in section.splitlines() if line.startswith("| ")
        ][2:]
        self.assertEqual(len(rows), 3)
        low, unknown, valid = rows
        self.assertIn("所有者指定済みのLevel 3", low[0])
        self.assertIn("所有者指定がなくても規約上の最低Level 3が確定", low[0])
        self.assertEqual(low[1:], ("`FAIL`", "受入 `FAIL`、Gate A/B/C不成立", "該当操作を停止"))
        self.assertIn("最低分類が未確定", unknown[0])
        self.assertEqual(unknown[1:], (
            "`UNKNOWN`", "分類に依存するGate・受入を保留", "該当する危険な転送・公開・破壊等を停止",
        ))
        self.assertIn("保存・再取得・検証等の条件を個別に判定", valid[2])
        self.assertIn("別途必要な許可", valid[3])
        self.assertIn("既知のSHA不一致", section)
        self.assertIn("依存する受入は `FAIL`", section)
        self.assertIn("無関係な安全な作業は継続できる", section)

    def test_relative_links_resolve(self):
        for path in (ROOT / "README.md", *sorted(DOCS.glob("*.md"))):
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in link:
                    continue
                file, _, anchor = link.partition("#")
                target = path.parent / file if file else path
                with self.subTest(path=path.name, link=link):
                    self.assertTrue(target.is_file())
                    if anchor:
                        headings = re.findall(r"^#{1,6} (.+)$", target.read_text(encoding="utf-8"), re.MULTILINE)
                        self.assertIn(anchor, [
                            re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                            for heading in headings
                        ])


if __name__ == "__main__":
    unittest.main()
