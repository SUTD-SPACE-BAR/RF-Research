#!/usr/bin/env python3
"""Glossary harvester and builder for the RF Physics knowledge base.

Three jobs, all from local files only:

1. ``python3 tools/glossary_harvest.py`` (harvest, the default)
   Scans every ``kb/**/*.md`` page and writes candidate glossary terms to
   ``research-logs/raw-harvest/glossary/``:
     candidates.tsv   term, kind, occurrences, pages, top pages, expansions seen
     expansions.tsv   acronym -> written-out form found on a page ("Long Form (ACR)" / "ACR (Long Form)")
     ambiguous.tsv    acronyms written out in two or more different ways (review by hand)
     tags.tsv         front-matter tags with counts and pages
   Candidate kinds: ``caps`` (all-caps tokens of 2-8 chars, digits/hyphens allowed: IIP3, P1DB, CPWG),
   ``mixed`` (mixed-case technical tokens: LoRa, GaN, pHEMT, P1dB), ``dB`` (dB-family units: dBm, dBc/Hz,
   dB-Hz), ``bold`` (short bold phrases, which is how pages mark a defined term), ``tag`` (front matter).

2. ``python3 tools/glossary_harvest.py --missing [N]``
   Lists harvested acronym/unit candidates used on >= N pages (default 3) that are not yet in
   ``tools/glossary_terms.txt`` (as a term or alias). Use it after new pages land.

3. ``python3 tools/glossary_harvest.py --build``
   Regenerates ``GLOSSARY.md`` from ``tools/glossary_terms.txt`` (hand-written definitions) and
   ``tools/glossary_ambiguous.md`` (hand-written ambiguous-acronym section). Every ``[[NN/slug]]`` or
   ``[[NN/slug#anchor]]`` reference is resolved to a relative link and checked to exist; the build fails
   on a missing page. The number of pages using each term is taken from the harvest.

Format of ``tools/glossary_terms.txt`` - one term per line, fields separated by " ‖ " (U+2016):
    Term ‖ Expansion ‖ Meaning (plain English) ‖ Formula / typical value ‖ See ‖ aliases (optional)
``See`` holds one or more ``NN/slug`` (comma-separated, optional ``#anchor``); ``NN/planned|NN/existing`` links the
first alternative that exists, so an entry can name a planned page and fall back until it is written. Lines starting with
``#`` are comments. Write definitions in your own words (CONVENTIONS.md section 4).
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "kb"
OUT = ROOT / "research-logs" / "raw-harvest" / "glossary"
TERMS = ROOT / "tools" / "glossary_terms.txt"
AMBIG = ROOT / "tools" / "glossary_ambiguous.md"
GLOSSARY = ROOT / "GLOSSARY.md"
SEP = " ‖ "

# --------------------------------------------------------------------------------------------
# Page reading and cleaning
# --------------------------------------------------------------------------------------------
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
FENCE_RE = re.compile(r"```.*?```", re.S)
LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
URL_RE = re.compile(r"https?://\S+")
SOURCES_RE = re.compile(r"\n## Sources\b.*", re.S)


def pages() -> list[Path]:
    return sorted(p for p in KB.rglob("*.md") if p.is_file())


def read_page(p: Path) -> tuple[dict, str]:
    """Return (front-matter dict of raw strings, cleaned body)."""
    text = p.read_text(encoding="utf-8", errors="replace")
    fm: dict[str, str] = {}
    m = FM_RE.match(text)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()
        text = text[m.end():]
    text = SOURCES_RE.sub("\n", text)          # bibliography: author names/journals are not terms
    text = FENCE_RE.sub(" ", text)             # code blocks: identifiers are not terms
    text = LINK_TARGET_RE.sub("]", text)       # keep link text, drop target paths
    text = URL_RE.sub(" ", text)
    return fm, text


def parse_tags(fm: dict) -> list[str]:
    raw = fm.get("tags", "").strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [t.strip().strip("'\"") for t in raw.split(",") if t.strip()]


def rel(p: Path) -> str:
    return str(p.relative_to(KB))


# --------------------------------------------------------------------------------------------
# Candidate regexes
# --------------------------------------------------------------------------------------------
# all-caps tokens (2-8 chars) that may contain digits and internal hyphens; >= 2 capital letters,
# or one capital plus a digit (S11, L1, E5a is mixed)
CAPS_RE = re.compile(r"(?<![A-Za-z0-9_\\])([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)(?![A-Za-z0-9_])")
# mixed-case technical tokens: at least two capitals and at least one lower-case letter (LoRa, GaN,
# SiGe, NanoVNA, pHEMT, P1dB). Length 3-12.
MIXED_RE = re.compile(r"(?<![A-Za-z0-9_\\])((?=[A-Za-z0-9]*[A-Z][A-Za-z0-9]*[A-Z])(?=[A-Za-z0-9]*[a-z])[A-Za-z][A-Za-z0-9]{2,11})(?![A-Za-z0-9_])")
# dB-family units
DB_RE = re.compile(r"(?<![A-Za-z])(dB(?:[a-zA-Zµμ]+)?(?:[-/](?:Hz|MHz|K|m|km|m²|m2|sm))?)(?![A-Za-z])")
BOLD_RE = re.compile(r"\*\*([^*\n]{2,48}?)\*\*")
# "ACR (Long Form)" and "Long Form (ACR)"
PAREN_AFTER_ACR = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Za-z0-9\-]{1,9})\s*\(([A-Za-z][^()\n]{3,70}?)\)")
ACR_IN_PAREN = re.compile(r"\(([A-Z][A-Za-z0-9\-]{1,9})(?:s)?[,;)\s]")

STOP_CAPS = {
    # ordinary words, roman numerals, single-letter variables in caps, page-structure words
    "TL", "DR", "TL;DR", "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII", "OK", "AND", "OR", "NOT",
    "THE", "IS", "OF", "TO", "IN", "ON", "NO", "YES", "BY", "AT", "AS", "AN", "BE", "DO", "SO", "UP",
    "WE", "IT", "MY", "ME", "US", "ALL", "ANY", "NB", "ID", "VS", "EG", "IE", "FAQ", "TODO", "NOTE",
}


# Harvested tokens deliberately left out of the glossary (ordinary units and words, document names, people,
# software UI words, part numbers). Extend when --missing reports noise.
NOT_TERMS = {
    "GHz", "MHz", "kHz", "THz", "PASS", "FAIL", "WHEN", "MAX", "THRU", "README", "PDF", "PDFs", "GUI", "GUIs",
    "MATLAB", "macOS", "USD", "SGD", "GST", "DIY", "MIT", "McGraw", "McLean", "McClellan", "GitHub", "WebFetch",
    "PySDR", "SciPy", "PyPI", "JSON", "HTML", "HTTP", "API", "CLI", "CPU", "GPU", "RAM", "ROM", "SD", "PC", "USB",
    "TV", "MB", "GB", "KB", "OK", "EE", "ECE", "NTU", "SUTD", "EPFL", "USC", "NASA", "NIST", "NOAA", "LLNL", "NRL",
    "IRE", "MTT", "MTT-S", "JSSC", "ICASSP", "SPAWC", "BSTJ", "QEX", "TAP", "OCW", "IAP", "LL", "DLR", "WSMR",
    "AliExpress", "DigiKey", "SparkFun", "KEMET", "MACOM", "TDK", "NXP", "AVX", "ATC", "KDS", "HP", "AMD", "ARM",
    "IDs", "DUTs", "VNAs", "NanoVNAs", "SoCs", "MCUs", "ICs", "FFTs", "FIRs", "LPFs", "DACs", "ADCs", "PLLs",
    "VCOs", "TCXOs", "MMICs", "BJTs", "FETs", "MOSFETs", "PCBs", "SMAs", "LNAs", "PAs", "SDRs", "SAWs", "DSAs",
    "LDOs", "MLCCs", "NFs", "SFs", "LOs", "IFs", "PRNs", "DDCs", "NCOs", "EVMs", "LPDAs", "QFNs", "HBTs", "pHEMTs",
    "ESRs", "TLTs", "UCAs", "USRPs", "FEMs", "SRDs", "MACs", "CubeSat", "LiPo", "AU", "USA", "EU", "SG", "AS",
}


def schwartz_hearst(short: str, long_text: str) -> str | None:
    """Return the shortest suffix of long_text whose letters spell `short` (Schwartz & Hearst 2003)."""
    s = [c.lower() for c in short if c.isalnum()]
    lt = long_text.lower()
    si, li = len(s) - 1, len(lt) - 1
    while si >= 0:
        c = s[si]
        while li >= 0 and (lt[li] != c or (si == 0 and li > 0 and lt[li - 1].isalnum())):
            li -= 1
        if li < 0:
            return None
        si -= 1
        li -= 1
    start = lt.rfind(" ", 0, li + 1) + 1
    cand = long_text[start:].strip(" ,;:-–(")
    nwords = len(cand.split())
    if nwords > min(len(s) + 5, 2 * len(s)) or nwords == 0:
        return None
    return cand


def norm_expansion(e: str) -> str:
    e = e.lower().replace("-", " ").replace("–", " ")
    e = re.sub(r"[^a-z0-9 ]", "", e)
    e = re.sub(r"\s+", " ", e).strip()
    words = [w[:-1] if w.endswith("s") and len(w) > 3 else w for w in e.split()]
    return " ".join(words)


def harvest():
    counts = collections.Counter()
    kind = {}
    page_counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    expansions: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    exp_pages: dict[tuple[str, str], set] = collections.defaultdict(set)
    exp_example: dict[tuple[str, str], str] = {}
    tag_pages: dict[str, set] = collections.defaultdict(set)

    for p in pages():
        fm, body = read_page(p)
        r = rel(p)
        for t in parse_tags(fm):
            tag_pages[t].add(r)

        def add(tok, k):
            counts[tok] += 1
            kind.setdefault(tok, k)
            page_counts[tok][r] += 1

        for m in CAPS_RE.finditer(body):
            tok = m.group(1)
            if not (2 <= len(tok) <= 8) or tok in STOP_CAPS:
                continue
            ncap = sum(c.isupper() for c in tok)
            ndig = sum(c.isdigit() for c in tok)
            if ncap >= 2 or (ncap == 1 and ndig >= 1):
                if re.fullmatch(r"[A-Z]\d{3,}", tok):   # R1000 etc.
                    continue
                add(tok, "caps")
        for m in MIXED_RE.finditer(body):
            tok = m.group(1)
            if tok.isupper():
                continue
            add(tok, "mixed")
        for m in DB_RE.finditer(body):
            add(m.group(1), "dB")
        for m in BOLD_RE.finditer(body):
            b = m.group(1).strip().rstrip(":.,")
            letters = sum(c.isalpha() for c in b)
            if letters >= 3 and letters >= 0.6 * len(b.replace(" ", "")) and len(b.split()) <= 5 and "$" not in b:
                add("**" + b + "**", "bold")
        # expansions: Long Form (ACR)
        for m in ACR_IN_PAREN.finditer(body):
            acr = m.group(1)
            if sum(c.isupper() for c in acr) < 2:
                continue
            before = body[max(0, m.start() - 120):m.start()]
            before = re.split(r"[.;:!?\n(\[]", before)[-1]
            cand = schwartz_hearst(acr, before)
            if cand:
                ne = norm_expansion(cand)
                expansions[acr][ne] += 1
                exp_pages[(acr, ne)].add(r)
                exp_example.setdefault((acr, ne), cand)
        # expansions: ACR (Long Form)
        for m in PAREN_AFTER_ACR.finditer(body):
            acr, inside = m.group(1), m.group(2)
            if sum(c.isupper() for c in acr) < 2:
                continue
            inside = re.split(r"[,;=]", inside)[0].strip()
            words = inside.split()
            if not words or len(words) > 8:
                continue
            # accept when initials of the parenthetical spell the acronym (loosely)
            ini = "".join(w[0] for w in re.split(r"[\s\-–]+", inside) if w).lower()
            a = re.sub(r"[^a-z]", "", acr.lower())
            if len(a) >= 2 and (ini.startswith(a) or schwartz_hearst(acr, inside) == inside.strip(" ,;:-–(")):
                ne = norm_expansion(inside)
                expansions[acr][ne] += 1
                exp_pages[(acr, ne)].add(r)
                exp_example.setdefault((acr, ne), inside)

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "candidates.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["term", "kind", "occurrences", "pages", "top_pages", "expansions_seen"])
        for tok, n in sorted(counts.items(), key=lambda kv: (-len(page_counts[kv[0]]), -kv[1], kv[0])):
            top = ", ".join(f"{pg}({c})" for pg, c in page_counts[tok].most_common(4))
            ex = "; ".join(f"{exp_example[(tok, e)]} [{c}]" for e, c in expansions.get(tok, {}).items())
            w.writerow([tok, kind[tok], n, len(page_counts[tok]), top, ex])
    with open(OUT / "expansions.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["acronym", "expansion", "count", "pages"])
        for acr in sorted(expansions):
            for e, c in expansions[acr].most_common():
                w.writerow([acr, exp_example[(acr, e)], c, ", ".join(sorted(exp_pages[(acr, e)]))])
    with open(OUT / "ambiguous.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["acronym", "n_expansions", "expansions (count; pages)"])
        for acr in sorted(expansions):
            if len(expansions[acr]) >= 2:
                parts = [f"{exp_example[(acr, e)]} ({c}; {', '.join(sorted(exp_pages[(acr, e)])[:4])})"
                         for e, c in expansions[acr].most_common()]
                w.writerow([acr, len(expansions[acr]), " | ".join(parts)])
    with open(OUT / "tags.tsv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["tag", "pages", "page_list"])
        for t, ps in sorted(tag_pages.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            w.writerow([t, len(ps), ", ".join(sorted(ps)[:8])])
    n_caps = sum(1 for t in counts if kind[t] in ("caps", "mixed", "dB"))
    print(f"pages scanned: {len(pages())}")
    print(f"acronym/unit candidates: {n_caps} (used on >=2 pages: "
          f"{sum(1 for t in counts if kind[t] in ('caps','mixed','dB') and len(page_counts[t]) >= 2)})")
    print(f"bold phrases: {sum(1 for t in counts if kind[t] == 'bold')}; tags: {len(tag_pages)}")
    print(f"acronyms with expansions: {len(expansions)}; with >=2 different expansions: "
          f"{sum(1 for a in expansions if len(expansions[a]) >= 2)}")
    print(f"wrote {OUT.relative_to(ROOT)}/{{candidates,expansions,ambiguous,tags}}.tsv")
    return counts, kind, page_counts


# --------------------------------------------------------------------------------------------
# Glossary build
# --------------------------------------------------------------------------------------------
def domain_dirs() -> dict[str, str]:
    return {d.name[:2]: d.name for d in KB.iterdir() if d.is_dir() and d.name[:2].isdigit()}


def resolve(ref: str, dd: dict[str, str]) -> str:
    """'07/noise-figure-and-friis#anchor' -> 'kb/07-noise-linearity/noise-figure-and-friis.md#anchor'."""
    ref = ref.strip()
    anchor = ""
    if "#" in ref:
        ref, anchor = ref.split("#", 1)
        anchor = "#" + anchor
    if "/" not in ref:
        raise ValueError(f"bad reference {ref!r}")
    dom, slug = ref.split("/", 1)
    dom = dom[:2]
    if dom not in dd:
        raise ValueError(f"unknown domain in {ref!r}")
    path = KB / dd[dom] / (slug + ".md")
    if not path.exists():
        raise FileNotFoundError(f"missing page for reference {ref!r}: {path.relative_to(ROOT)}")
    return f"kb/{dd[dom]}/{slug}.md{anchor}"


def pick(ref: str, dd) -> str:
    """'a|b|c' -> the first alternative whose page exists (lets an entry point at a planned page and fall
    back to an existing one until the planned page is written)."""
    alts = [a.strip() for a in ref.split("|") if a.strip()]
    for a in alts:
        try:
            resolve(a, dd)
            return a
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"no existing page among {alts}")


def link_md(ref: str, dd) -> str:
    ref = pick(ref, dd)
    target = resolve(ref, dd)
    label = ref.split("#")[0].strip()
    return f"[{label}]({target.replace(' ', '%20')})"


INLINE_REF = re.compile(r"\[\[([0-9]{2}/[a-z0-9\-]+(?:#[A-Za-z0-9\-_.]+)?)\]\]")


def expand_inline(text: str, dd) -> str:
    return INLINE_REF.sub(lambda m: link_md(m.group(1), dd), text)


def esc(cell: str) -> str:
    return cell.replace("|", "\\|")


def load_terms() -> list[dict]:
    rows = []
    for ln, line in enumerate(TERMS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = [x.strip() for x in line.split("‖")]
        if len(parts) < 5:
            raise ValueError(f"{TERMS.name}:{ln}: expected >= 5 fields, got {len(parts)}: {line[:80]}")
        rows.append({"term": parts[0], "exp": parts[1], "meaning": parts[2], "formula": parts[3],
                     "see": parts[4], "aliases": parts[5] if len(parts) > 5 else "", "line": ln})
    return rows


def sort_key(term: str) -> tuple:
    t = term.lstrip("*_`'\"(")
    first = t[:1]
    if first.isascii() and first.isalpha():
        sec = first.upper()
    elif first.isdigit():
        sec = "0–9"
    else:
        sec = "Symbols"
    return (sec, t.lower())


def covered_tokens(rows) -> set[str]:
    cov = set()
    for r in rows:
        cov.add(r["term"])
        cov.add(r["term"].split(" (")[0])
        for piece in re.split(r"\s*/\s*|\s*,\s*", r["term"]):
            cov.add(piece.strip())
            cov.add(piece.strip().split(" ")[0])
        for a in r["aliases"].split(","):
            if a.strip():
                cov.add(a.strip())
    return cov


def build():
    _, _, page_counts = harvest()
    dd = domain_dirs()
    rows = load_terms()
    seen = {}
    for r in rows:
        k = r["term"]
        if k in seen:
            raise ValueError(f"duplicate term {r['term']!r} (lines {seen[k]} and {r['line']})")
        seen[k] = r["line"]
    sections: dict[str, list] = collections.defaultdict(list)
    for r in rows:
        sec, _ = sort_key(r["term"])
        sections[sec].append(r)
    order = ["0–9"] + [chr(c) for c in range(ord("A"), ord("Z") + 1)] + ["Symbols"]
    present = [s for s in order if s in sections]
    n_pages = len(pages())

    out = []
    out.append("# GLOSSARY — acronyms and specialist terms used in this knowledge base\n")
    out.append(f"**{len(rows)} terms** harvested from the {n_pages} pages under `kb/` and defined in plain English. "
               "Each entry links to the KB page that explains the idea properly; the definitions here are short "
               "reminders, written to agree with those pages. Last regenerated 2026-10-12 by W6-F1.\n")
    out.append("## How to use it\n")
    out.append("- Look the term up in the A–Z tables below (acronyms, units such as dBc/Hz, and named concepts are "
               "mixed together and sorted alphabetically; terms that start with a digit are under **0–9**, Greek "
               "symbols under **Symbols**).\n"
               "- **Expansion** is what the letters stand for; **Meaning** is a one-to-three-sentence plain-English "
               "explanation; **Formula / typical value** gives the defining equation or a number to sanity-check "
               "against (values follow the KB's canonical conventions: $T_0$ = 290 K, dBm re 1 mW, gain in dBi, "
               "50 Ω, $e^{j\\omega t}$ — see [canonical values](kb/00-math-foundations/canonical-values-and-conventions.md)); **See** links the page to read next.\n"
               "- Some acronyms mean different things on different pages (for example *NF*, *PG*, *CR*). Check the "
               "[ambiguous-acronyms section](#ambiguous-acronyms-in-this-kb) before assuming a meaning.\n"
               "- If a term is missing, it may be defined in bold on its page: search `kb/` for `**term**`.\n")
    out.append("## How to regenerate or extend it\n")
    out.append("- Definitions live in `tools/glossary_terms.txt` (one line per term, fields separated by ` ‖ `: "
               "term ‖ expansion ‖ meaning ‖ formula ‖ see ‖ aliases). The ambiguous-acronym section lives in "
               "`tools/glossary_ambiguous.md`. Edit those files, never this one.\n"
               "- `python3 tools/glossary_harvest.py` re-harvests candidate terms from every page (all-caps tokens "
               "of 2–8 characters, mixed-case tokens such as LoRa or P1dB, dB-family units, bold phrases, "
               "\"Long Form (ACR)\" expansions and front-matter tags) into `research-logs/raw-harvest/glossary/`, "
               "including `ambiguous.tsv` (acronyms written out in more than one way).\n"
               "- `python3 tools/glossary_harvest.py --missing 3` lists acronyms used on at least 3 pages that the "
               "glossary does not define yet. Add them to `tools/glossary_terms.txt`.\n"
               "- `python3 tools/glossary_harvest.py --build` rewrites this file and fails if any **See** link "
               "points at a page that does not exist. Part numbers are left out on purpose, except for part "
               "families that the KB uses as concepts (for example SX126x, R820T).\n")
    out.append("**Jump to:** " + " · ".join(f"[{s}](#{anchor_for(s)})" for s in present) +
               " · [Ambiguous acronyms](#ambiguous-acronyms-in-this-kb)\n")
    for s in present:
        out.append(f"## {s}\n")
        out.append("| Term | Expansion | Meaning (plain English) | Formula / typical value | See |")
        out.append("|---|---|---|---|---|")
        for r in sorted(sections[s], key=lambda r: sort_key(r["term"])):
            see = ", ".join(link_md(x, dd) for x in r["see"].split(",") if x.strip())
            out.append("| " + " | ".join([
                f"**{esc(r['term'])}**", esc(expand_inline(r["exp"], dd)), esc(expand_inline(r["meaning"], dd)),
                esc(expand_inline(r["formula"], dd)), see]) + " |")
        out.append("")
    if AMBIG.exists():
        out.append(expand_inline(AMBIG.read_text(encoding="utf-8").strip(), dd))
        out.append("")
    GLOSSARY.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote GLOSSARY.md: {len(rows)} terms in {len(present)} sections")


def anchor_for(section: str) -> str:
    # GitHub-style anchor: lower-case, drop punctuation except hyphens, spaces -> hyphens
    a = section.lower()
    a = re.sub(r"[^\w\- ]", "", a)
    return a.replace(" ", "-")


def missing(min_pages: int):
    counts, kind, page_counts = harvest()
    cov = covered_tokens(load_terms()) if TERMS.exists() else set()
    cov_l = {c.lower() for c in cov}
    def is_noise(t: str) -> bool:
        # figure/table/step labels (T1, P12, S3, A-1), agent IDs (W4-D1), plain units, plurals of covered terms
        if re.fullmatch(r"[A-Z]-?\d{1,2}", t) or re.fullmatch(r"W\d-[A-Z]\d", t) or t in NOT_TERMS:
            return True
        return t.endswith("s") and (t[:-1] in cov or t[:-1].lower() in cov_l)
    rows = [(t, kind[t], counts[t], len(page_counts[t])) for t in counts
            if kind[t] in ("caps", "mixed", "dB") and len(page_counts[t]) >= min_pages
            and t not in cov and t.lower() not in cov_l and not is_noise(t)]
    rows.sort(key=lambda r: (-r[3], -r[2]))
    print(f"\n{len(rows)} candidates on >= {min_pages} pages not in the glossary:")
    for t, k, n, npg in rows:
        top = ", ".join(pg for pg, _ in page_counts[t].most_common(3))
        print(f"{t}\t{k}\t{n}\t{npg}\t{top}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--build", action="store_true", help="regenerate GLOSSARY.md")
    ap.add_argument("--missing", nargs="?", const=3, type=int, metavar="N",
                    help="list candidates on >= N pages not yet in the glossary")
    a = ap.parse_args()
    if a.build:
        build()
    elif a.missing is not None:
        missing(a.missing)
    else:
        harvest()
