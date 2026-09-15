import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.ai_provider import get_first_configured_api_key, normalize_api_key


def test_normalize_api_key_rejects_placeholder_values():
    assert normalize_api_key(None) is None
    assert normalize_api_key("   ") is None
    assert normalize_api_key("sk-or-v1-YOUR_OPENROUTER_API_KEY_HERE") is None
    assert normalize_api_key("YOUR_FREEMODEL_API_KEY") is None
    assert normalize_api_key("placeholder") is None
    assert normalize_api_key("valid-token") == "valid-token"


def test_get_first_configured_api_key_uses_first_valid_value():
    env = {
        "OPENROUTER_API_KEY": "   ",
        "FREEMODEL_API_KEY": "valid-token",
    }

    assert get_first_configured_api_key(
        ["OPENROUTER_API_KEY", "FREEMODEL_API_KEY"],
        env=env,
    ) == "valid-token"
