import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from django.core.management import BaseCommand, CommandError, call_command


GITHUB_API_BASE = "https://api.github.com"
DEFAULT_FILES = [
    "README.md",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "go.mod",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
]

JS_TECH = {
    "react": "React",
    "next": "Next.js",
    "vue": "Vue",
    "svelte": "Svelte",
    "angular": "Angular",
    "express": "Express",
    "nestjs": "NestJS",
    "fastify": "Fastify",
    "vite": "Vite",
    "tailwindcss": "Tailwind CSS",
    "typescript": "TypeScript",
}

PY_TECH = {
    "django": "Django",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "scikit-learn",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "langchain": "LangChain",
    "openai": "OpenAI API",
    "pgvector": "pgvector",
}


def github_get(url: str, token: str | None) -> Any | None:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def fetch_text(url: str, token: str | None) -> str | None:
    if not url:
        return None
    headers = {"Accept": "application/vnd.github.raw"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    with urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="replace")


def list_repos(username: str, token: str | None) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        url = (
            f"{GITHUB_API_BASE}/users/{username}/repos"
            f"?per_page=100&page={page}&sort=updated"
        )
        data = github_get(url, token)
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos


def get_repo_file(owner: str, repo: str, path: str, token: str | None) -> str | None:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    data = github_get(url, token)
    if not data or data.get("type") != "file":
        return None
    return fetch_text(data.get("download_url"), token)


def list_workflows(owner: str, repo: str, token: str | None) -> list[tuple[str, str]]:
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/.github/workflows"
    data = github_get(url, token)
    if not data:
        return []
    workflows = []
    for item in data:
        if item.get("type") != "file":
            continue
        name = item.get("name", "")
        if name.endswith((".yml", ".yaml")):
            workflows.append((name, item.get("download_url", "")))
    return workflows


def extract_package_json(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def extract_python_deps(text: str) -> set[str]:
    deps = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = re.split(r"[<=>\\[]", line, maxsplit=1)[0]
        if name:
            deps.add(name.lower())
    return deps


def extract_pyproject_deps(text: str) -> set[str]:
    lowered = text.lower()
    deps = set()
    for dep in PY_TECH:
        if re.search(rf"\\b{re.escape(dep)}\\b", lowered):
            deps.add(dep)
    return deps


def detect_stack(
    files: dict[str, str],
    workflows: Iterable[str],
    primary_language: str | None,
) -> tuple[list[str], list[str]]:
    tech: set[str] = set()
    evidence: list[str] = []

    if primary_language:
        tech.add(primary_language)
        evidence.append(f"primary language: {primary_language}")

    if "package.json" in files:
        tech.add("Node.js")
        evidence.append("package.json")
        pkg = extract_package_json(files["package.json"])
        deps = {}
        deps.update(pkg.get("dependencies", {}) or {})
        deps.update(pkg.get("devDependencies", {}) or {})
        for name in deps:
            key = name.lower()
            if key in JS_TECH:
                tech.add(JS_TECH[key])
                evidence.append(f"package.json: {name}")

    if "requirements.txt" in files:
        tech.add("Python")
        evidence.append("requirements.txt")
        for dep in extract_python_deps(files["requirements.txt"]):
            if dep in PY_TECH:
                tech.add(PY_TECH[dep])
                evidence.append(f"requirements.txt: {dep}")

    if "pyproject.toml" in files:
        tech.add("Python")
        evidence.append("pyproject.toml")
        for dep in extract_pyproject_deps(files["pyproject.toml"]):
            tech.add(PY_TECH[dep])
            evidence.append(f"pyproject.toml: {dep}")

    if "go.mod" in files:
        tech.add("Go")
        evidence.append("go.mod")

    if "Dockerfile" in files:
        tech.add("Docker")
        evidence.append("Dockerfile")

    if "docker-compose.yml" in files or "docker-compose.yaml" in files:
        tech.add("Docker Compose")
        evidence.append("docker-compose.yml")

    if workflows:
        tech.add("GitHub Actions")
        evidence.append(".github/workflows")

    return sorted(tech), evidence


def format_section_list(values: Iterable[str]) -> str:
    if not values:
        return "- (none)\n"
    return "\n".join(f"- {value}" for value in values) + "\n"


class Command(BaseCommand):
    help = "Generate a GitHub skills summary from public repositories."

    def add_arguments(self, parser):
        parser.add_argument("username", nargs="?", default=None, help="GitHub username.")
        parser.add_argument(
            "--output",
            default="docs/githubsummary.md",
            help="Output markdown path.",
        )
        parser.add_argument(
            "--include-forks",
            action="store_true",
            help="Include forked repositories.",
        )
        parser.add_argument(
            "--include-archived",
            action="store_true",
            help="Include archived repositories.",
        )
        parser.add_argument(
            "--ingest",
            action="store_true",
            help="Ingest the generated summary into the vector store.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing chunks before ingesting.",
        )

    def handle(self, *args, **options):
        username = options["username"] or os.environ.get("GITHUB_USERNAME")
        if not username:
            raise CommandError("Provide a username or set GITHUB_USERNAME in .env")

        token = os.environ.get("GITHUB_TOKEN")

        repos = list_repos(username, token)
        if not options["include_forks"]:
            repos = [r for r in repos if not r.get("fork")]
        if not options["include_archived"]:
            repos = [r for r in repos if not r.get("archived")]

        summary_lines = []
        summary_lines.append(f"# GitHub Skills Summary: {username}\n")
        summary_lines.append(
            f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        )
        summary_lines.append(
            f"Total repos analyzed: {len(repos)} (forks={'yes' if options['include_forks'] else 'no'}, "
            f"archived={'yes' if options['include_archived'] else 'no'})\n"
        )
        summary_lines.append(
            "Overview: Public repositories for this account, summarized by detected languages, "
            "frameworks, and tooling from key project files.\n"
        )

        all_tech: set[str] = set()
        all_languages: set[str] = set()

        summary_lines.append("## Skills Summary\n")

        repo_sections = []

        for repo in repos:
            name = repo.get("name", "")
            owner = repo.get("owner", {}).get("login", username)
            primary_language = repo.get("language")
            if primary_language:
                all_languages.add(primary_language)

            files: dict[str, str] = {}
            for file_path in DEFAULT_FILES:
                content = get_repo_file(owner, name, file_path, token)
                if content:
                    files[file_path] = content

            workflows = []
            for wf_name, wf_url in list_workflows(owner, name, token):
                wf_text = fetch_text(wf_url, token)
                if wf_text:
                    workflows.append(wf_name)

            tech, evidence = detect_stack(files, workflows, primary_language)
            all_tech.update(tech)

            repo_section = [f"### {name}\n"]
            repo_section.append(f"- URL: {repo.get('html_url', '')}")
            if repo.get("description"):
                repo_section.append(f"- Description: {repo.get('description')}")
            if primary_language:
                repo_section.append(f"- Primary language: {primary_language}")
            repo_section.append(
                f"- Stack: {', '.join(tech) if tech else '(none detected)'}"
            )
            repo_section.append("- Evidence:")
            if evidence:
                repo_section.extend([f"  - {item}" for item in evidence])
            else:
                repo_section.append("  - (none)")

            found_files = list(files.keys())
            if workflows:
                found_files.append(".github/workflows/*")
            if found_files:
                repo_section.append(f"- Key files: {', '.join(sorted(found_files))}")

            repo_sections.append("\n".join(repo_section) + "\n")

        summary_lines.append("### Languages\n")
        summary_lines.append(format_section_list(sorted(all_languages)))
        summary_lines.append("### Technologies\n")
        summary_lines.append(format_section_list(sorted(all_tech)))
        summary_lines.append("## Repositories\n")
        summary_lines.extend(repo_sections)

        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(summary_lines).strip() + "\n", encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"Saved: {output_path}"))

        if options["ingest"]:
            call_command(
                "ingest_document",
                str(output_path),
                source="github-summary",
                clear=options["clear"],
            )
