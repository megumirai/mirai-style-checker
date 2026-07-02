"""ルール: 「的」の多用を検出（段落密度方式）

writing-style.md の原意「1段落に複数回は避ける」に合わせ、
文書全体の絶対数ではなく段落ごとの出現数で判定する。
- 引用（「…」内）は文体の対象外なので既定で除外
- 固定語（法的・性的・目的など、置換不能な熟語）は例外リストで除外
"""

import re

NAME = "teki_overuse"
DESCRIPTION = "「的」の多用を検出（段落ごと。引用・固定語は除外）"

DEFAULT_PER_PARAGRAPH_LIMIT = 2
DEFAULT_EXCLUDE_QUOTED = True
DEFAULT_EXCEPTIONS = ["目的", "標的", "的中", "法的", "性的", "公的", "私的"]

_QUOTED = re.compile(r"「[^」]*」")


def check(
    text: str,
    per_paragraph_limit: int = DEFAULT_PER_PARAGRAPH_LIMIT,
    exclude_quoted: bool = DEFAULT_EXCLUDE_QUOTED,
    exceptions: list | None = None,
) -> dict:
    """
    段落（空行区切り）ごとに「的」の出現数を数え、
    per_paragraph_limit を超える段落があれば違反として返す。
    """
    if exceptions is None:
        exceptions = DEFAULT_EXCEPTIONS

    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    violations = []
    total = 0

    for i, para in enumerate(paragraphs, start=1):
        target = _QUOTED.sub("", para) if exclude_quoted else para
        for word in sorted(exceptions, key=len, reverse=True):
            target = target.replace(word, "")
        count = target.count("的")
        total += count
        if count > per_paragraph_limit:
            excerpt = para.strip().replace("\n", " ")[:40]
            violations.append({"paragraph": i, "count": count, "excerpt": excerpt})

    passed = len(violations) == 0
    return {
        "rule": NAME,
        "passed": passed,
        "count": total,
        "limit": per_paragraph_limit,
        "violating_paragraphs": violations,
        "message": (
            f"OK: 全段落で「的」は段落あたり {per_paragraph_limit} 回以内です（引用・固定語除く総数 {total}）。"
            if passed else
            f"NG: 「的」が段落あたり上限 {per_paragraph_limit} 回を超える段落が {len(violations)} 箇所あります。"
        ),
    }
