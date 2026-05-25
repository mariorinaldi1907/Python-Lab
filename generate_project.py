"""
GitHub Auto-Commit: AI-Powered Python Project Generator
Generates real, runnable Python mini-projects via Claude API
and commits them to keep your GitHub contribution graph active.
"""

import anthropic
import os
import random
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# ── Tuning knobs ─────────────────────────────────────────────────────────────
# Each scheduled trigger has this % chance of actually committing.
# Keeps the graph looking human (not every slot fires every day).
COMMIT_PROBABILITY = 0.70

# How many projects to generate per run (1–3 recommended)
PROJECTS_PER_RUN = random.choice([1, 1, 1, 2, 2, 3])  # weighted toward 1-2
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_CATEGORIES = [
    "a data structures implementation (e.g. trie, AVL tree, LRU cache, bloom filter, skip list)",
    "an algorithm (e.g. Dijkstra, A*, KMP string search, Knuth-Morris-Pratt, topological sort)",
    "a math/number theory utility (e.g. sieve of Eratosthenes, fast exponentiation, matrix ops)",
    "a text processing tool (e.g. tokenizer, Markov chain text generator, diff algorithm)",
    "a mini simulation (e.g. Conway's Game of Life, random walk, bouncing balls, epidemic model)",
    "a statistics/probability module (e.g. bootstrapping, chi-square test, Bayesian updater)",
    "a design pattern demo (e.g. observer, strategy, command, decorator with real use case)",
    "a puzzle/game solver (e.g. Sudoku, N-Queens, maze generator, word ladder)",
    "a functional programming utility (e.g. lazy evaluation, monadic pipeline, memoization)",
    "a file/data parser (e.g. CSV analyzer, log parser, config file reader, JSON validator)",
    "a mini interpreter or expression evaluator (e.g. RPN calc, simple expression parser)",
    "a graph algorithm (e.g. cycle detection, shortest path variants, minimum spanning tree)",
    "a compression/encoding utility (e.g. run-length encoding, Huffman coding, base-N)",
    "a geometry/spatial utility (e.g. convex hull, point-in-polygon, rectangle packing)",
    "a concurrency pattern demo using threading or asyncio (e.g. producer-consumer, rate limiter)",
]

SYSTEM_PROMPT = """You are a senior Python developer writing clean, idiomatic code.
Generate real, working Python scripts that look like genuine developer work.
Code should be well-structured, well-commented, and demonstrate good engineering practices."""


def should_run() -> bool:
    """Randomly decide whether to commit this run."""
    roll = random.random()
    print(f"[autocommit] Commit roll: {roll:.2f} (threshold: {COMMIT_PROBABILITY})")
    return roll < COMMIT_PROBABILITY


def generate_project(client: anthropic.Anthropic, category: str) -> str:
    """Call Claude API to generate a Python project."""
    prompt = f"""Write a complete Python script implementing {category}.

Hard requirements:
- 60–180 lines of code (excluding blank lines and comments)
- Uses ONLY the Python standard library (no pip installs)
- Every function/class has a docstring
- Includes a `if __name__ == "__main__":` block that runs a real demo
- The demo prints meaningful output to stdout
- Code must be syntactically correct and runnable as-is

Respond in EXACTLY this format (no extra text before or after):

FILENAME: <descriptive_snake_case_name>
COMMIT_MESSAGE: <conventional commit, e.g. "feat: implement LRU cache with O(1) operations">
DESCRIPTION: <one sentence, what it does and why it's interesting>
CODE:
<complete python source code here>"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def parse_response(response: str) -> tuple[str, str, str, str]:
    """Parse structured response into components."""
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
    # Strip markdown fences if Claude wrapped it
    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:])
    if code.endswith("```"):
        code = "\n".join(code.split("\n")[:-1])

    return filename, commit_message, description, code.strip()


def run_script(filepath: Path) -> tuple[str, bool]:
    """Run the generated script and return (output, success)."""
    try:
        result = subprocess.run(
            ["python", str(filepath)],
            capture_output=True,
            text=True,
            timeout=20,
        )
        success = result.returncode == 0
        output = (result.stdout + result.stderr)[:600]
        return output, success
    except subprocess.TimeoutExpired:
        return "Script timed out (> 20s)", False
    except Exception as e:
        return str(e), False


def update_readme(entries: list[dict]) -> None:
    """Append new project entries to README.md."""
    readme = Path("README.md")
    if not readme.exists():
        readme.write_text(
            "# 🐍 Python Lab\n\n"
            "Auto-generated Python projects — algorithms, data structures, simulations & more.\n\n"
            "## Projects\n\n"
            "| Date | File | Description |\n"
            "|------|------|-------------|\n"
        )

    content = readme.read_text()
    table_marker = "| Date | File | Description |\n|------|------|-------------|\n"

    new_rows = ""
    for e in entries:
        date = datetime.now().strftime("%Y-%m-%d")
        new_rows += f"| {date} | `{e['filename']}` | {e['description']} |\n"

    if table_marker in content:
        content = content.replace(table_marker, table_marker + new_rows)
    else:
        content += f"\n\n## Projects\n\n| Date | File | Description |\n|------|------|-------------|\n{new_rows}"

    readme.write_text(content)


def main() -> None:
    if not should_run():
        print("[autocommit] Skipping this run — keeping cadence natural.")
        # Write empty commit message so the workflow step exits cleanly
        Path(".commit_message").write_text("")
        sys.exit(0)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[autocommit] ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    projects_dir = Path("projects")
    projects_dir.mkdir(exist_ok=True)

    generated = []
    commit_messages = []
    selected_categories = random.sample(PROJECT_CATEGORIES, PROJECTS_PER_RUN)

    for i, category in enumerate(selected_categories, 1):
        print(f"\n[autocommit] Generating project {i}/{PROJECTS_PER_RUN}: {category[:60]}...")

        try:
            response = generate_project(client, category)
            filename, commit_msg, description, code = parse_response(response)

            if not filename or not code:
                print(f"[autocommit] Parse failed, skipping.")
                continue

            # Deduplicate filenames with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{filename}_{timestamp}.py"
            filepath = projects_dir / safe_filename

            # Write the file
            header = (
                f'"""\nGenerated: {datetime.now().isoformat()}\nDescription: {description}\n"""\n\n'
            )
            filepath.write_text(header + code)

            # Run it to verify + show output
            output, success = run_script(filepath)
            status = "✓ ran successfully" if success else "⚠ run had errors"
            print(f"[autocommit] {status}")
            print(f"[autocommit] Output preview: {output[:200]}")

            generated.append({"filename": safe_filename, "description": description})
            commit_messages.append(commit_msg)

        except Exception as e:
            print(f"[autocommit] Error generating project: {e}")
            continue

    if not generated:
        print("[autocommit] Nothing generated. Exiting.")
        Path(".commit_message").write_text("")
        sys.exit(0)

    # Update README
    update_readme(generated)

    # Write combined commit message
    if len(commit_messages) == 1:
        final_message = commit_messages[0]
    else:
        bullet_list = "\n".join(f"- {m}" for m in commit_messages)
        final_message = f"feat: add {len(commit_messages)} new Python projects\n\n{bullet_list}"

    Path(".commit_message").write_text(final_message)
    print(f"\n[autocommit] Done! Committing {len(generated)} project(s).")
    print(f"[autocommit] Commit message: {final_message}")


if __name__ == "__main__":
    main()
