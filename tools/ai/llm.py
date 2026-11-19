"""
Минимальный клиент к любому OpenAI-совместимому API (Polza, OpenRouter, OpenAI, DeepSeek, Ollama и др.).

Провайдер и модели берутся из ai/config.toml, ключ — из переменной окружения,
имя которой указано в provider.api_key_env. Только стандартная библиотека.
"""
import json
import os
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class LLMError(RuntimeError):
    pass


def load_config() -> dict:
    with open(ROOT / "ai" / "config.toml", "rb") as file:
        return tomllib.load(file)


def model_for(config: dict, role: str) -> str:
    return config["models"].get("roles", {}).get(role, config["models"]["default"])


def chat(
        messages: list[dict],
        role: str,
        config: dict | None = None,
        temperature: float = 0.1,
        timeout: int = 180,
        retries: int = 2,
) -> str:
    """Отправляет диалог модели роли `role` и возвращает текст ответа."""
    config = config or load_config()
    provider = config["provider"]
    api_key = os.environ.get(provider["api_key_env"], "")
    if not api_key and "localhost" not in provider["base_url"]:
        raise LLMError(f"Не задана переменная окружения {provider['api_key_env']} с API-ключом")

    payload = {"model": model_for(config, role), "messages": messages, "temperature": temperature}
    request = urllib.request.Request(
        url=provider["base_url"].rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )

    last_error = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"] or ""
        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8", errors="replace")[:500]
            last_error = LLMError(f"HTTP {error.code} от {provider['name']}: {details}")
            if error.code < 500 and error.code != 429:
                break  # ошибка запроса или ключа — повтор не поможет
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as error:
            last_error = LLMError(f"Ошибка обращения к {provider['name']}: {error}")
        time.sleep(2 * (attempt + 1))
    raise last_error


def extract_json(text: str) -> dict:
    """Достаёт JSON-объект из ответа модели (модели любят оборачивать его в ```json ... ```)."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LLMError("В ответе модели нет JSON-объекта")
    return json.loads(text[start:end + 1])
