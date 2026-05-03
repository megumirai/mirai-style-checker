"""
mirai-style-checker MCP server
日本語文章のスタイルルールをチェックする
"""

import yaml
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from rules import (
    teki_overuse,
    forbidden_phrases,
    bracket_overuse,
    dramatic_expressions,
)

mcp = FastMCP("mirai-style-checker")

# rules.yaml を読み込んで設定として保持
CONFIG_PATH = Path(__file__).parent / "rules.yaml"
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        RULES_CONFIG = yaml.safe_load(f) or {}
else:
    RULES_CONFIG = {}

# 全ルールのレジストリ（モジュール参照を一覧化）
RULES = {
    teki_overuse.NAME: teki_overuse,
    forbidden_phrases.NAME: forbidden_phrases,
    bracket_overuse.NAME: bracket_overuse,
    dramatic_expressions.NAME: dramatic_expressions,
}


def _run_rule(rule_module, text: str) -> dict:
    """指定ルールに対応する設定をrules.yamlから取り出して check() を呼ぶ"""
    config = RULES_CONFIG.get(rule_module.NAME, {})
    
    # ルールごとに引数の渡し方が違う
    if rule_module.NAME in ("teki_overuse", "bracket_overuse"):
        threshold = config.get("threshold", rule_module.DEFAULT_THRESHOLD)
        return rule_module.check(text, threshold=threshold)
    elif rule_module.NAME == "forbidden_phrases":
        phrases = config.get("list", rule_module.DEFAULT_PHRASES)
        return rule_module.check(text, phrases=phrases)
    elif rule_module.NAME == "dramatic_expressions":
        words = config.get("list", rule_module.DEFAULT_WORDS)
        return rule_module.check(text, words=words)
    else:
        return rule_module.check(text)


@mcp.tool()
def check_all_rules(text: str) -> dict:
    """
    Run all configured Japanese writing-style rules against a text 
    and return a structured list of violations.

    Use this when the user asks to validate or proofread a Japanese 
    article against multiple style rules at once. 
    Returns each violation with rule name, severity, and details. 
    Does NOT modify the text. 
    For checking a single rule only, use check_specific_rule instead.

    Args:
        text: The Japanese text to check
    """
    if not text:
        return {
            "isError": True,
            "error_code": "invalid_input",
            "error": "text parameter is required and cannot be empty",
        }

    violations = []
    for rule_name, rule_module in RULES.items():
        result = _run_rule(rule_module, text)
        if not result["passed"]:
            violations.append(result)

    return {
        "passed": len(violations) == 0,
        "rule_count": len(RULES),
        "violations_count": len(violations),
        "violations": violations,
    }


@mcp.tool()
def check_specific_rule(text: str, rule_name: str) -> dict:
    """
    Run a single specified Japanese writing-style rule against a text.

    Use this when the user explicitly asks about ONE specific rule 
    (e.g., 'check only for overuse of 的'). Requires rule_name parameter. 
    For checking all rules at once, use check_all_rules instead.

    Args:
        text: The Japanese text to check
        rule_name: The rule identifier (e.g., 'teki_overuse', 'forbidden_phrases', 
                   'bracket_overuse', 'dramatic_expressions')
    """
    if not text:
        return {
            "isError": True,
            "error_code": "invalid_input",
            "error": "text parameter is required and cannot be empty",
        }

    if rule_name not in RULES:
        return {
            "isError": True,
            "error_code": "unknown_rule",
            "error": f"rule '{rule_name}' is not defined. Available: {list(RULES.keys())}",
        }

    return _run_rule(RULES[rule_name], text)


@mcp.tool()
def list_rules() -> dict:
    """
    List all available Japanese writing-style rules supported by this checker, 
    with their identifiers, descriptions, and configurability.

    Use this when the user asks 'what rules can you check?' or before calling 
    check_specific_rule to find the right rule_name.
    """
    return {
        "rules": [
            {
                "name": rule_module.NAME,
                "description": rule_module.DESCRIPTION,
            }
            for rule_module in RULES.values()
        ],
        "count": len(RULES),
    }


if __name__ == "__main__":
    mcp.run()