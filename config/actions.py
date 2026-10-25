"""ローカル Ollama 上の Qwen3Guard を NeMo の入力レールへ接続する。"""

import re
from typing import Optional

import httpx
from nemoguardrails import RailsConfig
from nemoguardrails.actions import action
from nemoguardrails.actions.rail_outcome import RailOutcome


@action(is_system_action=True)
async def qwen_guard_check_input(
    context: Optional[dict] = None,
    config: Optional[RailsConfig] = None,
    debug_events: Optional[list[dict[str, str]]] = None,
):
    user_message = (context or {}).get("user_message", "")
    if not user_message:
        return RailOutcome.allow()

    settings = config.custom_data["qwen_guard"]
    async with httpx.AsyncClient(timeout=120, trust_env=False) as client:
        response = await client.post(
            settings["endpoint"],
            json={
                "model": settings["model"],
                "messages": [{"role": "user", "content": user_message}],
                "stream": False,
                "options": {"temperature": 0, "num_predict": 64},
            },
        )
        response.raise_for_status()

    content = response.json()["message"]["content"]
    match = re.search(r"(?m)^Safety:\s*(Safe|Unsafe|Controversial)\s*$", content)
    label = match.group(1) if match else "不明"
    if debug_events is not None:
        debug_events.append({"label": label, "raw": content})
    if not match:
        raise RuntimeError(f"Qwen3Guard の判定を読み取れません: {content!r}")
    if label in settings["block_labels"]:
        return RailOutcome.block(reason=f"Qwen3Guard: {label}")
    return RailOutcome.allow()
