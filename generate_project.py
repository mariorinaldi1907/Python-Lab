"""
Python Lab — Project Generator
Generates real, runnable Python scripts that read like genuine developer work.
Commits sound personal, not auto-generated.
"""

import anthropic
import os
import random
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
COMMIT_PROBABILITY = 0.70   # Change to 1.0 to force a commit, 0.70 for natural cadence
PROJECTS_PER_RUN   = random.choice([1, 1, 1, 2, 2, 3])
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_CATEGORIES = [
    "a data structures implementation (e.g. trie, AVL tree, LRU cache, bloom filter, skip list)",
    "an algorithm (e.g. Dijkstra, A*, KMP string search, topological sort, Floyd-Warshall)",
    "a math/number theory utility (e.g. sieve of Eratosthenes, fast exponentiation, matrix ops)",
    "a text processing tool (e.g. tokenizer, Markov chain generator, diff algorithm)",
    "a mini simulation (e.g. Conway's Game of Life, random walk, bouncing balls, epidemic model)",
    "a statistics/probability module (e.g. bootstrapping, chi-square test, Bayesian updater)",
    "a design pattern implementation (e.g. observer, strategy, command, decorator with real use case)",
    "a puzzle or game solver (e.g. Sudoku, N-Queens, maze generator, word ladder BFS)",
    "a functional programming utility (e.g. lazy evaluation, memoization, currying, pipelines)",
    "a file or data parser (e.g. CSV analyzer, log parser, config reader, JSON schema validator)",
    "a mini interpreter or expression evaluator (e.g. RPN calculator, simple expression parser)",
    "a graph algorithm (e.g. cycle detection, shortest path variants, minimum spanning tree)",
    "a compression or encoding utility (e.g. run-length encoding, Huffman coding, base-N encoder)",
    "a geometry or spatial utility (e.g. convex hull, point-in-polygon, rectangle packing)",
    "a concurrency pattern demo using threading or asyncio (e.g. producer-consumer, rate limiter)",
    "a machine learning concept from scratch (e.g. linear regression, k-means, decision tree, naive bayes)",
    "a network/socket utility (e.g. simple HTTP server, port scanner, ping tool using stdlib)",
    "a CLI tool with argparse (e.g. file deduplicator, directory tree printer, word frequency counter)",
]

SYSTEM_PROMPT = """You are Mario, a developer writing Python scripts for your personal GitHub.
Write code that sounds personal and genuine — like something you actually sat down and built.
Use clear variable names, and write comments that explain *why* decisions were made, not just what the code does.
The commit messages and descriptions should sound like a real developer's voice, casual but technical."""


def should_run() -> bool:
    roll = random.random()
    print(f"[lab] Roll: {roll:.2f} (threshold: {COMMIT_PROBABILITY})")
    return roll < COMMIT_PROBABILITY


def generate_project(client: anthropic.Anthropic, category: str) -> str:
    prompt = f"""Write a complete Python script implementing {category}.

Requirements:
- 60–180 lines (excluding blanks/comments)
- Standard library ONLY — no pip installs
- Every function/class has a docstring
- Includes `if __name__ == "__main__":` with a real working demo that prints output
- Must be syntactically correct and run cleanly

Respond in EXACTLY this format (nothing before or after):

FILENAME: <descriptive_snake_case_name>
COMMIT_MESSAGE: <first-person, casual-technical commit message, e.g. "implemented Dijkstra with a min-heap, handles disconnected graphs too">
DESCRIPTION: <one sentence in first person, e.g. "Built a Bloom filter to explore probabilistic data structures — tunable false positive rate">
CODE:
<complete python source>"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def parse_response(response: str) -> tuple[str, str, str, str]:
    filename = commit_message = description = ""
    code_lines = []
    in_code = False

    for line in response.strip().split("\n"):
        if line.startswith("FILENAME:"):
            filename = line.split(":", 1)[1].strip()
        elif line.startswith("COMMIT_MESSAGE:"):
            commit_message = line.split(":", 1)[1].strip()
        elif line.startswith("DESCRIPTION:"):
            description = line.split(":", 1)[1].strip()
        elif line.startswith("CODE:"):
            in_code = True
        elif in_code:
            code_lines.append(line)

    code = "\n".join(code_lines).strip()
    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:])
    if code.endswith("```"):
        code = "\n".join(code.split("\n")[:-1])

    return filename, commit_message, description, code.strip()


def run_script(filepath: Path) -> tuple[str, bool]:
    try:
        result = subprocess.run(
            ["python", str(filepath)],
            capture_output=True, text=True, timeout=20,
        )
        return (result.stdout + result.stderr)[:600], result.returncode == 0
    except subprocess.TimeoutExpired:
        return "Timed out", False
    except Exception as e:
        return str(e), False


def update_readme(entries: list[dict]) -> None:
    readme = Path("README.md")

    # Bootstrap README if missing
    if not readme.exists():
        readme.write_text(
            "# Mario's Python Lab 🔬\n\n"
            "A collection of Python projects I've been building — spanning algorithms, "
            "data structures, simulations, and systems-level tools.\n\n"
            "> Mostly written in vanilla Python (stdlib only).\n\n"
            "---\n\n"
            "## Projects\n\n"
            "| Date | Project | What I built & why |\n"
            "|------|---------|-------------------|\n"
        )

    content = readme.read_text()
    TABLE_HEADER = "| Date | Project | What I built & why |\n|------|---------|-------------------|\n"

    new_rows = ""
    for e in entries:
        date = datetime.now().strftime("%Y-%m-%d")
        name = e["filename"].replace(".py", "").replace("_", " ").title()
        new_rows += f"| {date} | [{name}](projects/{e['filename']}) | {e['description']} |\n"

    if TABLE_HEADER in content:
        # Insert new rows right after the header (at the top of the table)
        content = content.replace(TABLE_HEADER, TABLE_HEADER + new_rows)
    else:
        # Table header missing — append a fresh one
        content = content.rstrip() + f"\n\n## Projects\n\n{TABLE_HEADER}{new_rows}"

    readme.write_text(content)


def main() -> None:
    if not should_run():
        print("[lab] Skipping this slot — keeping the graph looking natural.")
        Path(".commit_message").write_text("")
        sys.exit(0)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[lab] ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    projects_dir = Path("projects")
    projects_dir.mkdir(exist_ok=True)

    generated      = []
    commit_messages = []
    categories     = random.sample(PROJECT_CATEGORIES, PROJECTS_PER_RUN)

    for i, category in enumerate(categories, 1):
        print(f"\n[lab] Generating {i}/{PROJECTS_PER_RUN}: {category[:60]}...")
        try:
            response                              = generate_project(client, category)
            filename, commit_msg, description, code = parse_response(response)

            if not filename or not code:
                print("[lab] Parse failed, skipping.")
                continue

            timestamp     = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{filename}_{timestamp}.py"
            filepath      = projects_dir / safe_filename

            header = f'"""\nDate: {datetime.now().strftime("%Y-%m-%d")}\n{description}\n"""\n\n'
            filepath.write_text(header + code)

            output, success = run_script(filepath)
            print(f"[lab] {'✓ ran ok' if success else '⚠ had errors'}")
            print(f"[lab] Output: {output[:200]}")

            generated.append({"filename": safe_filename, "description": description})
            commit_messages.append(commit_msg)

        except Exception as e:
            print(f"[lab] Error: {e}")
            continue

    if not generated:
        print("[lab] Nothing generated.")
        Path(".commit_message").write_text("")
        sys.exit(0)

    update_readme(generated)

    if len(commit_messages) == 1:
        final_msg = commit_messages[0]
    else:
        items     = "\n".join(f"- {m}" for m in commit_messages)
        final_msg = f"added {len(commit_messages)} new scripts\n\n{items}"

    Path(".commit_message").write_text(final_msg)
    print(f"\n[lab] Done — committing {len(generated)} project(s).")
    print(f"[lab] Message: {final_msg}")


if __name__ == "__main__":
    main()
