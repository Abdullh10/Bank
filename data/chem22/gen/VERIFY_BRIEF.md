# تحقق مستقل من أسئلة كيمياء 2-2 — تعليمات المراجع

You are an independent Saudi secondary chemistry reviewer. Another writer produced the question files; you did not write them. Your job: find and FIX real defects in the files of ONE lesson. Arabic, textbook terminology.

## Inputs
- Files: `/home/user/Bank/data/chem22/questions/<id>.json` for the ids listed in your task. Format: see `data/chem22/gen/BRIEF.md` (same rules apply — read it first).
- Objectives (wording, level, basis, pages): `/home/user/Bank/data/chem22/objective_reviews.json`.
- Textbook part 1: `/tmp/claude-0/-home-user-Bank/1235914e-9a1d-5a11-b164-a0610d1a6fe2/scratchpad/chem22/book1.pdf` — printed page = PDF page + 6; page images (Read with `pages`). Notes: `.../scratchpad/chem22/notes.md`.

## Procedure (every MCQ, every essay)
1. **Blind-solve** each MCQ from stem + options only, BEFORE looking at the key. If your answer ≠ `options[correct_index]`, or two options are defensible, or none is correct → defect.
2. Recompute every number with Python (`python3 -c`), with the book's data (c water 4.184 J/g·°C, 1 cal = 4.184 J, ΔHvap 40.7, ΔHfus 6.01, molar masses H 1.008 C 12.01 O 16.00 N 14.01 S 32.07). Check significant figures, units, signs (ΔH, q_metal = −q_water).
3. Check `explanation` proves the keyed option, `distractor_notes[correct_index]` is "" and each other note explains why THAT option is wrong.
4. Scientific accuracy vs the book: a statement the book contradicts, or chemistry that is wrong, is a defect. A question that needs information neither in the book nor in the stem is a defect (add the data to the stem, or replace the question).
5. The question must measure its objective. Remove pointers to sources outside `source_ref` («الكتاب»، «الشكل»، «الجدول»).
6. Essays: model answer fully answers the stem, numbers correct, marks sum = top rubric level.
7. Heuristic warnings from `node scripts/verify-questions.js --course chem22 <ids>` (similar-options, longest-key, key-vs-explanation, number-mismatch) — look at each; fix if real (e.g. longest option is the key by habit → rebalance), ignore if harmless (numeric options naturally look alike).

## Fixing
Edit the JSON files in place (keep structure). Keep the key-position spread (no position > 3 in a file). After edits run `node scripts/check-questions.js --course chem22 <your ids>` until all ✓. Do NOT run git, do not touch other lessons' files.

## Report (short)
Per file: defects found and what you changed (question number, before → after, why). Then a list of residual doubts for the owner. Give counts: MCQs checked, defects fixed (key errors / numeric errors / scientific / wording).
