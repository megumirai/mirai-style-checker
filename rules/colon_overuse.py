"""ルール: コロンの多用を検出（段落密度方式）

writing-style.md の禁止表現「過剰な括弧、コロン多用」のコロン側を実装。
段落ごとに半角「:」・全角「：」を数え、上限を超えたら違反。

文体の対象外として数えないもの（レビュー指摘 Issue #2 反映）:
- YAMLフロントマター（記事mdの先頭 --- ... --- ブロック）
- fenced code block（``` ... ```）
- Markdownリンク（[text](url) 全体。リンク文字列内の書名コロン等も対象外）
- 裸URL内のコロン（https://… 。全角文字で区切る）
- 時刻・比率など数字間のコロン（13:00 等）
- Markdownテーブルの整列指定行（|---:| や ---: | :--- 等）

判定単位は段落だが、箇条書きは1項目=1単位として扱う
（「- ラベル: 説明」は項目ごとに正当な慣用のため、リスト全体で合算しない）。
"""

import re

NAME = "colon_overuse"
DESCRIPTION = "コロンの多用を検出（段落ごと。箇条書きは項目ごと。URL・時刻・コード・リンク・表は除外）"

DEFAULT_PER_PARAGRAPH_LIMIT = 1

_FRONTMATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
_CODE_FENCE = re.compile(r"```.*?```", re.DOTALL)
_MD_LINK = re.compile(r"\[[^\]]*\]\([^)]*\)")
_URL = re.compile(r"https?://[^\s）」》】、。（「：]+")
_TABLE_ALIGN_ROW = re.compile(r"^(?=.*-)[|: \t\-]+$", re.MULTILINE)
_DIGIT_COLON = re.compile(r"(?<=\d)[:：](?=\d)")
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _units(text: str) -> list[str]:
    """判定単位のリストを返す: 通常段落は段落ごと、箇条書きは1項目1単位。"""
    units = []
    for para in re.split(r"\n\s*\n", text):
        if not para.strip():
            continue
        rest = []
        for line in para.splitlines():
            if _BULLET.match(line):
                units.append(line)
            elif line.strip():
                rest.append(line)
        if rest:
            units.append("\n".join(rest))
    return units


def check(text: str, per_paragraph_limit: int = DEFAULT_PER_PARAGRAPH_LIMIT) -> dict:
    """
    判定単位（段落／箇条書き項目）ごとにコロンを数え、
    per_paragraph_limit を超える単位があれば違反として返す。
    """
    target = _FRONTMATTER.sub("", text)
    target = _CODE_FENCE.sub("", target)
    target = _MD_LINK.sub("", target)
    target = _URL.sub("", target)
    target = _TABLE_ALIGN_ROW.sub("", target)
    target = _DIGIT_COLON.sub("", target)

    violations = []
    total = 0

    for i, unit in enumerate(_units(target), start=1):
        count = unit.count(":") + unit.count("：")
        total += count
        if count > per_paragraph_limit:
            excerpt = unit.strip().replace("\n", " ")[:40]
            violations.append({"paragraph": i, "count": count, "excerpt": excerpt})

    passed = len(violations) == 0
    return {
        "rule": NAME,
        "passed": passed,
        "count": total,
        "limit": per_paragraph_limit,
        "violating_paragraphs": violations,
        "message": (
            f"OK: コロンは全単位で {per_paragraph_limit} 個以内です（除外後の総数 {total}）。"
            if passed else
            f"NG: コロンが単位あたり上限 {per_paragraph_limit} 個を超える箇所が {len(violations)} 箇所あります。"
        ),
    }
