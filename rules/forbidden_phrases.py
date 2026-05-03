"""ルール: 禁則語の検出（しましょう、してください等）"""

NAME = "forbidden_phrases"
DESCRIPTION = "禁則語句の検出（部分一致）"
DEFAULT_PHRASES = ["しましょう", "してください"]


def check(text: str, phrases: list = None) -> dict:
    """
    テキスト中に禁則語が含まれていないかチェック。
    """
    if phrases is None:
        phrases = DEFAULT_PHRASES
    
    found = []
    for phrase in phrases:
        if phrase in text:
            # 出現位置を記録
            positions = []
            start = 0
            while True:
                pos = text.find(phrase, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            found.append({"phrase": phrase, "positions": positions})
    
    passed = len(found) == 0
    
    return {
        "rule": NAME,
        "passed": passed,
        "found_phrases": found,
        "checked_phrases": phrases,
        "message": (
            "OK: 禁則語は見つかりませんでした。"
            if passed else
            f"NG: 禁則語を {len(found)} 種類検出しました。"
        ),
    }