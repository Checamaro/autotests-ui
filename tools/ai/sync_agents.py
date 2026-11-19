"""
Собирает конфиги ИИ-инструментов из единого источника в папке ai/.

Источник (правим руками):
    ai/config.toml      провайдер, модели по ролям, имя переменной с ключом
    ai/agents.toml      роли, команды, права, MCP-серверы
    ai/prompts/         тексты ролей и команд
    AGENTS.md           правила проекта

Результат (генерируется, руками не правим):
    OpenCode:     opencode.json, .opencode/agents/*.md, .opencode/commands/*.md
    Claude Code:  .mcp.json, .claude/settings.json, .claude/agents/*.md, .claude/skills/*/SKILL.md

Использование:
    python tools/ai/sync_agents.py            пересобрать
    python tools/ai/sync_agents.py --check    проверить, что сгенерированное актуально (для CI)

Только стандартная библиотека Python 3.11+.
"""
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTICE = "<!-- Сгенерировано tools/ai/sync_agents.py из ai/. Не редактируйте вручную. -->"

# Инструменты Claude Code: базовые + запись, если роли разрешено редактировать
CLAUDE_READ_TOOLS = ["Read", "Glob", "Grep", "Bash"]
CLAUDE_EDIT_TOOLS = ["Write", "Edit"]


def load_toml(relative: str) -> dict:
    with open(ROOT / relative, "rb") as file:
        return tomllib.load(file)


def read_prompt(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").strip() + "\n"


def model_for(config: dict, role: str) -> str:
    return config["models"].get("roles", {}).get(role, config["models"]["default"])


def yaml_str(value: str) -> str:
    # JSON-строка — корректная строка YAML: экранирует кавычки и двоеточия
    return json.dumps(value, ensure_ascii=False)


# ---------------------------------------------------------------- OpenCode

def opencode_bash_permissions(permissions: dict) -> dict:
    # В OpenCode побеждает последнее совпавшее правило: сначала "*", затем частные правила
    rules = {"*": "ask"}
    for level in ("allow", "ask", "deny"):
        for prefix in permissions.get(level, []):
            rules[f"{prefix}*"] = level
    return rules


def build_opencode(config: dict, agents: dict) -> dict[str, str]:
    provider = config["provider"]
    prefix = config.get("mcp", {}).get("command_prefix", [])
    used_models = sorted({config["models"]["default"], *config["models"].get("roles", {}).values()})

    opencode_config = {
        "$schema": "https://opencode.ai/config.json",
        "provider": {
            provider["id"]: {
                "npm": "@ai-sdk/openai-compatible",
                "name": provider["name"],
                "options": {
                    "baseURL": provider["base_url"],
                    "apiKey": "{env:" + provider["api_key_env"] + "}",
                },
                "models": {model: {"name": model} for model in used_models},
            }
        },
        "model": f"{provider['id']}/{config['models']['default']}",
        "instructions": ["AGENTS.md"],
        "mcp": {
            name: {
                "type": "local",
                "command": [*prefix, *server["command"]],
                "enabled": True,
                **({"environment": {k: "{env:" + v + "}" for k, v in server["env"].items()}}
                   if server.get("env") else {}),
            }
            for name, server in agents["mcp"].items()
        },
        "permission": {
            "edit": "ask",
            "bash": opencode_bash_permissions(agents["permissions"]),
        },
    }
    files = {"opencode.json": json.dumps(opencode_config, ensure_ascii=False, indent=2) + "\n"}

    bash_rules = opencode_bash_permissions(agents["permissions"])
    for agent in agents["agents"]:
        lines = [
            "---",
            f"description: {yaml_str(agent['description'])}",
            "mode: subagent",
            f"model: {yaml_str(provider['id'] + '/' + model_for(config, agent['name']))}",
            "permission:",
            f"  edit: {'ask' if agent.get('edit') else 'deny'}",
            "  bash:",
            *[f"    {yaml_str(pattern)}: {level}" for pattern, level in bash_rules.items()],
            "---",
            NOTICE,
            "",
            read_prompt(agent["prompt"]),
        ]
        files[f".opencode/agents/{agent['name']}.md"] = "\n".join(lines)

    for command in agents["commands"]:
        lines = [
            "---",
            f"description: {yaml_str(command['description'])}",
            "---",
            NOTICE,
            "",
            read_prompt(command["prompt"]),
        ]
        files[f".opencode/commands/{command['name']}.md"] = "\n".join(lines)
    return files


# ------------------------------------------------------------- Claude Code

def build_claude(config: dict, agents: dict) -> dict[str, str]:
    prefix = config.get("mcp", {}).get("command_prefix", [])
    mcp_config = {
        "mcpServers": {
            name: {
                "command": [*prefix, *server["command"]][0],
                "args": [*prefix, *server["command"]][1:],
                **({"env": {k: "${" + v + "}" for k, v in server["env"].items()}}
                   if server.get("env") else {}),
            }
            for name, server in agents["mcp"].items()
        }
    }
    permissions = agents["permissions"]
    settings = {
        "permissions": {
            level: [f"Bash({prefix_cmd}:*)" for prefix_cmd in permissions.get(level, [])]
            for level in ("allow", "ask", "deny")
        }
    }
    settings["permissions"]["allow"] += [
        f"mcp__playwright__{tool}" for tool in
        ("browser_navigate", "browser_snapshot", "browser_take_screenshot", "browser_click",
         "browser_type", "browser_navigate_back", "browser_close")
    ]
    settings["permissions"]["ask"].append("Edit(.env)")

    files = {
        ".mcp.json": json.dumps(mcp_config, ensure_ascii=False, indent=2) + "\n",
        ".claude/settings.json": json.dumps(settings, ensure_ascii=False, indent=2) + "\n",
    }
    for agent in agents["agents"]:
        tools = CLAUDE_READ_TOOLS + (CLAUDE_EDIT_TOOLS if agent.get("edit") else [])
        tools += [f"mcp__{name}" for name in agent.get("mcp", [])]
        lines = [
            "---",
            f"name: {agent['name']}",
            f"description: {yaml_str(agent['description'])}",
            f"tools: {', '.join(tools)}",
            # Псевдоним; конкретная модель задаётся в Claude Code (подписка или ANTHROPIC_DEFAULT_SONNET_MODEL)
            "model: sonnet",
            "---",
            NOTICE,
            "",
            read_prompt(agent["prompt"]),
        ]
        files[f".claude/agents/{agent['name']}.md"] = "\n".join(lines)

    for command in agents["commands"]:
        lines = [
            "---",
            f"name: {command['name']}",
            f"description: {yaml_str(command['description'])}",
            "---",
            NOTICE,
            "",
            read_prompt(command["prompt"]),
        ]
        files[f".claude/skills/{command['name']}/SKILL.md"] = "\n".join(lines)
    return files


def main() -> None:
    check_only = "--check" in sys.argv
    config = load_toml("ai/config.toml")
    agents = load_toml("ai/agents.toml")
    files = {**build_opencode(config, agents), **build_claude(config, agents)}

    outdated = []
    for relative, content in files.items():
        path = ROOT / relative
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == content:
            continue
        outdated.append(relative)
        if not check_only:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")

    if check_only and outdated:
        print("Сгенерированные файлы устарели. Запустите: python tools/ai/sync_agents.py")
        print("\n".join(f"  - {name}" for name in outdated))
        sys.exit(1)
    action = "Проверено" if check_only else "Обновлено"
    print(f"{action}: {len(outdated) if not check_only else len(files)} файл(ов)")
    for name in outdated:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
