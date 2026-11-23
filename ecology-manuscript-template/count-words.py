#!/usr/bin/env python3
"""Write separate prose-only TeXcount estimates for the abstract and main text."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent

def count(name):
    result = subprocess.run(
        ['texcount', '-utf8', '-sum=1,0,0,0,0,0,0', '-1', str(ROOT / name)],
        check=True, capture_output=True, text=True,
    )
    value = result.stdout.strip()
    if not value.isdigit():
        raise RuntimeError(f'TeXcount did not return a numeric count for {name}: {value}')
    return int(value)

abstract = count('sections/abstract.tex')
main = count('sections/manuscript.tex')
(ROOT / 'wordcounts.tex').write_text(
    '% Generated estimates: prose only; headings, captions, equations and supplement excluded.\n'
    f'\\newcommand{{\\AbstractWordCount}}{{{abstract}}}\n'
    f'\\newcommand{{\\MainWordCount}}{{{main}}}\n'
)
print(f'Abstract: {abstract}; main text: {main} (prose-only estimates).')
