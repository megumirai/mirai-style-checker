"""ルール: 鍵カッコの多用を検出（強調カッコのみ・段落密度方式）

writing-style.md の対象は「過剰な括弧」＝語の強調（「疑惑」「主張」等）。
証言・声明・作品名などの引用（中身が長い「…」）は正当な用法として数えない。
- 中身が emphasis_max_chars 以下の「…」を強調カッコとみなす
- 段落ごとに数え、per_paragraph_limit を超えたら違反
"""

import re

NAME = "bracket_overuse"
DESCRIPTION = "強調用の鍵カッコの多用を検出（段落ごと。長い引用は除外）"

DEFAULT_PER_PARAGRAPH_LIMIT = 2
DEFAULT_EMPHASIS_MAX_CHARS = 8

_QUOTED = re.compile(r"「([^」]*)」")


def check(
    text: str,
    per_paragraph_limit: int = DEFAULT_PER_PARAGRAPH_LIMIT,
    emphasis_max_chars: int = DEFAULT_EMPHASIS_MAX_CHARS,
) -> dict:
    """
    段落（空行区切り）ごとに強調カッコ（中身が短い「…」）を数え、
    per_paragraph_limit を超える段落があれば違反として返す。
    """
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    violations = []
    total_emphasis = 0
    total_all = 0

    for i, para in enumerate(paragraphs, start=1):
        contents = _QUOTED.findall(para)
        total_all += len(contents)
        emphasis = [c for c in contents if len(c) <= emphasis_max_chars]
        total_emphasis += len(emphasis)
        if len(emphasis) > per_paragraph_limit:
            excerpt = para.strip().replace("\n", " ")[:40]
            violations.append(
                {"paragraph": i, "count": len(emphasis), "examples": emphasis[:5], "excerpt": excerpt}
            )

    passed = len(violations) == 0
    return {
        "rule": NAME,
        "passed": passed,
        "count": total_emphasis,
        "count_all_brackets": total_all,
        "limit": per_paragraph_limit,
        "violating_paragraphs": violations,
        "message": (
            f"OK: 強調カッコは全段落で {per_paragraph_limit} 個以内です（強調 {total_emphasis}／全体 {total_all}）。"
            if passed else
            f"NG: 強調カッコが段落あたり上限 {per_paragraph_limit} 個を超える段落が {len(violations)} 箇所あります。"
        ),
    }
