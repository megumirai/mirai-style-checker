"""ルール: 「的」の多用を検出"""

NAME = "teki_overuse"
DESCRIPTION = "「的」の多用を検出"
DEFAULT_THRESHOLD = 3


def check(text: str, threshold: int = DEFAULT_THRESHOLD) -> dict:
    """
    テキスト中の「的」の出現回数を数え、閾値を超えたら違反として返す。
    """
    count = text.count("的")
    passed = count <= threshold
    
    return {
        "rule": NAME,
        "passed": passed,
        "count": count,
        "limit": threshold,
        "message": (
            f"OK: 「的」の使用は {count} 回で制限内です。"
            if passed else
            f"NG: 「的」が {count} 回使われています（上限 {threshold} 回）。"
        ),
    }