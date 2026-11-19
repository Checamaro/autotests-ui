"""
ИИ-разбор упавшего прогона автотестов. Работает с любым OpenAI-совместимым провайдером из ai/config.toml.

Шаги:
  1. summarize_allure.py сжимает allure-results в короткую сводку упавших тестов;
  2. модель роли ci-triage классифицирует падения: BUG / TEST / ENV / FLAKY и готовит тексты багов;
  3. для каждого бага ищется дубль в GitHub Issues: есть — комментарий, нет — новый issue (bug, ai-triage);
  4. создаётся один issue «AI-разбор прогона #N» с таблицей; отчёт пишется и в GitHub Step Summary.

Использование:
    python tools/ai/triage.py allure-results --run-url <url> --run-number <N>
    python tools/ai/triage.py allure-results --dry-run      только показать отчёт, в GitHub ничего не создавать
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import LLMError, ROOT, chat, extract_json, load_config, model_for  # noqa: E402

CATEGORIES = ("BUG", "TEST", "ENV", "FLAKY")
MAX_SUMMARY_CHARS = 60_000  # ограничение размера запроса к модели


def summarize(results_dir: str) -> dict:
    output = subprocess.run(
        [sys.executable, str(ROOT / "tools/ai/summarize_allure.py"), results_dir, "--json"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    ).stdout
    return json.loads(output)


def ask_model(summary: dict) -> dict:
    system = (ROOT / "ai/prompts/ci-triage.md").read_text(encoding="utf-8")
    rules = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    data = json.dumps(summary["failures"], ensure_ascii=False, indent=1)[:MAX_SUMMARY_CHARS]
    answer = chat(
        role="ci-triage",
        config=load_config(),
        messages=[
            {"role": "system", "content": f"{system}\n\n# AGENTS.md\n{rules}"},
            {"role": "user", "content": f"Сводка упавших тестов:\n```json\n{data}\n```"},
        ],
    )
    result = extract_json(answer)
    for item in result.get("items", []):
        if item.get("category") not in CATEGORIES:
            item["category"] = "TEST"
            item["reason"] = f"(модель вернула неизвестную категорию) {item.get('reason', '')}"
    result.setdefault("bugs", [])
    return result


def cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def render_report(result: dict, statuses: dict, run_url: str, bug_links: dict) -> str:
    counts = {c: sum(1 for i in result["items"] if i["category"] == c) for c in CATEGORIES}
    model = model_for(load_config(), "ci-triage")
    lines = [
        f"Прогон: {run_url or 'локальный'}",
        f"Статусы: " + ", ".join(f"{k}={v}" for k, v in sorted(statuses.items())),
        f"Модель: `{model}`",
        "",
        f"**Итог:** {result.get('summary', '')}",
        "",
        " | ".join(f"{c}: {n}" for c, n in counts.items()),
        "",
        "| Тест | Категория | Причина | Действие |",
        "|---|---|---|---|",
    ]
    for item in result["items"]:
        lines.append(f"| `{cell(item['test'])}` | {item['category']} | {cell(item['reason'])} | {cell(item['action'])} |")
    if bug_links:
        lines += ["", "**Баги:**"] + [f"- {title}: {link}" for title, link in bug_links.items()]
    lines += ["", "_Разбор сделан ИИ: проверьте выводы перед тем, как чинить._"]
    return "\n".join(lines)


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, encoding="utf-8").stdout.strip()


def file_bugs(bugs: list[dict], run_url: str, dry_run: bool) -> dict:
    links = {}
    for bug in bugs:
        title, body = bug["title"], bug["body"] + f"\n\n---\nНайдено ИИ-разбором прогона {run_url}"
        if dry_run:
            links[title] = "(dry-run: issue не создан)"
            continue
        found = json.loads(gh("issue", "list", "--state", "all", "--label", "bug",
                              "--search", title, "--json", "number,url", "--limit", "1") or "[]")
        if found:
            gh("issue", "comment", str(found[0]["number"]), "--body", f"Повторилось в прогоне {run_url}")
            links[title] = found[0]["url"] + " (дубль, добавлен комментарий)"
        else:
            links[title] = gh("issue", "create", "--title", title, "--body", body, "--label", "bug,ai-triage")
    return links


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results_dir")
    parser.add_argument("--run-url", default="")
    parser.add_argument("--run-number", default="local")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    summary = summarize(args.results_dir)
    if not summary["failures"]:
        print("Упавших тестов нет — разбирать нечего.")
        return

    try:
        result = ask_model(summary)
    except (LLMError, json.JSONDecodeError) as error:
        # ИИ-разбор не должен ронять пайплайн: сообщаем и выходим без ошибки
        print(f"::warning::ИИ-разбор не выполнен: {error}")
        return

    links = file_bugs(result["bugs"], args.run_url, args.dry_run)
    report = render_report(result, summary["statuses"], args.run_url, links)
    print(report)

    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as file:
            file.write("## AI-разбор прогона\n\n" + report + "\n")
    if not args.dry_run:
        print(gh("issue", "create", "--title", f"AI-разбор прогона #{args.run_number}",
                 "--body", report, "--label", "ai-triage"))


if __name__ == "__main__":
    main()
