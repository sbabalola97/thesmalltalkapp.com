#!/usr/bin/env python3
"""Builds website/privacy.html from BETA-PRIVACY-POLICY.md.

Run from the repository root after editing the policy:
    python3 website/build-privacy.py
Handles the Markdown the policy uses: headings, paragraphs, bullet lists,
bold, and links. No dependencies.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "BETA-PRIVACY-POLICY.md"
TARGET = pathlib.Path(__file__).resolve().parent / "privacy.html"


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", out)
    return out


def convert(markdown: str) -> tuple[str, str]:
    title = "Beta privacy policy"
    parts: list[str] = []
    para: list[str] = []
    items: list[str] = []

    def flush() -> None:
        if para:
            parts.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()
        if items:
            parts.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
            items.clear()

    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
        elif line.startswith("# "):
            flush()
            title = line[2:].strip()
        elif line.startswith("## "):
            flush()
            parts.append(f"<h2>{inline(line[3:].strip())}</h2>")
        elif re.match(r"^\s*[-*] ", line):
            if para:
                flush()
            items.append(re.sub(r"^\s*[-*] ", "", line))
        elif items and line.startswith("  "):
            items[-1] += " " + line.strip()
        else:
            para.append(line.strip())
    flush()
    return title, "\n".join(parts)


def main() -> None:
    title, body = convert(SOURCE.read_text(encoding="utf-8"))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Privacy · Small Talk</title>
<meta name="description" content="Privacy policy for the Small Talk prototype beta, from Small Talk Technologies Inc.">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,600,0..100,0..1&family=Manrope:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="site.css">
</head>
<body>
<div class="wrap">
  <header class="site">
    <a class="wordmark" href="/">small talk.</a>
    <a class="back" href="/">Home</a>
  </header>
  <main class="doc">
    <h1>{html.escape(title.replace('Small Talk — ', ''))}</h1>
{body}
  </main>
  <footer class="site">
    <span>© 2026 Small Talk Technologies Inc.</span>
    <nav aria-label="Footer"><a href="/">Home</a><a href="mailto:team@thesmalltalkapp.com">Contact</a></nav>
  </footer>
</div>
</body>
</html>
"""
    TARGET.write_text(page, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
