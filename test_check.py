"""
mirai-style-checker のテスト
- 各ルールの単体テスト
- 3ツール構成（check_all_rules / check_specific_rule / list_rules）のテスト
"""

# ===== 各ルールの単体テスト =====
from rules import teki_overuse, forbidden_phrases, bracket_overuse, dramatic_expressions

# teki_overuse 単体テスト（1段落に4回 > 上限2 → 違反）
r = teki_overuse.check("基本的かつ効率的かつ革新的かつ技術的。")
print("teki_overuse:", r)
assert r["passed"] is False
assert r["count"] == 4

# teki_overuse: 引用内は数えない
r = teki_overuse.check("彼は「戦略的で本質的な計画」と述べた。")
print("teki_overuse (quoted):", r)
assert r["passed"] is True
assert r["count"] == 0

# teki_overuse: 固定語（法的・目的等）は数えない
r = teki_overuse.check("法的な手続きの目的を確認する。")
print("teki_overuse (exceptions):", r)
assert r["passed"] is True
assert r["count"] == 0

# teki_overuse: 段落が分かれていれば各2回まで許容
r = teki_overuse.check("基本的かつ効率的。\n\n革新的かつ技術的。")
print("teki_overuse (two paragraphs):", r)
assert r["passed"] is True
assert r["count"] == 4

# forbidden_phrases テスト
r = forbidden_phrases.check("確認してください。お願いしましょう。")
print("forbidden_phrases:", r)
assert r["passed"] is False
assert len(r["found_phrases"]) == 2

# bracket_overuse テスト（強調カッコ6個 > 上限2 → 違反）
r = bracket_overuse.check("「あ」「い」「う」「え」「お」「か」")
print("bracket_overuse:", r)
assert r["passed"] is False
assert r["count"] == 6

# bracket_overuse: 長い引用は数えない
r = bracket_overuse.check("彼は「これは長い証言の引用でありますよ」と述べた。")
print("bracket_overuse (long quote):", r)
assert r["passed"] is True
assert r["count"] == 0
assert r["count_all_brackets"] == 1

# dramatic_expressions テスト
r = dramatic_expressions.check("圧倒的な性能と衝撃の結果。")
print("dramatic_expressions:", r)
assert r["passed"] is False
assert len(r["found_words"]) == 2

# 全部OKケース
r = teki_overuse.check("普通の文章です。")
assert r["passed"] is True

r = forbidden_phrases.check("普通の文章です。")
assert r["passed"] is True

r = bracket_overuse.check("普通の文章です。")
assert r["passed"] is True

r = dramatic_expressions.check("普通の文章です。")
assert r["passed"] is True

print("\n✅ 各ルール単体テスト 全合格\n")

# ===== 3ツール構成テスト =====
print("--- 3ツール構成テスト ---\n")

from server import check_all_rules, check_specific_rule, list_rules

# list_rules テスト
r = list_rules()
print("list_rules:", r)
assert r["count"] == 4
assert {rule["name"] for rule in r["rules"]} == {
    "teki_overuse", "forbidden_phrases", "bracket_overuse", "dramatic_expressions"
}

# check_all_rules: 違反なし
r = check_all_rules("普通の文章です。何の問題もありません。")
print("check_all_rules (no violations):", r)
assert r["passed"] is True
assert r["violations_count"] == 0
assert r["rule_count"] == 4

# check_all_rules: 複数違反
r = check_all_rules("基本的かつ効率的かつ革新的かつ技術的な、圧倒的な性能で衝撃しましょう。")
print("check_all_rules (multiple violations):", r)
assert r["passed"] is False
assert r["violations_count"] >= 3

# check_specific_rule: 正常
r = check_specific_rule("基本的かつ効率的かつ革新的かつ技術的", "teki_overuse")
print("check_specific_rule (teki):", r)
assert r["passed"] is False
assert r["rule"] == "teki_overuse"

# check_specific_rule: 未知のルール名（isError期待）
r = check_specific_rule("テスト", "unknown_rule_xyz")
print("check_specific_rule (unknown rule):", r)
assert r.get("isError") is True
assert r.get("error_code") == "unknown_rule"

# check_all_rules: 空テキスト（isError期待）
r = check_all_rules("")
print("check_all_rules (empty text):", r)
assert r.get("isError") is True
assert r.get("error_code") == "invalid_input"

print("\n✅ 3ツール構成 全テスト合格")

print("\n--- rules.yaml 設定反映テスト ---\n")

# rules.yaml の設定が反映されているか確認
# rules.yamlは per_paragraph_limit=2 なので、1段落4回で違反になる
r = check_specific_rule("基本的かつ効率的かつ革新的かつ技術的", "teki_overuse")
print("teki_overuse (config from yaml):", r)
assert r["passed"] is False
assert r["limit"] == 2  # rules.yaml の値
assert r["count"] == 4

# 引用除外もyaml経由で有効
r = check_specific_rule("彼は「戦略的で本質的で理想的」と述べた。", "teki_overuse")
print("teki_overuse (yaml exclude_quoted):", r)
assert r["passed"] is True

print("\n✅ rules.yaml 反映確認")