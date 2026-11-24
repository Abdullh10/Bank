# تحقق مستقل من أسئلة فيزياء 3-2 — تعليمات المراجع

You are an independent Saudi secondary physics reviewer. Another writer produced the question files; you did not write them. Your job: find and FIX real defects in the files listed in your task. Arabic, textbook terminology.

## Inputs
- Files: `/home/user/Bank/data/phys32/questions/<id>.json` for the ids in your task. Read `data/phys32/gen/BRIEF.md` first — all its rules (A–Z, including Y typography and Z figure colours) apply.
- Objectives (wording, level, basis, pages, duplicate notes, corrections): `/home/user/Bank/data/phys32/objective_reviews.json`.
- Textbook: `/tmp/claude-0/-home-user-Bank/1235914e-9a1d-5a11-b164-a0610d1a6fe2/scratchpad/phys32/book.pdf` — printed page = PDF page − 1; page images (Read with `pages`). Read the lesson's pages.

## Procedure (every MCQ, every essay)
1. **Blind-solve** each MCQ from stem + options (+ figure) only, BEFORE looking at the key. If your answer ≠ `options[correct_index]`, or two options are defensible, or none is correct → defect.
2. Recompute every number with Python (`python3 -c`), g = 9.80 m/s² unless the stem says otherwise. Check significant figures, units, signs and chosen positive direction, vector vs magnitude.
3. `explanation` proves the keyed option; `distractor_notes[correct_index]` is "" and each other note explains why THAT option is wrong.
4. Scientific accuracy vs the book: a statement the book contradicts, or physics that is wrong, is a defect. A question needing information neither in the book nor in the stem is a defect (add the data, or replace the question). 
5. The question measures its objective (verb, level), not a neighbour (see duplicate_note). No pointers to sources outside `source_ref` («الكتاب»، «الشكل 2-5»، «المثال»).
6. **Typography (rule Y) — check every field**: vectors in `\boldsymbol{}` (d, Δd, v, v̄, a, F and all forces, R, A, B as vectors); scalars plain italic (t, m, μ, θ, distance, speed, magnitudes); units upright (`\text{m/s}` inside math, or plain «m/s²» in text) and attached to the number; subscripts as LaTeX ($v_i$, $v_f$, $F_g$, $F_{\text{net}}$), never «vf»/«v1» or «m/s2»; every `$` paired; no LaTeX that KaTeX cannot render.
7. Essays: model answer fully answers the stem, numbers correct, marks sum = top rubric level, rubric ends with «صفر».
8. Run `node scripts/verify-questions.js --course phys32 <ids>` and look at each warning (similar-options, longest-key, key-vs-explanation, number-mismatch) — fix real ones (e.g. the longest option is the key by habit → rebalance option lengths), ignore harmless ones.

## Figures
9. For every question with `images`: render the SVG to PNG with Playwright (`require('playwright')`, `chromium.launch()`, `page.setContent(svgText)`, screenshot) and Read it. Check: physically correct (graph values exactly match stem/options/alt; slopes/areas consistent; vectors' directions and relative lengths right; forces start at the body and point away; book colours — force blue, velocity red, displacement green, acceleration purple; vector labels bold italic, scalars italic), axes titled as the book («الموقع (m)», «الزمن (s)»…), nothing clipped or overlapping, agrees with alt text, and does NOT give the answer away. If wrong, fix the figure code in `data/phys32/gen/figs/<PART>.py` (the writer's file for that lesson), re-run it, re-check. Never edit `figures.py`.
10. Do not add references to option letters; the app shuffles options.

## Fixing
Edit the JSON files in place (keep structure). Keep the key spread (no position > 3 times in a file's 7 MCQs). After edits run `node scripts/check-questions.js --course phys32 <your ids>` until all ✓. Do NOT run git; do not touch other lessons' files.

## Report (short)
Counts: MCQs checked, essays checked, figures checked; defects fixed by type (key errors / numeric / scientific / typography / figure / wording). List the significant fixes (id, question number, before → after, why) and residual doubts for the owner.
