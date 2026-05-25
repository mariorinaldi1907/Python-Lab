
import anthropic
import os
import random
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# ── Tuning knobs ─────────────────────────────────────────────────────────────
COMMIT_PROBABILITY = 1.0   # set back to 0.70 after first successful test run
PROJECTS_PER_RUN = random.choice([1, 1, 1, 2, 2, 3])
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_CATEGORIES = [
    "a data structures implementation (e.g. trie, AVL tree, LRU cache, bloom filter, skip list)",
    "an algorithm (e.g. Dijkstra, A*, KMP string search, topological sort, Bellman-Ford)",
    "a math/number theory utility (e.g. sieve of Eratosthenes, fast exponentiation, matrix ops)",
    "a text processing tool (e.g. tokenizer, Markov chain text generator, diff algorithm)",
    "a mini simulation (e.g. Conway's Game of Life, random walk, bouncing balls, epidemic model)",
    "a statistics/probability module (e.g. bootstrapping, chi-square test, Bayesian updater)",
    "a design pattern demo (e.g. observer, strategy, command, decorator with real use case)",
    "a puzzle/game solver (e.g. Sudoku, N-Queens, maze generator, word ladder)",
    "a functional programming utility (e.g. lazy evaluation, monadic pipeline, memoization)",
    "a file/data parser (e.g. CSV analyzer, log parser, config file reader, JSON validator)",
    "a mini interpreter or expression evaluator (e.g. RPN calculator, simple expression parser)",
    "a graph algorithm (e.g. cycle detection, shortest path variants, minimum spanning tree)",
    "a compression/encoding utility (e.g. run-length encoding, Huffman coding, base-N encoder)",
    "a geometry/spatial utility (e.g. convex hull, point-in-polygon, rectangle packing)",
    "a concurrency pattern demo using threading or asyncio (e.g. producer-consumer, rate limiter)",
    "a CLI tool that does something genuinely useful (file organizer, log summarizer, todo tracker)",
    "a simple machine learning algorithm from scratch (e.g. k-means, linear regression, kNN)",
    "a data pipeline utility (e.g. ETL script, data cleaner, schema validator)",
]

# Authentic-sounding commit message styles a real developer would write
COMMIT_STYLES = [
    "casual",       # "been playing around with X, got it working"
    "technical",    # "implement X with Y approach for better Z"
    "reflective",   # "finally figured out why X was slow — switched to Y"
    "iterative",    # "clean up X, add edge case handling"
    "exploratory",  # "experimenting with X to see if it's faster than Y"
]

SYSTEM_PROMPT = """You are Mario, a university student and developer who codes for fun and learning.
You write clean Python code and your commit messages sound like a real person — sometimes casual,
sometimes technical, always genuine. Never robotic or overly formal."""


def should_run() -> bool:
    roll = random.random()
    print(f"[autocommit] Commit roll: {roll:.2f} (threshold: {COMMIT_PROBABILITY})")
    return roll < COMMIT_PROBABILITY


def generate_project(client: anthropic.Anthropic, category: str) -> str:
    """Call Claude API to generate a Python project with a personal commit style."""
    style = random.choice(COMMIT_STYLES)

    style_instructions = {
        "casual": (
            "Write the commit message casually, like you're talking to a friend. "
            "Examples: 'got the LRU cache working finally', 'quick script to parse logs', "
            "'been messing around with graph traversal'"
        ),
        "technical": (
            "Write a clean technical commit message. "
            "Examples: 'implement Dijkstra with min-heap for O((V+E) log V)', "
            "'add bloom filter with configurable false positive rate'"
        ),
        "reflective": (
            "Write a commit message that sounds like you learned something or fixed a bug. "
            "Examples: 'turns out my original BFS was O(n²), rewrote it properly', "
            "'finally understood how Huffman coding works, implemented it from scratch'"
        ),
        "iterative": (
            "Write a commit message that sounds like you're improving existing work. "
            "Examples: 'clean up the matrix class, add transpose and determinant', "
            "'add better error handling to the CSV parser'"
        ),
        "exploratory": (
            "Write a commit message that sounds experimental and curious. "
            "Examples: 'playing with cellular automata, Conway rules implemented', "
            "'trying out a Markov chain text generator — actually works pretty well'"
        ),
    }

    prompt = f"""Write a complete, working Python script implementing {category}.

The script should feel like something a developer named Mario genuinely built while learning or experimenting.

Code requirements:
- 60–180 lines (excluding blank lines and comments)
- Uses ONLY Python standard library (no pip installs)
- Every function/class has a docstring
- Has a `if __name__ == "__main__":` block with a real demo that prints meaningful output
- Must be syntactically correct and runnable as-is
- Comments should sound human, not robotic (occasional "# this is the tricky part" style notes are fine)

Commit message style: {style_instructions[style]}
The commit message must NOT start with "feat:", "chore:", etc. — just write it naturally.
Keep it under 72 characters. Lowercase. No period at the end.

Description style: One casual sentence about what it does, like you'd tell a friend.

Respond in EXACTLY this format (no extra text):

FILENAME: <descriptive_snake_case_name>
COMMIT_MESSAGE: <natural human commit message>
DESCRIPTION: <one casual sentence about what it does>
CODE:
<complete python source code>"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
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
    if code.startswith("```"):
        code = "\n".join(code.split("\n")[1:])
    if code.endswith("```"):
        code = "\n".join(code.split("\n")[:-1])

    return filename, commit_message, description, code.strip()


def run_script(filepath: Path) -> tuple[str, bool]:
    """Run the generated script and capture output."""
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
            "# Python Lab\n\n"
            "A collection of Python scripts I've built while learning — algorithms, "
            "data structures, simulations, tools, and experiments.\n\n"
            "## Projects\n\n"
            "| Date | File | What it does |\n"
            "|------|------|--------------|\n"
        )

    content = readme.read_text()
    table_marker = "| Date | File | What it does |\n|------|------|--------------|\n"

    new_rows = ""
    for e in entries:
        date = datetime.now().strftime("%Y-%m-%d")
        new_rows += f"| {date} | `{e['filename']}` | {e['description']} |\n"

    if table_marker in content:
        content = content.replace(table_marker, table_marker + new_rows)
    else:
        content += f"\n\n## Projects\n\n| Date | File | What it does |\n|------|------|--------------|\n{new_rows}"

    readme.write_text(content)


def main() -> None:
    if not should_run():
        print("[autocommit] Skipping this run — keeping cadence natural.")
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
    selected_categories = random.sample(PROJECT_CATEGORIES, min(PROJECTS_PER_RUN, len(PROJECT_CATEGORIES)))

    for i, category in enumerate(selected_categories, 1):
        print(f"\n[autocommit] Generating project {i}/{len(selected_categories)}: {category[:60]}...")

        try:
            response = generate_project(client, category)
            filename, commit_msg, description, code = parse_response(response)

            if not filename or not code:
                print("[autocommit] Parse failed, skipping.")
                continue

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{filename}_{timestamp}.py"
            filepath = projects_dir / safe_filename

            # Write file with a human-style header comment
            header = f"# {description}\n# written: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            filepath.write_text(header + code)

            output, success = run_script(filepath)
            status = "✓ ran successfully" if success else "⚠ run had errors (keeping anyway)"
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

    update_readme(generated)

    # For multiple projects, combine messages naturally
    if len(commit_messages) == 1:
        final_message = commit_messages[0]
    else:
        # Pick the best one as the main message, list others as context
        final_message = commit_messages[0] + "\n\nalso:\n" + "\n".join(f"- {m}" for m in commit_messages[1:])

    Path(".commit_message").write_text(final_message)
    print(f"\n[autocommit] Done! Committing {len(generated)} project(s).")
    print(f"[autocommit] Commit message: {final_message}")


if __name__ == "__main__":
    main()
