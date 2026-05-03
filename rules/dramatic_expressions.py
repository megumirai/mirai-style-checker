"""ルール: ドラマチック表現の検出"""

NAME = "dramatic_expressions"
DESCRIPTION = "ドラマチック表現の検出（部分一致）"
DEFAULT_WORDS = ["圧倒的", "驚愕", "衝撃", "劇的", "鮮烈", "絶望的", "絶対的"]


def check(text: str, words: list = None) -> dict:
    """
    テキスト中にドラマチック表現が含まれていないかチェック。
    """
    if words is None:
        words = DEFAULT_WORDS
    
    found = []
    for word in words:
        if word in text:
            positions = []
            start = 0
            while True:
                pos = text.find(word, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            found.append({"word": word, "positions": positions})
    
    passed = len(found) == 0
    
    return {
        "rule": NAME,
        "passed": passed,
        "found_words": found,
        "checked_words": words,
        "message": (
            "OK: ドラマチック表現は見つかりませんでした。"
            if passed else
            f"NG: ドラマチック表現を {len(found)} 種類検出しました。"
        ),
    }