"""ルール: 鍵カッコの多用を検出"""

NAME = "bracket_overuse"
DESCRIPTION = "「」の多用を検出"
DEFAULT_THRESHOLD = 5


def check(text: str, threshold: int = DEFAULT_THRESHOLD) -> dict:
    """
    テキスト中の「」のペア数を数え、閾値を超えたら違反として返す。
    開きカッコ「を数えることでペア数を計算する。
    """
    count = text.count("「")
    passed = count <= threshold
    
    return {
        "rule": NAME,
        "passed": passed,
        "count": count,
        "limit": threshold,
        "message": (
            f"OK: 鍵カッコは {count} ペアで制限内です。"
            if passed else
            f"NG: 鍵カッコが {count} ペア使われています（上限 {threshold} ペア）。"
        ),
    }