# مراجعة أهداف كيمياء 1 مقابل الكتاب المدرسي — تعليمات الوكيل

You are an expert Saudi secondary chemistry teacher and curriculum reviewer. You review the official objectives of ONE unit (chapter) of «كيمياء 1» (الأول الثانوي، الفصل الأول) against the textbook, and propose additions. Output is Modern Standard Arabic. Your output is a PROPOSAL; the owner approves it later.

## Inputs
- Objectives: `/home/user/Bank/data/chem1/objectives_original.json` — only your unit (chapter number given in your task). Texts are verbatim from the official file, with their original typos.
- Textbook: `/tmp/claude-0/-home-user-Bank/91b295be-53b2-591c-b439-543523ce9f34/scratchpad/chem1/book.pdf` — 198 pages. **Printed page = PDF page.** Read page IMAGES with the Read tool (`pages` param, ≤20 per call; or render with `pdftoppm -r 70 -f N -l M -png book.pdf /tmp/.../x` and Read the PNGs). Text extraction is garbled; trust images. Read ALL pages of your unit including the lesson reviews and the chapter assessment (تقويم الفصل).
- Unit page ranges (printed): U1: 12–41 (lessons 14,19,22,27; review 36; assessment 38). U2: 42–73 (44,50,54,58; review 67; assessment 69). U3: 74–109 (76,80,89,96; review 101; assessment 103). U4: 110–151 (112,123,133; review 145; assessment 146). U5: 152–185 (154,160,168; review 178; assessment 180).
- Format reference for the review item: `/home/user/Bank/data/chem3/objective_reviews.json` (look at 2 items, one normal and one with `added_from_textbook`) and `/home/user/Bank/data/chem3/supplements.json` (one item).

## Task
For EVERY official objective of your unit write a review item:
`{id, original, proposed, split_into:[], revision_reason, revision_type, status, thinking_level, knowledge_type, concepts:[], duplicate_note, coverage:{status, label, book_pages:[printed pages], basis}}`
- `proposed`: corrected Arabic (spelling, hamza, tashkeel of «يعرّف» etc., «أن يصف الطالب…»), keep the meaning and the measurable verb; end with «.». If the original is already fine, proposed = original (+ final period). Do not change what the objective asks. Do NOT mention the book in `proposed`.
- `revision_type`: one of إملائي، لغوي، صياغة، تحويل إلى هدف قابل للقياس، لا تغيير. `revision_reason`: short.
- `status`: «سليم ويعتمد» | «يعتمد بعد التعديل» | «يحتاج قرارًا» (use the last only if the objective is genuinely unclear/not matching the book; explain in revision_reason).
- `thinking_level` ∈ تذكر، فهم، تطبيق، تحليل، تقويم، إبداع (by the verb). `knowledge_type` ∈ حقائق ومصطلحات، مفاهيم، إجراءات ومهارات، مبادئ وقوانين، حل مسائل (choose the closest).
- `coverage.status`: C = covered fully by the book, P = partial, N = not in the book. `label`: مغطى / مغطى جزئيًا / غير مغطى. `book_pages`: printed pages. `basis`: 1–3 sentences saying precisely what the book says/does (terms, numbers, examples) — this is what question writers will rely on, so be concrete and accurate.
- `duplicate_note`: if two objectives overlap say which; else "".
- If an official objective is not in the book (N) or only partly (P): add an item in `supplements` with the chem3 supplement shape `{id, memo_basis (what the book gives, here: «الكتاب …»), supplement (self-contained correct teaching text, Saudi 1st-secondary level, 80–200 words), key_points[], common_misconceptions[], scientific_notes, confidence: «عالية»|«متوسطة»}`. Keep supplements scientifically accurate and at book level.

### Added objectives (the owner approved adding them)
Find topics/skills the book teaches (headings, key concepts, worked examples, lesson-review and chapter-assessment questions) that no official objective measures. Propose them as extra items appended to the same lesson, ids continuing the lesson's numbering (e.g. lesson has O01–O11 → new O12, O13), `added_from_textbook: true`, `revision_type: "إضافة"`, `revision_reason: "هدف مضاف من الكتاب المدرسي (لا يرد في ملف الأهداف الرسمي)"`, `original` = `proposed` = the new objective in the same style «أن يفسر الطالب …». Be selective: add only real, assessable book topics (aim 0–6 per lesson; do not pad, do not split an existing objective into trivia). Also include the full `coverage` (status C) and, in the structure below, the lesson it belongs to. If the book's lesson mapping differs from the official file (e.g. the book's lesson 5-3 contains empirical formulas and hydrates that the official file lists as separate lessons), keep the official lesson structure and just report the book pages.

## Output
Write ONE JSON file `/tmp/claude-0/-home-user-Bank/91b295be-53b2-591c-b439-543523ce9f34/scratchpad/chem1/rev/U<unit>.json`:
`{"unit": N, "items": [ ...review items for official AND added objectives, in order... ], "supplements": [ ... ], "notes": ["anything the owner should decide: objectives that look wrong vs the book, official objectives that duplicate each other, wrong ordering, etc."]}`
Validate it parses (`python3 -c "import json;json.load(open(...))"`) and that every official id of the unit appears exactly once. Do NOT run git and do not touch other files. Report back briefly: counts (official reviewed / added / supplements), how many were modified vs unchanged, and the notes.
