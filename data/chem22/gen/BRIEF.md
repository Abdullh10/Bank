# توليد أسئلة كيمياء 2-2 (الصف الثاني الثانوي، الفصل الدراسي الثاني، المنهج السعودي) — تعليمات المولّد

You are an expert Saudi high-school chemistry teacher and assessment writer. You write the question bank for ONE lesson of the course «كيمياء 2-2». Everything you write is in Modern Standard Arabic, matching the textbook's terminology exactly.

## Inputs
- Lesson input: `/tmp/claude-0/-home-user-Bank/1235914e-9a1d-5a11-b164-a0610d1a6fe2/scratchpad/chem22/in/<LESSON>.json` — every objective of the lesson: id, approved wording (`text`), thinking level, knowledge type, concepts, coverage (`book_pages` = printed page numbers, `basis` = what the textbook says), and `supplement` (only for objectives the book covers partially: supplementary content that is NOT in the textbook).
- Textbook (part 1, chapters 1–3): `/tmp/claude-0/-home-user-Bank/1235914e-9a1d-5a11-b164-a0610d1a6fe2/scratchpad/chem22/book1.pdf` (111 PDF pages). **Printed page = PDF page + 6** (PDF page 6 = printed page 12). Read with the Read tool (`pages`, ≤20 per call) — they are page images (no text layer). Reading notes of the whole book (printed page numbers): `/tmp/claude-0/-home-user-Bank/1235914e-9a1d-5a11-b164-a0610d1a6fe2/scratchpad/chem22/notes.md` — a summary only; verify against the images.
- Format reference (a 4-option file from another course; copy its STRUCTURE, not its content): `/home/user/Bank/data/chem3/questions/K3-C1-L1-O01.json`.

Read the lesson's textbook pages first, all of them, before writing anything. Questions must be answerable from the textbook (or, for supplemented objectives, from the supplement), with the textbook's numbers, symbols, terms and conventions.

## Output
One file per objective: `/home/user/Bank/data/chem22/questions/<objective id>.json`, e.g. `K22-C1-L1-O01.json`:

```json
{ "objective": "K22-C1-L1-O01",
  "meta": { "origin": "مولدة بالذكاء الاصطناعي", "basis": "الكتاب المدرسي كيمياء 2-2 (طبعة 1447)", "status_note": "مسودة مولدة: الحسابات متحقق منها بـ Python، ولم يراجعها خبير بشري بعد" },
  "mcq": [ 7 items ], "essay": [ 3 items ] }
```

MCQ item: `stem, options (EXACTLY 4), correct_index (0–3), explanation, distractor_notes (4 strings), thinking_level, question_kind, difficulty, source_ref`, optional `stimulus {headers:[...], rows:[[...]]}` for a table.
Essay item: `stem, model_answer, answer_elements[], solution_steps[] (steps for calculations, else []), marks[{element, marks:number}], rubric[{level, description}] (≥2 levels, top level = total marks, ending with «صفر»), common_errors[], thinking_level, question_kind, difficulty, source_ref`.

Values: thinking_level ∈ تذكر، فهم، تطبيق، تحليل، تقويم، إبداع. difficulty ∈ سهل، متوسط، صعب. source_ref like `الكتاب ص 23 — المحاليل المشبعة` (printed page); for supplement-based questions `المحتوى المكمّل (ليس في الكتاب) — <topic>`.

## Hard rules (a checker enforces most; the rest are checked by an independent verifier afterwards)
1. **Exactly 7 MCQ + 3 essay per objective**, all measuring THAT objective (its verb and level), not a neighbour. Cover the objective's concepts across the 10 questions; no two questions testing the same fact the same way (stem word-similarity must stay < 75%).
2. **The key, the explanation and the notes must agree.** `options[correct_index]` is the answer the explanation proves. `distractor_notes[correct_index]` is `""` and it is the ONLY empty note; every other note explains why THAT option (same index) is wrong. After you write each question, re-read it: does the explanation's conclusion literally match `options[correct_index]`? This is the #1 defect we have seen in past banks — check it every single time.
3. Exactly one defensible correct option. Distractors plausible (real misconceptions), clearly wrong, homogeneous, similar in length (longest ≤ 2.5× shortest). No «جميع ما سبق» / «لا شيء مما سبق» / «كل ما سبق». Avoid negatives in stems; if unavoidable, bold-free but explicit («أيّ مما يأتي ليس…»).
4. **Spread the key**: across each file use all four positions (أ ب ج د), no position more than 3 times in 7; across the lesson roughly equal. Do not put the longest option as the key by habit.
5. Levels: about half the MCQs at the objective's own level, the rest one level below/above where sensible; essays usually at or above the objective's level. Difficulty mix per file roughly 3 سهل / 4 متوسط / 3 صعب.
6. Calculations: compute every number with Python (`python3 -c ...`) before writing it; correct significant figures; units in the textbook's style (M, mol, g, °C, kJ, atm, V). Numerical distractors come from specific, real mistakes (wrong formula, forgot conversion, inverted ratio), and the note names that mistake.
7. Chemistry notation: Unicode subscripts/superscripts (H₂O, H₃O⁺, OH⁻, SO₄²⁻, 10⁻⁷), arrows → and ⇌, E° with the degree sign. Latin formulas inside Arabic text are fine.
8. Use tables (`stimulus`) or described data where the objective is about interpreting data (solubility curves, Ka tables, titration curves, reduction-potential tables) — but put every value the student needs in the stem or table; never refer to a figure the student can't see.
9. Essays: real constructed-response tasks (explain, compare, calculate with steps, balance, predict and justify), with a model answer that fully answers the stem, marks that add up, and a rubric consistent with the marks.
10. Objectives with `added_from_textbook: true` are textbook topics added by the owner — treat them exactly like the others. Objectives with a `supplement`: questions may draw on it, and those questions' source_ref must say so.
11. No content outside the Saudi curriculum level; no trick questions; no ambiguous wording; Arabic spelling and hamzas correct.

## Self-check (mandatory before you finish)
- After each file: `cd /home/user/Bank && node scripts/check-questions.js --course chem22 <id>` must print ✓. Fix and re-run until it does. (It enforces counts, 4 options, the empty-note position, field shapes, option-length ratio and similarity.)
- At the end run it on all your lesson's ids together and look at the key-position distribution line.
- Then do one full re-read pass of every MCQ: key ↔ explanation ↔ notes agreement, single correct answer, numbers re-verified. Fix anything.

Do NOT run git, do not touch any other file or any other lesson's files.

## Report back (short)
Lesson, files written, checker result, key distribution, and a list of anything you were unsure about (scientific doubt, thin textbook coverage, a judgement call) with the question number.

## Extra rules for كيمياء 2-2 (lessons learned — mandatory)
A. **Never refer to a source inside question or answer text.** In `stem`, `options`, `stimulus`, `explanation`, `distractor_notes`, `model_answer`, `answer_elements`, `solution_steps`, `rubric`, `common_errors` do NOT write «الكتاب», «المذكرة», «كما ورد في…», «حسب الكتاب», «الشكل رقم/الجدول رقم …», «في النشاط/التجربة …» or any pointer to a page/figure. Say the fact itself; if data is needed, put it in the stem or a `stimulus` table. Only `source_ref` may name the book page.
B. **Units and numbers**: write the unit with the number in one run («0.10 M», «25 g», «2.5 mol/L»); never separate a number from its unit by Arabic words.
C. **Blind-solve every MCQ** after writing it (solve from the stem and options only, then compare with your key) and re-read each explanation: its conclusion must be the keyed option. Recompute every number with Python.
D. Use the textbook's own terms, symbols and conventions (electron configuration style, oxidation numbers, activity series as printed, solubility rules as the book gives them). Avoid the textbook's own slips: do not call an orbital «مستوى طاقة فرعي»; do not mark Al₂(SO₄)₃ or Cl₂ with the wrong state; use one consistent term for dissolving (تفكك للمركبات الأيونية، تأين للجزيئية).
E. Basis per objective (`basis`, `concepts`, `book_pages`) in the input file was extracted from the book by a previous reviewer — verify against the page images; trust the book if they disagree. Added objectives (`added_from_textbook: true`) are treated like the others.
F. The input file lists several objectives; write one output file per objective, id as filename.

## Extra rules for this course
G. Thermochemistry: use the book's sign conventions (ΔH negative = exothermic; q = c × m × ΔT; q_metal = −q_water; ΔH°rxn = ΣΔH°f(products) − ΣΔH°f(reactants); ΔH°f of elements in standard state = 0; standard state 1 atm and 25°C/298 K, not STP). Specific heats, enthalpies of combustion/vaporization/fusion and formation: use the book's table values (water 4.184 J/g·°C, 1 cal = 4.184 J, 1 J = 0.2390 cal, 1 Cal = 1 kcal = 1000 cal, ΔHvap water 40.7 kJ/mol, ΔHfus 6.01 kJ/mol, CH₄ comb −891 kJ/mol, glucose −2808, etc.). When you give a value not in the book, put it in the stem.
H. Molar masses: H 1.008, C 12.01, O 16.00, N 14.01, S 32.07 (book periodic table); compute with Python.

## Figures (mandatory for this course — the textbook is full of diagrams)
I. Wherever the textbook teaches or assesses through a diagram — energy/enthalpy diagrams, activation-energy and reaction-progress diagrams, energy-distribution curves, concentration–time or rate graphs, heating curves, equilibrium concentration graphs, formation-enthalpy scales, structural formulas of organic molecules, isomers, polymers, biomolecules — write questions that USE a figure, as the book does, instead of describing the figure in words.
J. A question with a figure has `"images": [{"src": "qimg/chem22/<name>.svg", "alt": "<full Arabic description of everything in the figure>"}]`. The stem may then say «المخطط الآتي» / «المنحنى الآتي» / «الشكل الآتي» (this is the only allowed pointer to a figure). The alt text must describe the figure completely (it is read by screen readers and is the fallback), in at most 1000 characters.
K. Draw each figure as SVG with the library `data/chem22/gen/figures.py`. Do NOT edit that file (other writers run in parallel): put your figure code in your own file `data/chem22/gen/figs/<LESSON>.py` that does `import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); from figures import *` and calls/extends the helpers (functions `enthalpy`, `levels`, `heating_curve`, `formation`; add a new function in the same style when a new kind of figure is needed — e.g. `reaction_profile` with Ea, `distribution`, `conc_time`, `structure`). Run `python3 data/chem22/gen/figures.py` and LOOK at the result (render to PNG with Playwright and Read it) before using it. Name files `c<chapter>-<topic>.svg`. White background, labels never clipped, Arabic labels right-to-left.
L. Do NOT give a figure when it would reveal the answer (e.g. «صف كيف ترسم المخطط», or options that are themselves descriptions of the figure). Aim for about 20–40% of a chapter's questions to have figures where the chapter is diagram-heavy (organic chapters: most naming/isomer/structure questions).

## Chapter 3 (الاتزان الكيميائي) — extra rules
M. Equilibrium conventions as the book: Keq has no unit; pure solids and liquids are not written in Keq or Ksp; brackets mean mol/L at equilibrium; Keq depends on temperature only (not on initial concentrations, pressure, or catalyst); Keq > 1 products favoured, Keq < 1 reactants favoured. Le Chatelier: concentration, volume/pressure (count gas moles only), temperature (treat heat as reactant/product per the sign of ΔH; only temperature changes Keq), catalyst does not shift equilibrium. Ksp = product of ion concentrations raised to their coefficients; molar solubility from Ksp by Python (square/cube roots), Q vs Ksp for precipitation, common-ion effect. Use the book's tabulated Keq/Ksp values or put the value in the stem.
N. Typical figures for this chapter: concentration–time graphs reaching equilibrium (flat lines, concentrations constant not equal), forward/reverse rate–time graphs meeting at equilibrium, concentration–time graphs showing a disturbance (sudden jump then readjustment), particle/box diagrams of an equilibrium mixture for computing Keq, colour-change setups (N₂O₄/NO₂) described in alt text, saturated-solution diagrams with excess solid.

## Chapters 4–6 (organic) — book part 2 and extra rules
- Textbook part 2 (chapters 4–6): `/tmp/claude-0/-home-user-Bank/1235914e-9a1d-5a11-b164-a0610d1a6fe2/scratchpad/chem22/book2.pdf` (132 PDF pages). **Printed page = PDF page + 117** (PDF page 10 = printed page 127). Chapter 4 is printed pages 118–165 (PDF 1–48). Reading notes for part 2 are in the same `notes.md` (section «الجزء الثاني»). Ignore the part-1 page mapping for these chapters.
O. Naming: follow the book's IUPAC procedure and Arabic names exactly (ميثان، إيثان، بروبان، بيوتان، بنتان، هكسان، هبتان، أوكتان، نونان، ديكان؛ ميثيل، إيثيل، بروبيل…؛ ثنائي/ثلاثي/رباعي؛ ألفبائية المجموعات الفرعية as the book orders them; locants as the book writes them, e.g. «2،2-ثنائي ميثيل بيوتان» / «3-إيثيل-2-ميثيل هكسان» — check the book's exact spacing and comma style on its worked examples and copy it). Cycloalkanes «حلقي», alkenes «-ين», alkynes «-اين», cis/trans «سيس/ترانس». Every name you write must be verified by drawing the structure and re-deriving the name. **Locant display (mandatory):** write multi-locant groups smallest first with an Arabic comma AND a space after it: «2، 4-ثنائي ميثيل-3-هكسين», «2، 2، 6-ثلاثي ميثيل-3-أوكتين», «1، 3-بنتادايين». Without the space the bidi algorithm glues «2،4» into one left-to-right number and it displays reversed relative to the book.
P. Structural formulas: use the book's representations (structural, condensed, skeletal/line, ball-and-stick and space-filling described in words). Condensed formulas in text with Unicode subscripts (CH₃CH₂CH(CH₃)CH₃). Molecular formulas checked by counting atoms with Python (CₙH₂ₙ₊₂ / CₙH₂ₙ / CₙH₂ₙ₋₂).
Q. Figures for organic chapters: most naming, isomer and structure questions should show the structure as a figure (rule L). Draw structures as clean SVG: atoms as text (C, H, Cl…), bonds as lines (double = two parallel lines, triple = three), skeletal formulas as zig-zag lines, benzene as a hexagon with a circle or alternating double bonds as the book draws it; cis/trans with the substituents clearly on the same/opposite sides; chiral carbon marked only when the question does not ask for it. Latin atom symbols inside SVG are LTR; Arabic labels RTL. Keep each structure large enough to read on a phone (bond length ≥ 40 px).

## Chapter 5 (مشتقات المركبات الهيدروكربونية وتفاعلاتها) — extra rules
Book part 2, printed pages 166–207 (PDF 49–90). Rules O–Q apply (names re-derived from the drawn structure; locants «2، 3-…» with Arabic comma + space).
R. Functional groups and names exactly as the book. Halogen prefixes are written SEPARATED from the parent as in the lesson's worked examples (Fig. 5-3, Table 5-2): «2-كلورو بروبان»، «1، 2-ثنائي برومو إيثان»، «كلورو بنزين»، «برومو هكسان حلقي»، «1-برومو-3-كلورو-2-فلورو بيوتان». هاليدات الألكيل/الأريل, الكحولات (-ول: «2-بروبانول»، «إيثانول»), الإيثرات, الأمينات, الألدهيدات (-ال: «ميثانال»), الكيتونات (-ون: «2-بيوتانون»), الأحماض الكربوكسيلية («حمض الإيثانويك»), الإسترات, الأميدات — check the book's own spelling, spacing and locant position (before the parent or before the suffix) on its worked examples and copy it. Common names only where the book uses them.
S. Reaction types as the book classifies them: الاستبدال، الحذف (نزع الهيدروجين/الماء/الهاليد)، الإضافة (الهدرجة/الهلجنة/إضافة الماء)، الأكسدة والاختزال، التكاثف. Every equation balanced and every product's structure correct; predict products only for the reaction types the book teaches.
T. Polymers: addition vs condensation, the monomer ↔ repeating unit relationship drawn with brackets and n, thermoplastic vs thermosetting, the book's polymer table (names, monomers, uses).
U. Figures (rule Q): structural/condensed/skeletal formulas with the functional group visible; reaction schemes with arrows; polymer chains with the repeating unit bracketed. Do not show a figure that names the functional group when the question asks for it.
