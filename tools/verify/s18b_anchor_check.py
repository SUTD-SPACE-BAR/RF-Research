"""W5-S18b: check that every relative Markdown link with a #fragment resolves to a heading anchor.

tools/build_index.py --check validates the target file only, not the #anchor. This script slugs
headings the way GitHub does (lower-case; keep letters, marks, numbers, '_', '-', ' '; spaces -> '-')
and reports links whose fragment matches no heading in the target page.

Run: python3 tools/verify/s18b_anchor_check.py [file ...]   (default: every kb/**/*.md)
"""
import glob, os, re, sys, unicodedata


def slug(h):
    h = h.strip().lower()
    h = re.sub(r"[*`]", "", h)                                  # markdown emphasis/code
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)               # links -> text
    h = re.sub(r"\$", "", h)
    out = "".join(ch for ch in h if ch in "-_ " or unicodedata.category(ch)[0] in "LMN")
    return out.replace(" ", "-")


_cache = {}


def anchors(path):
    if path not in _cache:
        a, seen = set(), {}
        try:
            for line in open(path, encoding="utf-8"):
                m = re.match(r"#{1,6}\s+(.*)", line)
                if m:
                    s = slug(m.group(1))
                    n = seen.get(s, 0)
                    a.add(s if n == 0 else f"{s}-{n}")
                    seen[s] = n + 1
        except FileNotFoundError:
            a = None
        _cache[path] = a
    return _cache[path]


files = sys.argv[1:] or glob.glob("kb/**/*.md", recursive=True)
bad = 0
for f in files:
    text = open(f, encoding="utf-8").read()
    for link, frag in re.findall(r"\]\(([^)#\s]*\.md)?#([^)\s]+)\)", text):
        tgt = os.path.normpath(os.path.join(os.path.dirname(f), link)) if link else f
        a = anchors(tgt)
        if a is None:
            print(f"MISSING FILE  {f} -> {link}#{frag}"); bad += 1
        elif frag.lower() not in a:
            print(f"BAD ANCHOR    {f} -> {link or '(self)'}#{frag}"); bad += 1
print(f"{bad} bad anchor(s) in {len(files)} file(s)")
