#!/usr/bin/env python3
"""Checks that the catalog, the base constitution, the skill and the docs agree with each other.

Every `#n` names a principle that exists, the theme index matches the theme tables, the skill's theme table
reaches every principle, every principle and article is complete, the articles are numbered in order, stated
counts and article ranges are true, and every relative link and anchor resolves outside code fences. Run it from the repository root (`make check`), or pass the root. Standard library only.
"""

import re
import sys
from pathlib import Path

SKILL = Path("skills/architecture-constitution")
CATALOG = SKILL / "references/principles.md"
BASE = SKILL / "references/constitution-base.md"
ROMAN = "I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX".split()


def numbers(text):
    """'1–9, 120' -> {1, …, 9, 120}"""
    out = set()
    for part in re.findall(r"\d+(?:–\d+)?", text):
        a, _, b = part.partition("–")
        out |= set(range(int(a), int(b or a) + 1))
    return out


def unfence(text):
    """The text with fenced code blanked out, line numbers kept: links and headings there aren't rendered."""
    return re.sub(r"```.*?```", lambda f: "\n" * f[0].count("\n"), text, flags=re.S)


def anchors(text):
    """GitHub's anchors for a file's headings; a repeated heading gets -1, -2, …"""
    seen, out = {}, set()
    for heading in re.findall(r"^#{1,6} (.+)$", unfence(text), re.M):
        s = re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
        out.add(f"{s}-{seen[s]}" if s in seen else s)
        seen[s] = seen.get(s, 0) + 1
    return out


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def check(root):
    errors = []

    def err(path, line, msg):
        errors.append(f"{path.relative_to(root)}:{line}: {msg}")

    docs = {p: p.read_text(encoding="utf-8") for p in sorted(root.rglob("*.md")) if ".git" not in p.parts}
    cat, base, skill = root / CATALOG, root / BASE, root / SKILL / "SKILL.md"
    for p in (cat, base, skill):
        if p not in docs:
            return [f"{p.relative_to(root)}: missing"]

    # The catalog: one row per principle, grouped in theme sections that the index at the top lists.
    rows, themes, index, section, stars = {}, {}, {}, None, 0
    for i, line in enumerate(docs[cat].splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
            themes[section] = set()
        if m := re.match(r"\| \[([^\]]+)\]\(#[^)]+\) \| ([\d–, ]+) \|$", line):
            index[m[1]] = (numbers(m[2]), i)
        if m := re.match(r"\| (\d+) \| \*\*", line):
            n = int(m[1])
            if n in rows or section is None:
                err(cat, i, f"principle {n} is defined twice or outside a theme")
            rows[n] = i
            themes.setdefault(section, set()).add(n)
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            if len(cells) != 5 or not all(cells):
                err(cat, i, f"principle {n} needs number, rule, why, check and conflicts, none empty")
            stars += "★" in line
    if not rows or not index:
        return errors + [f"{CATALOG}: no principle rows or no theme index found"]
    for name, (nums, i) in index.items():
        if themes.get(name) != nums:
            err(cat, i, f"theme '{name}' lists {sorted(nums)}, its table holds {sorted(themes.get(name, []))}")
    for name, nums in themes.items():
        if nums and name not in index:
            err(cat, 1, f"theme '{name}' is missing from the index")

    # The skill's theme table must reach every principle.
    text = docs[skill]
    table = re.search(r"\| The input touches \| Themes \(#\) \|\n\|[-|]+\|\n((?:\|.*\|\n)+)", text)
    reached = numbers("".join(r.rsplit("|", 2)[1] for r in table[1].splitlines())) if table else set()
    if reached != set(rows):
        err(skill, 1, f"theme table misses {sorted(set(rows) - reached)}, names unknown {sorted(reached - set(rows))}")

    # The base: articles numbered I, II, … in order, the lean ones first, as the profile line says.
    arts = []
    for i, line in enumerate(docs[base].splitlines(), 1):
        if not line.startswith("### "):
            continue
        m = re.match(r"### ([IVXL]+)\. .+ \((lean|full)(?:; #\d+(?:, #\d+)*)?\)$", line)
        if not m:
            err(base, i, "an article heading reads '### <numeral>. <title> (lean|full; #n, …)'")
        elif m[1] != ROMAN[len(arts)] or (m[2] == "lean" and any(p == "full" for _, p in arts)):
            err(base, i, f"article {m[1]} is out of order")
        else:
            arts.append((m[1], m[2]))
    lean = [a for a, p in arts if p == "lean"]
    m = re.search(r"\*\*lean\*\*:.*Articles I–([IVXL]+)\.", docs[base])
    if not arts or not lean or not m or m[1] != lean[-1]:
        err(base, 1, f"the lean profile line must name Articles I–{lean[-1] if lean else '?'}")
    for sec in re.split(r"\n(?=### )", docs[base])[1:]:
        head = sec.splitlines()[0]
        for part in ("Rule", "Why", "Check"):
            if f"\n- **{part}:** " not in sec:
                err(base, line_of(docs[base], docs[base].index(head)), f"'{head}' has no {part}")
    ranges = {f"I–{lean[-1]}" if lean else None, f"I–{arts[-1][0]}" if arts else None}

    # Front matter, as the Agent Skills format requires it.
    fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
    name = fm and re.search(r"^name: (.+)$", fm[1], re.M)
    desc = fm and re.search(r'^description: "?(.+?)"?$', fm[1], re.M)
    if not name or name[1] != SKILL.name or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name[1]):
        err(skill, 2, f"name must be '{SKILL.name}', the folder's name")
    if not desc or len(desc[1]) > 1024:
        err(skill, 3, "description is missing or longer than 1024 characters")

    # Every doc: references, counts and links.
    counts = {"principles": len(rows), "themes": len(index), "articles": len(arts)}
    refs = links = 0
    for path, text in docs.items():
        for m in re.finditer(r"(?<![\w&/])#(\d+)\b", text):
            refs += 1
            if int(m[1]) not in rows:
                err(path, line_of(text, m.start()), f"#{m[1]} is no principle")
        for m in re.finditer(r"\b(\d+)\s+(principles|themes|articles)\b|\bcore\s+(\d+)\b", text):
            stated, want = (m[3], stars) if m[3] else (m[1], counts[m[2]])
            if int(stated) != want:
                err(path, line_of(text, m.start()), f"'{' '.join(m[0].split())}', but there are {want}")
        for m in re.finditer(r"\bArticles\s+(I–[IVXL]+)\b", text):
            if m[1] not in ranges:
                err(path, line_of(text, m.start()), f"'Articles {m[1]}' is neither the lean profile nor all articles")
        for m in re.finditer(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", unfence(text)):
            target, _, anchor = m[1].partition("#")
            if re.match(r"[a-z]+:", target):
                continue
            links += 1
            dest = (root / target.lstrip("/") if target.startswith("/") else path.parent / target) if target else path
            if not dest.resolve().exists():
                err(path, line_of(text, m.start()), f"link to missing {m[1]}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest.read_text(encoding="utf-8")):
                err(path, line_of(text, m.start()), f"no heading for anchor #{anchor}")
    if not errors:
        print(f"ok: {len(rows)} principles in {len(index)} themes, {len(arts)} articles, {refs} references, "
              f"{links} links in {len(docs)} files")
    return errors


if __name__ == "__main__":
    found = check(Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve())
    print("\n".join(found), file=sys.stderr)
    sys.exit(1 if found else 0)
