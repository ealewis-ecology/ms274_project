# Quantitative Ecology Manuscript Template · v2.0

A reusable manuscript, supplement and reviewer-response workflow. Updated 4 October 2026. All authors, comments and results in the examples are fictitious or illustrative.

## Start in Overleaf

1. Upload the complete ZIP as a new project. Keep the files and folders together.
2. Select `main.tex` as the main document and pdfLaTeX as the compiler. Use TeX Live 2024 or newer. Biber runs through latexmk.
3. Edit `metadata.tex`, then the three files in `sections/` and `references.bib`.
4. Compile `main.tex` for the review PDF. Select `reading.tex` for a compact copy without line numbers, draft notes or blue revision text.
5. Compile `main.tex` again before selecting `response.tex`. The response imports labels from `main.aux`; its page and line references refer to the review PDF.

A reading PDF is not an anonymized or journal-formatted submission. Edit author information and comply with the journal's instructions separately.

## Files

| File                         | Role                                                               |
| ---------------------------- | ------------------------------------------------------------------ |
| `main.tex`                   | Review entry point, main references, supplement and its references |
| `reading.tex`                | Same content in clean reading mode                                 |
| `response.tex`               | Numbered reviewer comments, replies and manuscript excerpts        |
| `metadata.tex`               | Title, author block, journal, revision date and keywords           |
| `ecology.sty`                | Consolidated typography, theorem, reference and numbering tools    |
| `sections/abstract.tex`      | Abstract only, counted separately                                  |
| `sections/manuscript.tex`    | Main text, figures, tables and end matter                          |
| `sections/supplement.tex`    | Supplement, with its own contents and S numbering                  |
| `references.bib`             | Shared reference database, separated by `refsection`               |
| `figures/example-figure.tex` | Portable vector illustration with no external assets               |
| `count-words.py`             | Optional prose-only TeXcount estimates                             |
| `wordcounts.tex`             | Optional generated count macros (not printed by default)           |
| `latexmkrc`                  | Shared local / Overleaf build configuration                        |

## Local build

Requires an up-to-date TeX Live or MiKTeX installation with pdfLaTeX, latexmk and Biber. Python and TeXcount are needed only for the optional count helper.

```sh
python3 count-words.py
latexmk -pdf main.tex
latexmk -pdf reading.tex
latexmk -pdf response.tex
```

Do not build response and main concurrently: the response reads the manuscript's auxiliary file. The default example was tested with pdfLaTeX and Biber; journal-specific classes and XeLaTeX/LuaLaTeX require their own validation.

## References

Each `refsection` has an independent bibliography. The optional `\MainReferenceCount` and `\SupplementReferenceCount` macros count entries printed in the main and supplementary lists, **not unique references across the entire project**. A source cited in both lists is counted once in each list. Counts settle after repeated LaTeX passes; latexmk handles this.

The author–year style uses biblatex/Biber. `natbib=true` preserves familiar `\citep`, `\citet` and `\citealt` syntax, but it does not make a BibTeX `.bst` compatible with biblatex. If a journal requires a `.bst`, migrate to its class and BibTeX workflow rather than loading natbib and biblatex together.

## Numbering and cross-references

Use `\label` immediately after a section, statement or caption and refer to it with `\cref` or `\Cref`. Use `\eqref` when only the equation number is wanted. Theorem, proposition, lemma and corollary share a sequence, so the next mathematical statement has an unambiguous number. Supplementary counters restart with S prefixes and distinct hyperlink targets.

Place line labels at the passages that will be cited in replies:

```tex
\linelabel{line:question-start}
The revised paragraph begins here ...
... and ends here.\linelabel{line:question-end}
```

In `response.tex`:

```tex
\wherechanged{line:question-start}{line:question-end}
\cref{m-eq:logistic}
\pageref{m-sec:methods}
```

The `m-` prefix keeps imported manuscript labels distinct from response labels. Never copy `main.aux` from a different revision. Compare the printed line ranges with the actual submission PDF; final edits can move lines and pages. Link destinations depend on `main.pdf` staying alongside the response PDF, so distribute both together when those links matter.

## Review and reading modes

`main.tex` sets `\ReviewMode` to 1. `reading.tex` sets it to 0 and inputs the same source. Review mode has 1.5 line spacing and continuous line numbers; reading mode is compact. Modern lineno handles amsmath without the legacy manual equation/align patches.

`\revision{new prose}` is blue in the review PDF and plain in the reading PDF. `\draftnote{a note}` appears only in review mode; remove unresolved notes before submission. Use revision highlighting for prose. For changes spanning complex equations, tables or citations, use a tested diff workflow and inspect its output.

## Word-count scope

`count-words.py` writes separate estimates for the abstract and the main-text file. It excludes headings, figure/table captions, displayed and inline mathematics, and the supplement. TeXcount ignore directives also exclude the figure/table examples. Acknowledgements, contributions and the open-research statement remain part of the main-text estimate; move or mark those regions if the journal excludes them.

These are estimates, not a guarantee of a journal's counting rules. Inspect the count after introducing custom macros or additional `\input` files; the helper counts the two named files and does not recursively follow new inputs. Run the helper after editing. It prints the estimates in the terminal and stores them in `wordcounts.tex`; no count box appears in the PDF. If you want to print counts elsewhere, use `\AbstractWordCount` and `\MainWordCount`. When `wordcounts.tex` is absent, those macros say “Not supplied.”

## Revision diffs

Keep each submitted version in Git or a separate named folder. For a one-file manuscript:

```sh
latexdiff old.tex new.tex > changes.tex
```

For this modular template, flatten **both versions** using latexpand before running latexdiff, or use a suitable latexdiff-vc workflow. The resulting diff needs its metadata, style and figure files, and should be compiled in a separate directory. Verify math, references, floats and supplement numbering before submission. Consult Overleaf's current latexdiff guide for its build-specific workflow.

## Customization and limits

- A4 paper and 25 mm margins are defaults; modify `geometry` to match the journal.
- Use `[tbp]` floats unless placement is part of the argument. Avoid forcing all figures with `[H]`.
- Use vector PDF figures where possible; keep labels and units legible at printed size.
- Caption examples identify the evidence and explicitly distinguish illustrative curves from data.
- No source files are automatically embedded inside the PDFs.
- No shell escape is required for compilation. The optional Python word-count helper is run separately.
- The title page has no submission-details box. Journal and manuscript ID remain in the response letter.
- This is a writing template, not a replacement for the journal's submission class, accessibility requirements or data policy.

## Provenance and license

This v2.0 template develops the manuscript/supplement and reviewer-response workflow in Chuliang Song's earlier public template. It incorporates generic practices used in the current research workflow, with newly written examples rather than manuscript text or actual reviewer comments. It uses standard maintained packages rather than redistributing a journal's bibliography style.

The template source is released under the MIT license in `LICENSE`. The LaTeX packages retain their own licenses. Example bibliographic metadata describe the cited publications; they do not grant rights to those publications.

Useful documentation: [biblatex](https://ctan.org/pkg/biblatex), [lineno](https://ctan.org/pkg/lineno), [cleveref](https://ctan.org/pkg/cleveref), [Overleaf word counts](https://docs.overleaf.com/writing-and-editing/using-word-count), [Overleaf latexdiff](https://www.overleaf.com/learn/latex/Articles/How_to_use_latexdiff_on_Overleaf).

## Inline source guidance

The TeX files include comments explaining where to edit content, metadata and formatting; how review/reading modes differ; how Biber and independent bibliographies work; how to label floats and reviewer line ranges; and why supplementary counters and hyperlink anchors reset together. Comments do not appear in the PDF. Start with `metadata.tex` and `sections/`; customize `ecology.sty` only when you want to change shared formatting.
