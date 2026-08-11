import pathlib
import datetime
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- DATE FORMATTING UTILITIES ---

def get_iso_date() -> str:
    """Returns YYYY-MM-DD for filenames and sort order."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

def get_human_date() -> str:
    """Returns 'D MMM YYYY' (e.g. '5 Aug 2026') for human-facing content.
    No leading zero on day, 3-letter month, no commas."""
    now = datetime.datetime.now(datetime.timezone.utc)
    day = str(now.day)  # Strips leading zero
    month_year = now.strftime("%b %Y")
    return f"{day} {month_year}"

# --- NODE PROMPT LOADING ---
# Resolves to project root / nodes
NODES_DIR = pathlib.Path(__file__).resolve().parent.parent / "nodes"


def load_node(name: str) -> str:
    """Loads a node definition from nodes/<name>.md, relative to project root."""
    return (NODES_DIR / f"{name}.md").read_text(encoding="utf-8").strip()


# --- STANDING PRODUCT & BUSINESS CONTEXT ---
PRODUCT_CONTEXT = load_node("context")

# --- SCOUT LOADING ---
# Resolves to project root / scouts
SCOUTS_DIR = pathlib.Path(__file__).resolve().parent.parent / "scouts"


def load_scouts() -> list[dict]:
    """Loads all scout definitions from scouts/*.md, relative to project root."""
    if not SCOUTS_DIR.exists():
        raise FileNotFoundError(f"Scouts directory missing: {SCOUTS_DIR}")

    scout_files = sorted(SCOUTS_DIR.glob("*.md"))
    if not scout_files:
        raise ValueError(f"No scout markdown files found in {SCOUTS_DIR}")

    scouts = []
    for file_path in scout_files:
        scout_id = file_path.stem
        lines = file_path.read_text(encoding="utf-8").strip().splitlines()

        name = scout_id.replace("_", " ").title() + " Scout"
        queries = []
        time_range = "week"
        topic = "general"

        current_section = None
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("# "):
                name = stripped.lstrip("#").strip()
                continue
            elif stripped.startswith("## "):
                current_section = stripped.lstrip("#").strip().lower()
                continue

            if current_section in ("search terms", "queries", "search queries"):
                clean_term = stripped.lstrip("-* ").strip()
                if clean_term:
                    queries.append(clean_term)
            elif current_section == "time range":
                time_range = stripped.lstrip("-* ").strip()
            elif current_section == "topic":
                topic = stripped.lstrip("-* ").strip()

        if not queries:
            queries = [name]

        query_string = " OR ".join(queries)
        scouts.append({
            "id": scout_id,
            "name": name,
            "queries": queries,
            "query": query_string,
            "time_range": time_range,
            "topic": topic,
        })

    return scouts


# --- MODULAR SEARCH SCOUTS CONFIGURATION ---
SCOUT_QUERIES = load_scouts()

# --- SYSTEM NODES ---
SKEPTIC_SYSTEM_PROMPT = load_node("skeptic")
SYNTHESIS_SYSTEM_PROMPT = load_node("synthesis")
