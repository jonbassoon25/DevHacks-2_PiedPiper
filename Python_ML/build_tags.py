"""Minimal build_tags: produce location_tags.npy and location_tags.json only."""

import os
import json
import argparse
import re
from typing import List

import numpy as np
import pandas as pd

try:
    import requests
except Exception:
    requests = None

CSV_FILENAME = "../location_database.csv"
TAGS_ARRAY_NPY = "location_tags.npy"
TAGS_ARRAY_JSON = "location_tags.json"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma2")


def parse_args():
    p = argparse.ArgumentParser(description="Build tags array using local Ollama (default) or heuristic (optional)")
    p.add_argument("--allow-heuristic", action="store_true", help="Allow fallback to heuristic tagging if Ollama is unavailable")
    return p.parse_args()


def load_csv(path: str = CSV_FILENAME) -> pd.DataFrame:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    alt = os.path.join(script_dir, path)
    candidates = [path]
    if alt not in candidates:
        candidates.append(alt)

    for p in candidates:
        try:
            if not os.path.exists(p):
                continue
            return pd.read_csv(p).fillna("")
        except Exception:
            continue

    existing = [p for p in candidates if os.path.exists(p)]
    if not existing:
        raise FileNotFoundError(f"CSV not found at any of: {candidates}")
    p = existing[0]
    rows = []
    with open(p, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.rstrip('\n')
            if i == 0:
                header = [h.strip() for h in line.split(',')]
                continue
            if line.strip() == '':
                continue
            parts = line.rsplit(',', 5)
            if len(parts) < len(header):
                parts = parts + [''] * (len(header) - len(parts))
            rows.append(parts)
    df = pd.DataFrame(rows, columns=header)
    return df.fillna("")


def is_ollama_available(timeout: float = 2.0) -> bool:
    if requests is None:
        return False
    try:
        resp = requests.get(f"{OLLAMA_URL.rstrip('/')}/api/tags", timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def call_ollama_for_tags(prompt: str, max_tags: int = 8) -> List[str]:
    if requests is None:
        raise RuntimeError("requests is required for Ollama calls")

    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "max_tokens": 200, "temperature": 0.2}

    try:
        resp = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/generate",
            json=payload,
            timeout=30,
            stream=True
        )
    except Exception as e:
        raise RuntimeError(f"Ollama request failed to connect: {e}. Is Ollama running at {OLLAMA_URL}?")

    if not (200 <= resp.status_code < 300):
        raise RuntimeError(f"Ollama returned status {resp.status_code}")

    collected = []
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "response" in obj:
            collected.append(obj["response"])
        if obj.get("done"):
            break

    if not collected:
        raise RuntimeError("Ollama returned no response text")

    text = "".join(collected).strip()

    # Parse into tags (expects comma-separated list)
    cleaned = re.sub(r"\s+", " ", text)
    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    return [p.lower().replace(" ", "-") for p in parts][:max_tags]



def simple_keyword_tags(text: str, max_tags: int = 6) -> List[str]:
    text = re.sub(r"[^\w\s-]", " ", text.lower())
    words = [w for w in text.split() if len(w) > 2]
    stop = {"with", "and", "for", "the", "from", "in", "on", "at", "a", "an", "of"}
    words = [w for w in words if w not in stop]
    freqs = {}
    for w in words:
        freqs[w] = freqs.get(w, 0) + 1
    sorted_words = sorted(freqs.items(), key=lambda x: (-x[1], x[0]))
    tags = [w for w, _ in sorted_words][:max_tags]
    return [t.replace(' ', '-') for t in tags]


def main():
    df = load_csv()
    n = len(df)
    print(f"Loaded {n} rows")

    args = parse_args()
    ollama_ok = is_ollama_available()
    if not ollama_ok and not args.allow_heuristic:
        raise RuntimeError(
            f"Ollama not reachable at {OLLAMA_URL}. Start Ollama (e.g. `ollama run {OLLAMA_MODEL}`) or set OLLAMA_URL."
        )

    if not ollama_ok and args.allow_heuristic:
        print(f"Warning: Ollama not reachable at {OLLAMA_URL}; proceeding with heuristic tagging because --allow-heuristic was set.")

    tags_for_rows = []
    used_ollama = False
    failed_count = 0
    for i, row in df.iterrows():
        text = f"Generate 5 to 8 short, single-word tags (in lowercase, hyphenated if multi-word) that best describe the following place. Return them as a comma-separated list only.\n\nName: {row.get('Name','')}\nDescription: {row.get('Description','')}"

        if ollama_ok:
            try:
                tags = call_ollama_for_tags(text)
                used_ollama = True
            except Exception as e:
                failed_count += 1
                if not args.allow_heuristic:
                    raise RuntimeError(f"Ollama failed during processing row {i}: {e}")
                # fallback
                tags = simple_keyword_tags(text)
        else:
            tags = simple_keyword_tags(text)
        tags_for_rows.append(tags)
        print(f"[Tagging] {i+1}/{n}", end='\r')

    arr = np.array(tags_for_rows, dtype=object)
    np.save(TAGS_ARRAY_NPY, arr)
    with open(TAGS_ARRAY_JSON, 'w', encoding='utf-8') as f:
        json.dump(tags_for_rows, f, ensure_ascii=False, indent=2)

    method = "ollama" if used_ollama and ollama_ok else "heuristic"
    print(f"\nSaved {TAGS_ARRAY_NPY} (len={len(arr)}), and {TAGS_ARRAY_JSON} — tagging method: {method}")


if __name__ == '__main__':
    main()
