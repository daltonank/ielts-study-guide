#!/usr/bin/env python3
"""Build the G4 Writing Task 1 curriculum into web/writing1_data.js.

Pipeline shape follows scripts/build_reading_curriculum.py (see
docs/development_design_plan.md sections 3-4): structured Python data in this
file is assembled into window.WRITING1_DATA, and tests/g4_writing1_validation.py
re-parses the emitted artifact and re-derives every check from the
specification rather than from this generator's intent.

Benchmarks (PROJECT_CHARTER.md section 9 / CURRICULUM_SPEC.md section 6):
  7 visual families, >=60 micro-exercises, >=20 full timed prompts.

All visuals and datasets are original to this product. No commercial IELTS
material is reproduced (PROJECT_CHARTER.md section 4.8).
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "web" / "writing1_data.js"

SKILL = "Writing Task 1"

# ---------------------------------------------------------------------------
# Error taxonomy (CLAUDE.md section 15). A wrong answer is classified into one
# of these so Task 1 errors flow into the same error-log / review-queue shape
# Reading already uses.
# ---------------------------------------------------------------------------
ERROR_TAXONOMY = [
    {
        "id": "data_misreading",
        "en": "Data misreading",
        "ua": "Неправильне зчитування даних",
        "description": "The statement does not match the figure actually shown: a value, a year, a unit or a category has been read incorrectly.",
        "correction": "Point at the exact data point before writing the sentence, then re-check the axis label and the unit.",
        "uaCorrection": "Спершу знайдіть конкретну точку даних, потім перевірте підпис осі та одиницю виміру.",
    },
    {
        "id": "invalid_comparison",
        "en": "Invalid or unsupported comparison",
        "ua": "Некоректне порівняння",
        "description": "The comparison is not supported by the visual: different units, different periods, or a relationship the data does not establish.",
        "correction": "Compare like with like: same unit, same point in time, same level of category.",
        "uaCorrection": "Порівнюйте однорідне з однорідним: та сама одиниця, той самий момент часу, той самий рівень категорії.",
    },
    {
        "id": "missing_overview",
        "en": "Missing or weak overview",
        "ua": "Відсутній або слабкий overview",
        "description": "No overview paragraph, or an overview that repeats individual figures instead of stating the largest general patterns.",
        "correction": "State two or three of the biggest patterns without figures; detail belongs in the body paragraphs.",
        "uaCorrection": "Сформулюйте дві-три найбільші загальні тенденції без цифр; конкретні дані — у body-абзацах.",
    },
    {
        "id": "list_like_description",
        "en": "List-like description without synthesis",
        "ua": "Перелік без узагальнення",
        "description": "Every category is described one after another with no grouping, contrast or ranking.",
        "correction": "Group categories that behave alike and contrast them with the ones that behave differently.",
        "uaCorrection": "Об'єднуйте категорії зі схожою поведінкою і протиставляйте їх тим, що поводяться інакше.",
    },
    {
        "id": "tense_misuse",
        "en": "Tense misuse",
        "ua": "Неправильний вибір часу",
        "description": "The tense does not match the timeframe of the visual, or shifts without reason.",
        "correction": "Past data takes past tenses; a timeless process takes present simple; projections take future or modal forms.",
        "uaCorrection": "Минулі дані — минулі часи; позачасовий процес — present simple; прогнози — майбутні або модальні форми.",
    },
    {
        "id": "unsupported_causal_claim",
        "en": "Unsupported causal claim",
        "ua": "Необґрунтоване твердження про причину",
        "description": "The response explains why something happened when the visual only shows that it happened.",
        "correction": "Describe the pattern; do not supply a reason the graphic cannot evidence.",
        "uaCorrection": "Описуйте закономірність, а не причину, якої графік не підтверджує.",
    },
    {
        "id": "personal_opinion",
        "en": "Personal opinion in Task 1",
        "ua": "Особиста думка в Task 1",
        "description": "The response evaluates, recommends or reacts instead of reporting the data.",
        "correction": "Task 1 reports; it does not judge, advise or predict beyond the graphic.",
        "uaCorrection": "Task 1 — це звіт: без оцінок, порад і прогнозів поза межами графіка.",
    },
    {
        "id": "imprecise_quantity",
        "en": "Imprecise quantity language",
        "ua": "Неточна мова кількості",
        "description": "The approximation, proportion word or quantifier misstates the size of the figure.",
        "correction": "Match the word to the number: just over, roughly, nearly, a fifth, a marginal rise.",
        "uaCorrection": "Підбирайте слово під число: just over, roughly, nearly, a fifth, a marginal rise.",
    },
    {
        "id": "paragraph_organisation",
        "en": "Poor paragraph organisation",
        "ua": "Слабка структура абзаців",
        "description": "Introduction, overview and body are missing, merged, or ordered so the reader cannot follow the report.",
        "correction": "Use a paraphrased task statement, then the overview, then two grouped body paragraphs.",
        "uaCorrection": "Перефразоване завдання, далі overview, далі два згруповані body-абзаци.",
    },
    {
        "id": "timing_failure",
        "en": "Timing failure",
        "ua": "Проблема з часом",
        "description": "The response was not planned and completed inside the 20 minutes Task 1 allows.",
        "correction": "Spend about 3 minutes planning, 15 writing and 2 checking.",
        "uaCorrection": "Приблизно 3 хвилини на план, 15 на письмо, 2 на перевірку.",
    },
    {
        "id": "article_preposition_transfer",
        "en": "Article or preposition transfer error",
        "ua": "Помилка з артиклем або прийменником",
        "description": "A first-language pattern produces a missing article, an extra article, or the wrong data preposition.",
        "correction": "Ukrainian has no articles, so check every countable singular noun, and learn the fixed data prepositions.",
        "uaCorrection": "В українській немає артиклів, тому перевіряйте кожен злічуваний іменник в однині; вивчіть сталі прийменники для даних.",
    },
    {
        "id": "lexical_distortion",
        "en": "Lexical variation that distorts the data",
        "ua": "Синонім, що спотворює дані",
        "description": "A synonym or paraphrase changes the magnitude, direction or certainty of the original figure.",
        "correction": "Vary the wording, never the value; check the paraphrase against the number before keeping it.",
        "uaCorrection": "Змінюйте формулювання, а не значення; звіряйте перефразування з числом.",
    },
]

ERROR_IDS = {e["id"] for e in ERROR_TAXONOMY}

# ---------------------------------------------------------------------------
# Micro-exercise types (CURRICULUM_SPEC.md section 6 "Exercise types").
# Every visual family carries exactly one exercise of each type, so family
# coverage is a set equality rather than a count.
# ---------------------------------------------------------------------------
MICRO_TYPES = [
    {"id": "feature_selection", "label": "Key-feature selection",
     "ua": "Вибір ключової ознаки",
     "focus": "Decide which detail is significant enough to report and which is noise.",
     "interaction": "select", "mode": "guided", "minutes": 3},
    {"id": "overview_selection", "label": "Overview selection",
     "ua": "Вибір overview",
     "focus": "Recognise an overview that states the largest patterns without listing figures.",
     "interaction": "select", "mode": "guided", "minutes": 3},
    {"id": "grouping", "label": "Grouping",
     "ua": "Групування",
     "focus": "Organise categories by shared behaviour instead of describing each in turn.",
     "interaction": "select", "mode": "guided", "minutes": 3},
    {"id": "trend_language", "label": "Trend-language choice",
     "ua": "Вибір мови тенденцій",
     "focus": "Match the verb, adverb and noun phrase to the actual shape and size of the movement.",
     "interaction": "select", "mode": "guided", "minutes": 3},
    {"id": "comparison_building", "label": "Comparison building",
     "ua": "Побудова порівняння",
     "focus": "Build a valid comparative statement from two supported data points.",
     "interaction": "select", "mode": "independent", "minutes": 4},
    {"id": "data_to_sentence", "label": "Data-to-sentence transformation",
     "ua": "Дані в речення",
     "focus": "Turn a data point into an accurate academic sentence with the right quantity language.",
     "interaction": "cloze", "mode": "independent", "minutes": 4},
    {"id": "paraphrase_no_distortion", "label": "Paraphrase without numerical distortion",
     "ua": "Перефразування без спотворення",
     "focus": "Re-word a statement while preserving magnitude, direction and certainty exactly.",
     "interaction": "select", "mode": "independent", "minutes": 4},
    {"id": "sentence_correction", "label": "Sentence correction",
     "ua": "Виправлення речення",
     "focus": "Find the reporting fault (a distortion, an opinion, an unsupported cause) and repair it.",
     "interaction": "select", "mode": "timed", "minutes": 4},
    {"id": "grammar_correction", "label": "Grammar correction",
     "ua": "Виправлення граматики",
     "focus": "Repair the article, preposition, tense or agreement error a Ukrainian speaker most often makes here.",
     "interaction": "cloze", "mode": "timed", "minutes": 4},
    {"id": "paragraph_ordering", "label": "Paragraph ordering",
     "ua": "Впорядкування абзаців",
     "focus": "Assemble introduction, overview and grouped body paragraphs into a coherent report.",
     "interaction": "order", "mode": "mastery", "minutes": 5},
]

MICRO_TYPE_IDS = [t["id"] for t in MICRO_TYPES]
MICRO_TYPE_BY_ID = {t["id"]: t for t in MICRO_TYPES}

MODE_LABELS = {
    "guided": "Guided",
    "independent": "Independent",
    "timed": "Timed",
    "mastery": "Mastery check",
}

FAMILY_ORDER = [
    "line_graph",
    "bar_chart",
    "pie_chart",
    "table",
    "process_diagram",
    "map_plan",
    "mixed_visual",
]

# ---------------------------------------------------------------------------
# Family metadata (CLAUDE.md section 14: what the visual tests, how IELTS
# constructs it, a strategy, common errors, a worked example, and the language
# the family actually needs). This is the instruction layer the module list and
# each family page render from.
# ---------------------------------------------------------------------------
FAMILY_META = {
    "line_graph": {
        "title": "Line graphs",
        "ua": "Лінійні графіки",
        "skill": "Describing change over time",
        "difficulty": "7",
        "whatItTests": "Whether you can read movement across time rather than isolated points, and whether you can say how fast, how far and in what shape a line moved.",
        "howIeltsConstructs": "Two to four lines over a dated horizontal axis, usually with at least one line that crosses another, one that reverses direction, and one that stays flat. The crossing point and the reversal are the features the examiner expects you to notice.",
        "strategy": [
            "Read the title, the axis labels and the unit before looking at any line.",
            "Fix the timeframe, because it decides your tense for the whole report.",
            "For each line, mark only three things: where it starts, where it ends, and its most extreme point.",
            "Look for the shape events: a crossover, a peak, a trough, a plateau, a reversal.",
            "Group the lines that behave alike, and set them against the ones that do not.",
            "Write the overview from the grouping, not from the individual numbers.",
        ],
        "trap": "Describing every year of every line in sequence. A line graph with four lines and seven years does not need twenty-eight sentences; it needs two groups and the points where the pattern breaks.",
        "commonErrors": [
            {"errorId": "list_like_description", "symptom": "A sentence for each year in order: 'In 2005 it was 20. In 2010 it was 24. In 2015 it was 29.'", "repair": "Collapse a steady run into one movement sentence with its start and end figures, then spend the words you saved on the point where the pattern changes."},
            {"errorId": "imprecise_quantity", "symptom": "'Numbers increased dramatically' for a rise of two percentage points.", "repair": "Size the adverb to the movement: marginally, gradually, steadily, sharply, dramatically."},
            {"errorId": "tense_misuse", "symptom": "Present simple used for a graph that ends in a past year.", "repair": "A dated past range takes past simple throughout; only a projection past today takes a future or modal form."},
            {"errorId": "unsupported_causal_claim", "symptom": "'The figure fell because of the economic crisis.' The graph shows the fall, not the crisis.", "repair": "Report the fall and stop. If you want a linking idea, link two data patterns to each other, not to an outside cause."},
        ],
        "workedExample": {
            "taskStatement": "The line graph below shows the percentage of household waste recycled in three cities between 2005 and 2025.",
            "planNotes": "All three rise. Group A: Oslo and Bergen, close together, steady. Group B: Tromso, starts lowest, ends highest, overtakes both around 2015. Overview = universal rise + the overtaking.",
            "modelSentence": "Although recycling rates climbed in all three cities, Tromso rose far more steeply than the other two, overtaking Bergen in around 2015 and finishing as the highest performer.",
            "analysis": "One sentence carries the shared pattern (all rose), the contrast (far more steeply), the shape event (overtaking) and the end state (highest). No individual figure is spent, because those belong in the body paragraphs.",
        },
        "languageBank": {
            "Movement up": ["rose", "climbed", "increased", "grew", "surged"],
            "Movement down": ["fell", "declined", "dropped", "decreased", "slid"],
            "Size of movement": ["marginally", "slightly", "gradually", "steadily", "sharply", "dramatically"],
            "Shape events": ["peaked at", "bottomed out at", "levelled off at", "plateaued", "overtook", "converged"],
            "Prepositions": ["rose to 40%", "rose by 12 points", "rose from 28% to 40%", "a rise of 12 points", "between 2005 and 2025"],
        },
        "tenseRule": "A dated past range takes past simple. Use past perfect only to show that one movement finished before another began.",
        "uaTransferNote": "В українській немає артиклів, тому 'the graph', 'the period', 'the highest figure' часто втрачають артикль. Також розрізняйте 'rise to' (кінцеве значення) і 'rise by' (величина зміни) — українське 'зросло на' відповідає саме 'by'.",
        "uaSupport": "Лінійний графік перевіряє не вміння читати числа, а вміння бачити форму руху: де лінії перетинаються, де змінюють напрям, де вирівнюються. Спочатку згрупуйте лінії за поведінкою, і лише потім беріть конкретні цифри.",
    },
    "bar_chart": {
        "title": "Bar charts",
        "ua": "Стовпчикові діаграми",
        "skill": "Comparing quantities across categories",
        "difficulty": "7",
        "whatItTests": "Whether you can rank and group categories rather than read each bar aloud, and whether you can hold a comparison steady across two variables at once.",
        "howIeltsConstructs": "Either one set of bars to be ranked, or grouped bars where each category is split by a second variable such as year, age band or country. Grouped bars are built so that the ranking is not the same in every group, and that inconsistency is the feature worth reporting.",
        "strategy": [
            "Identify the two variables: what the bars are, and what splits them.",
            "Rank the categories at the top level first: highest, lowest, and anything close enough to be a tie.",
            "Check whether the ranking holds inside every group, or whether it flips somewhere.",
            "Find the widest gap and the narrowest gap; both are reportable features.",
            "Group the categories that share a profile so the body paragraphs write themselves.",
            "Write the overview from the ranking and the exception to it.",
        ],
        "trap": "Reading the chart bar by bar in the order it is drawn. Drawing order is not importance order, and a report that follows it produces a list with no comparison in it.",
        "commonErrors": [
            {"errorId": "list_like_description", "symptom": "Six sentences, one per bar, in left-to-right order.", "repair": "Rank first, then write about the top group and the bottom group in two sentences."},
            {"errorId": "invalid_comparison", "symptom": "Comparing a figure from one age group with a figure from a different category in another group.", "repair": "Hold one variable fixed while you compare across the other; say which one you fixed."},
            {"errorId": "imprecise_quantity", "symptom": "'Twice as much' when one bar is 30 and the other is 22.", "repair": "Check the ratio before you write it, or switch to a safer phrase such as 'noticeably higher than'."},
            {"errorId": "missing_overview", "symptom": "An overview that names each category and its value.", "repair": "The overview should say who leads, who trails, and whether the pattern is consistent, with no figures at all."},
        ],
        "workedExample": {
            "taskStatement": "The bar chart below shows average weekly spending on four leisure categories by three age groups.",
            "planNotes": "Eating out leads for every group. Live events lowest for the oldest group but not the youngest. Group A: categories that fall with age. Group B: categories that rise with age. Overview = eating out dominant everywhere + age reverses the ranking of the rest.",
            "modelSentence": "Eating out attracted the highest weekly spending in all three age groups, but the ranking of the remaining categories reversed with age, as spending on live events fell while spending on cultural visits rose.",
            "analysis": "The sentence fixes one variable (age group) to state the constant, then reports the inconsistency, which is exactly the feature a grouped bar chart is built to contain. No figure is used, because the overview carries pattern, not data.",
        },
        "languageBank": {
            "Ranking": ["the highest", "the lowest", "second only to", "ranked below", "trailed"],
            "Size of gap": ["marginally higher than", "well above", "roughly double", "a fraction of", "on a par with"],
            "Grouping": ["both X and Y", "the remaining categories", "by contrast", "whereas", "the same pattern held for"],
            "Prepositions": ["spending on leisure", "at 42 pounds", "an increase of 8 pounds", "higher than", "compared with"],
        },
        "tenseRule": "Dated bars take past simple. An undated survey chart takes present simple.",
        "uaTransferNote": "Українське 'витрати на' дає 'spending on', не 'spending for'. Також 'compared with' або 'compared to', але ніколи 'compared of'. Перед назвою категорії в однині зазвичай потрібен артикль: 'the youngest group'.",
        "uaSupport": "Стовпчикова діаграма винагороджує ранжування, а не перелік. Якщо у вас шість категорій, не пишіть шість речень: визначте лідера, аутсайдера і те місце, де порядок ламається.",
    },
    "pie_chart": {
        "title": "Pie charts",
        "ua": "Кругові діаграми",
        "skill": "Describing proportions and shares",
        "difficulty": "7",
        "whatItTests": "Whether you can talk in proportions rather than raw amounts, and whether you keep the distinction between a share of a whole and a quantity.",
        "howIeltsConstructs": "Usually two pies for the same categories at two dates, so that the interesting feature is the change in share rather than any single slice. Categories are chosen so that one slice grows sharply, one shrinks, and one barely moves.",
        "strategy": [
            "Confirm what the whole represents, and check whether the two pies share the same total.",
            "Read the largest and smallest slice in each pie before reading anything else.",
            "For each category, note the direction and size of the change in share.",
            "Separate the categories that moved sharply from the ones that were stable.",
            "Use proportion language, not amount language, unless the total is given.",
            "Write the overview from the biggest reordering of shares.",
        ],
        "trap": "Saying that a category 'increased' when only its share increased. If the underlying total is not shown, a larger slice does not prove a larger quantity.",
        "commonErrors": [
            {"errorId": "lexical_distortion", "symptom": "'Consumption doubled' when the share moved from 20% to 40% but the total is unknown.", "repair": "Write 'its share doubled' or 'it accounted for twice the proportion'. Keep the claim inside what the pie can prove."},
            {"errorId": "imprecise_quantity", "symptom": "'Almost half' used for 38%.", "repair": "Calibrate the fraction: 38% is 'just under two fifths' or 'well over a third'."},
            {"errorId": "list_like_description", "symptom": "Each slice read out with its percentage, in legend order.", "repair": "Group the risers and the fallers, and give the stable categories one shared sentence."},
            {"errorId": "missing_overview", "symptom": "Body paragraphs only, with no statement of how the composition as a whole shifted.", "repair": "State which category took over as the largest, and whether the distribution became more or less even."},
        ],
        "workedExample": {
            "taskStatement": "The pie charts below show the composition of municipal waste in one city in 2000 and 2020.",
            "planNotes": "Organic dominant in 2000, still largest in 2020 but smaller share. Plastics up sharply. Paper down. Glass and metal flat. Overview = composition became more even, plastics the big riser.",
            "modelSentence": "The composition of municipal waste became noticeably more even over the twenty-year period, as the dominance of organic material weakened and plastics claimed a substantially larger share of the total.",
            "analysis": "The sentence describes the whole distribution before any single slice, and the verbs stay inside what a pie can support: 'claimed a larger share', not 'increased', because the total tonnage is never shown.",
        },
        "languageBank": {
            "Share": ["accounted for", "represented", "made up", "constituted", "comprised"],
            "Fractions": ["a quarter", "a third", "two fifths", "just under half", "a marginal share"],
            "Change in share": ["its share rose to", "climbed from 12% to 26%", "shed nine percentage points", "remained virtually unchanged"],
            "Prepositions": ["a share of 24%", "an increase of six percentage points", "in 2020", "out of the total"],
        },
        "tenseRule": "Dated pies take past simple. Use 'percentage points' for the difference between two percentages, and 'per cent' for the share itself.",
        "uaTransferNote": "'Accounted for' не потребує прийменника після себе перед числом: 'accounted for 24%', не 'accounted for of 24%'. Українське 'складати' часто перекладають як 'to compose', але правильно 'to make up' або 'to account for'.",
        "uaSupport": "Кругова діаграма показує частку, а не кількість. Якщо загальна сума не вказана, ви не можете стверджувати, що обсяг зріс — лише що зросла частка. Це найчастіша втрата балів у цій родині.",
    },
    "table": {
        "title": "Tables",
        "ua": "Таблиці",
        "skill": "Selecting from dense data",
        "difficulty": "7.5",
        "whatItTests": "Whether you can leave data out. A table gives more numbers than a 150-word report can carry, so selection is the skill being scored.",
        "howIeltsConstructs": "Rows of categories against columns of years, countries or measures, deliberately over-supplied so that a candidate who tries to report everything runs out of time and words.",
        "strategy": [
            "Read the row headings and the column headings before any cell.",
            "Decide the direction of the story: across the columns, or down the rows.",
            "Find the extreme cells: the largest, the smallest, and the biggest change.",
            "Ignore the middle of the table unless it breaks the pattern.",
            "Group rows that move together and name the exception.",
            "Write the overview from the extremes and the exception only.",
        ],
        "trap": "Trying to mention every cell. A table with five rows and four columns holds twenty figures; a Band 7 report uses perhaps six of them.",
        "commonErrors": [
            {"errorId": "list_like_description", "symptom": "A sentence per row, each one reciting all four columns.", "repair": "Select. Report the highest, the lowest, the largest change, and anything that contradicts the pattern."},
            {"errorId": "invalid_comparison", "symptom": "Comparing a figure in a percentage column with a figure in a count column.", "repair": "Check the column unit before comparing; different units cannot be compared directly."},
            {"errorId": "data_misreading", "symptom": "Reading across the wrong row when the table is dense.", "repair": "Track with a finger or a cursor and re-verify each figure against both its row and its column heading."},
            {"errorId": "missing_overview", "symptom": "An overview that says only 'the table shows various figures'.", "repair": "Name the leader, the trailer and the direction of travel for the group as a whole."},
        ],
        "workedExample": {
            "taskStatement": "The table below shows tourist arrivals and average length of stay in five destinations in 2019 and 2023.",
            "planNotes": "Arrivals recovered everywhere except one destination. Length of stay moved the opposite way to arrivals in most cases. Overview = arrivals up, stays shorter, one destination against both trends.",
            "modelSentence": "Arrivals had recovered in four of the five destinations by 2023, yet visitors were staying for shorter periods almost everywhere, so the two measures moved in opposite directions.",
            "analysis": "The sentence reports twenty cells in one line by naming the direction of each measure and the size of the exception. No individual figure appears, and nothing outside the table is claimed.",
        },
        "languageBank": {
            "Selection": ["the most striking figure", "at the other extreme", "the only exception", "with the exception of"],
            "Cross-measure": ["while", "whereas", "by contrast", "in the same period", "moved in the opposite direction"],
            "Change": ["a rise of", "a fall of", "recovered to", "remained static at"],
            "Prepositions": ["an average of 4.2 nights", "arrivals in 2023", "a fall of 0.6 nights", "compared with 2019"],
        },
        "tenseRule": "Dated columns take past simple. Past perfect is useful for the earlier of two dated columns when you want to show sequence.",
        "uaTransferNote": "'Average' як іменник потребує 'an average of': 'an average of 4.2 nights'. Українське 'у середньому' — 'on average' (без артикля) у позиції прислівника.",
        "uaSupport": "Таблиця дає більше чисел, ніж вміщує звіт на 150 слів. Оцінюється саме вміння відкинути зайве: беріть екстремуми та винятки, решту залишайте на папері.",
    },
    "process_diagram": {
        "title": "Process diagrams",
        "ua": "Схеми процесів",
        "skill": "Sequencing stages and choosing voice",
        "difficulty": "7",
        "whatItTests": "Whether you can carry a reader through an ordered sequence with accurate stage language, correct passive voice, and no invented steps.",
        "howIeltsConstructs": "Either a linear manufacturing process with a clear start and end, or a natural cycle with no true beginning. Diagrams often contain one branch or one point where material returns to an earlier stage.",
        "strategy": [
            "Count the stages and decide whether the process is linear or cyclical.",
            "Name the input at the start and the output at the end.",
            "Decide the voice: man-made processes are usually passive, natural cycles usually active.",
            "Note any branch or return loop, because it is the feature most candidates miss.",
            "Write the overview as the number of stages plus the start and end points.",
            "Sequence the body with varied linkers, not six sentences beginning with 'Then'.",
        ],
        "trap": "Inventing detail the diagram does not show. If the diagram gives a labelled box called 'washing', do not add the temperature, the chemicals or the duration.",
        "commonErrors": [
            {"errorId": "tense_misuse", "symptom": "Past simple used for a timeless process.", "repair": "A process with no date takes present simple, typically in the passive: 'the bottles are crushed'."},
            {"errorId": "unsupported_causal_claim", "symptom": "'The glass is heated so that impurities can be removed', when the diagram only labels the stage 'heating'.", "repair": "Report the stage and its position in the sequence; do not supply purpose the diagram does not label."},
            {"errorId": "paragraph_organisation", "symptom": "One long paragraph covering every stage.", "repair": "Split the sequence into two blocks at a natural boundary and give each its own paragraph."},
            {"errorId": "missing_overview", "symptom": "Straight into stage one with no overview.", "repair": "State the number of stages, the input and the output, and whether the process is cyclical."},
        ],
        "workedExample": {
            "taskStatement": "The diagram below shows how glass bottles are recycled.",
            "planNotes": "Eight stages, linear but with a return loop from the final stage back to collection. Input = used bottles, output = new bottles. Overview = eight stages, closed loop.",
            "modelSentence": "The recycling of glass bottles is a closed loop of eight stages, beginning with the collection of used containers and ending with new bottles that re-enter the same collection system.",
            "analysis": "The overview gives the count, the input, the output and the cyclical shape without describing a single stage. The passive fits a man-made process, and present simple fits a diagram with no date on it.",
        },
        "languageBank": {
            "Sequence": ["initially", "at the first stage", "once this is complete", "the resulting material is then", "in the final stage"],
            "Passive forms": ["is collected", "are sorted", "is crushed", "having been melted", "is subsequently moulded"],
            "Cycle language": ["a closed loop", "returns to the first stage", "the cycle begins again", "re-enters"],
            "Prepositions": ["is transported to", "is separated into", "at a temperature of", "by means of"],
        },
        "tenseRule": "Present simple passive for man-made processes; present simple active for natural cycles. No dates means no past tense.",
        "uaTransferNote": "Українська часто передає процес зворотним дієсловом ('пляшки сортуються'), і це збігається з англійським пасивом — але артикль зникає: правильно 'the bottles are sorted', а не 'bottles are sorted', коли йдеться про конкретні пляшки з діаграми.",
        "uaSupport": "У схемі процесу немає дат, тому немає минулого часу. Головні ризики — вигадані деталі та шість речень поспіль, що починаються з 'Then'.",
    },
    "map_plan": {
        "title": "Maps and plans",
        "ua": "Карти та плани",
        "skill": "Describing change in space",
        "difficulty": "7.5",
        "whatItTests": "Whether you can orient a reader in space, and whether you can classify every change as an addition, a removal, a replacement or a retention.",
        "howIeltsConstructs": "Two plans of the same site at two dates, or a current plan against a proposal. The maps are drawn so that some features are added, some removed, some converted into something else, and at least one deliberately left untouched.",
        "strategy": [
            "Orient yourself first: find north, the main road, the water, or whatever anchors the site.",
            "Classify every feature as added, removed, replaced or unchanged.",
            "Note what the site was used for overall, and what it is used for now.",
            "Use compass and relative position language rather than pointing words.",
            "Group the changes by type or by area, not by the order your eye found them.",
            "Write the overview as the change in overall character, plus what survived.",
        ],
        "trap": "Writing 'here' and 'this part' instead of locating things. A reader who cannot see the map cannot follow 'it was moved to here'.",
        "commonErrors": [
            {"errorId": "paragraph_organisation", "symptom": "Changes reported in the random order the eye found them.", "repair": "Group by area (north half, south half) or by type (added, removed), and give each group a paragraph."},
            {"errorId": "tense_misuse", "symptom": "Present simple for a plan dated in the past, or past simple for a proposal.", "repair": "Dated past maps take past simple; proposals take 'will be' or 'is to be'."},
            {"errorId": "data_misreading", "symptom": "Calling a converted building a new one.", "repair": "Check whether the footprint is the same: same outline plus new label means replacement, not addition."},
            {"errorId": "missing_overview", "symptom": "A list of buildings with no statement of what the site became.", "repair": "Say how the character of the whole site changed: rural to residential, industrial to recreational."},
        ],
        "workedExample": {
            "taskStatement": "The maps below show the village of Whitmore in 1985 and in the present day.",
            "planNotes": "Farmland in the south replaced by housing. Woodland in the north retained. Small shop replaced by a supermarket on the same footprint. New road on the eastern edge. Overview = rural to residential, woodland untouched.",
            "modelSentence": "Whitmore has changed from a largely agricultural settlement into a residential one, with farmland in the south given over to housing, although the woodland along the northern boundary has been left untouched.",
            "analysis": "The overview names the change in overall character first, locates it with a compass direction, and finishes with the retained feature, which is the detail weaker responses omit entirely.",
        },
        "languageBank": {
            "Position": ["to the north of", "along the eastern boundary", "in the south-west corner", "adjacent to", "on the opposite side of"],
            "Addition": ["was constructed", "has been built", "a new X was added", "was extended to include"],
            "Removal": ["was demolished", "was cleared", "made way for", "was given over to"],
            "Retention": ["remained unchanged", "was left untouched", "survived the redevelopment", "was retained"],
        },
        "tenseRule": "Two past dates take past simple. A past date against today takes present perfect. A proposal takes 'will be' or 'is to be'.",
        "uaTransferNote": "Напрямки потребують артикля: 'in the north', 'to the east of the river'. Українське 'на півночі' без артикля переноситься помилково як 'in north'. Також 'adjacent to', а не 'adjacent with'.",
        "uaSupport": "Карта перевіряє орієнтацію в просторі. Читач не бачить зображення, тому слова 'тут' і 'ця частина' не працюють — потрібні сторони світу та відносне розташування.",
    },
    "mixed_visual": {
        "title": "Mixed and multiple visuals",
        "ua": "Комбіновані візуали",
        "skill": "Integrating two sources without doubling the report",
        "difficulty": "8",
        "whatItTests": "Whether you can relate two visuals to each other inside the same word count, rather than writing two short separate reports.",
        "howIeltsConstructs": "Two graphics of different types on one page, sharing a subject but measuring different things, so that the reportable feature is the relationship between them.",
        "strategy": [
            "Identify what each visual measures and what the two have in common.",
            "Decide which visual carries the main story and which supports it.",
            "Look for the link: does one explain the shape of the other, or contradict it?",
            "Write one overview that covers both, not one overview each.",
            "Give each visual a body paragraph, but cross-refer between them.",
            "Protect your word count: two visuals still means about 170 words, not 300.",
        ],
        "trap": "Writing two separate mini-reports with two overviews and no sentence that connects them. The connection is the feature the task was built to test.",
        "commonErrors": [
            {"errorId": "missing_overview", "symptom": "One overview per visual, or an overview that covers only the first graphic.", "repair": "Write a single overview containing the biggest pattern from each visual and the relationship between them."},
            {"errorId": "invalid_comparison", "symptom": "Comparing a percentage from the pie with an absolute figure from the line graph as if they were the same measure.", "repair": "Relate them without equating them: 'while total consumption rose, the share drawn from coal fell'."},
            {"errorId": "list_like_description", "symptom": "Everything from visual one, then everything from visual two, with no link.", "repair": "Add at least one sentence that uses both visuals in the same claim."},
            {"errorId": "timing_failure", "symptom": "Running past 20 minutes because two visuals felt like twice the work.", "repair": "Plan for four paragraphs, not eight. The word count does not double."},
        ],
        "workedExample": {
            "taskStatement": "The charts below show total electricity consumption in one country between 2010 and 2024, and the sources of that electricity in 2024.",
            "planNotes": "Line: total consumption rises then flattens after 2019. Pie: renewables now largest single source. Link = demand stopped growing while the supply mix changed. Overview covers both.",
            "modelSentence": "Total electricity consumption rose steadily until 2019 before levelling off, and by the end of the period the mix supplying that demand had shifted decisively towards renewable sources, which had become the single largest contributor.",
            "analysis": "One sentence carries the trend from the line graph and the composition from the pie, and the word 'that demand' is what ties the two visuals together. Neither figure is presented as if it measured the other.",
        },
        "languageBank": {
            "Linking visuals": ["over the same period", "this demand was met by", "while the total rose, the mix", "the second chart shows how"],
            "Hedged relation": ["coincided with", "accompanied", "ran alongside", "in parallel with"],
            "Structure": ["turning to the second chart", "as for the composition", "taken together, the two charts"],
            "Prepositions": ["a share of", "drawn from", "accounted for by", "over the same period"],
        },
        "tenseRule": "Follow each visual's own timeframe, and use past perfect when you need to show that one visual's state was already reached before the other's period ended.",
        "uaTransferNote": "'Taken together' і 'over the same period' — сталі звороти без артикля перед 'together'. Уникайте 'in the same time' замість 'at the same time' або 'over the same period'.",
        "uaSupport": "Два візуали не означають подвійний звіт. Оцінюється зв'язок між ними: одне overview на обидва і хоча б одне речення, яке використовує обидва джерела одночасно.",
    },
}

# ---------------------------------------------------------------------------
# Original visuals and datasets (CURRICULUM_SPEC.md section 6 "Visual/data
# sourcing"). Every dataset below was authored for this product. Place names
# are invented or generic; no commercial IELTS graphic is reproduced.
#
# Shapes by kind:
#   line / bar : categories[] + series[{name, values[]}]
#   pie        : snapshots[{label, slices[{label, value}]}]
#   table      : columns[] + rows[{label, cells[]}]
#   process    : stages[{n, label, detail}] + input/output/cyclical
#   map        : periods[] + features[{label, area, status, note}]
#   mixed      : components[] holding two of the above
# ---------------------------------------------------------------------------
VISUALS = [
    # ---------------------------- line graphs ----------------------------
    {
        "id": "W1V-LINE-01", "family": "line_graph", "kind": "line",
        "title": "Household recycling rates in three cities, 2005-2025",
        "taskStatement": "The line graph below shows the percentage of household waste recycled in three cities between 2005 and 2025.",
        "unit": "% of household waste recycled", "timeframe": "2005-2025",
        "axisLabel": "Percentage recycled",
        "categories": ["2005", "2010", "2015", "2020", "2025"],
        "series": [
            {"name": "Oslo", "values": [28, 34, 39, 43, 46]},
            {"name": "Bergen", "values": [31, 36, 40, 42, 44]},
            {"name": "Tromso", "values": [18, 27, 41, 52, 61]},
        ],
        "altText": "A line graph with three lines over five points from 2005 to 2025. Oslo climbs steadily from 28 to 46 per cent. Bergen climbs more gently from 31 to 44 per cent. Tromso starts lowest at 18 per cent, rises far more steeply, passes both other cities between 2010 and 2015, and finishes highest at 61 per cent.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-LINE-02", "family": "line_graph", "kind": "line",
        "title": "International student enrolment at three universities, 2010-2024",
        "taskStatement": "The line graph below shows the number of international students enrolled at three universities between 2010 and 2024.",
        "unit": "thousands of students", "timeframe": "2010-2024",
        "axisLabel": "Students (thousands)",
        "categories": ["2010", "2014", "2018", "2022", "2024"],
        "series": [
            {"name": "Northgate", "values": [12.0, 15.5, 19.0, 16.5, 18.0]},
            {"name": "Riverside", "values": [8.0, 9.5, 11.0, 12.5, 14.0]},
            {"name": "Eastfield", "values": [20.0, 18.0, 15.0, 11.0, 9.5]},
        ],
        "altText": "A line graph with three lines from 2010 to 2024. Northgate rises to a peak of 19 thousand in 2018, dips to 16.5 thousand in 2022, then recovers to 18 thousand. Riverside rises steadily throughout from 8 to 14 thousand. Eastfield falls continuously from 20 thousand to 9.5 thousand and is overtaken by Riverside between 2018 and 2022.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-LINE-03", "family": "line_graph", "kind": "line",
        "title": "Electricity generated from three renewable sources, 2000-2020",
        "taskStatement": "The line graph below shows electricity generated from wind, solar and hydroelectric sources in one country between 2000 and 2020.",
        "unit": "terawatt-hours", "timeframe": "2000-2020",
        "axisLabel": "Generation (TWh)",
        "categories": ["2000", "2005", "2010", "2015", "2020"],
        "series": [
            {"name": "Hydroelectric", "values": [34, 35, 36, 35, 37]},
            {"name": "Wind", "values": [2, 8, 21, 44, 68]},
            {"name": "Solar", "values": [1, 1, 5, 18, 41]},
        ],
        "altText": "A line graph from 2000 to 2020. Hydroelectric generation is almost flat, moving only between 34 and 37 terawatt-hours. Wind rises from 2 to 68 terawatt-hours and overtakes hydroelectric between 2010 and 2015. Solar rises from 1 to 41 terawatt-hours and overtakes hydroelectric between 2015 and 2020.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    # ---------------------------- bar charts ----------------------------
    {
        "id": "W1V-BAR-01", "family": "bar_chart", "kind": "bar",
        "title": "Average weekly leisure spending by age group",
        "taskStatement": "The bar chart below shows average weekly spending on four leisure categories by three age groups in one country.",
        "unit": "pounds per week", "timeframe": "2024",
        "axisLabel": "Average weekly spending (pounds)",
        "categories": ["18-29", "30-49", "50 and over"],
        "series": [
            {"name": "Eating out", "values": [42, 38, 31]},
            {"name": "Live events", "values": [27, 18, 8]},
            {"name": "Cultural visits", "values": [9, 14, 22]},
            {"name": "Streaming services", "values": [15, 12, 6]},
        ],
        "altText": "A grouped bar chart with three age groups. Eating out is the highest category in every group, falling from 42 to 31 pounds with age. Live events and streaming services both fall with age. Cultural visits is the only category that rises with age, from 9 to 22 pounds, so it overtakes live events in the oldest group.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-BAR-02", "family": "bar_chart", "kind": "bar",
        "title": "Adults cycling to work in six cities, 2024",
        "taskStatement": "The bar chart below shows the percentage of working adults who cycle to work in six European cities in 2024.",
        "unit": "% of working adults", "timeframe": "2024",
        "axisLabel": "Percentage who cycle to work",
        "categories": ["Amsterdam", "Copenhagen", "Munich", "Lyon", "Dublin", "Naples"],
        "series": [
            {"name": "Cycle to work", "values": [48, 44, 21, 14, 9, 4]},
        ],
        "altText": "A bar chart of six cities in descending order. Amsterdam leads at 48 per cent and Copenhagen is close behind at 44 per cent. There is then a large gap to Munich at 21 per cent, followed by Lyon at 14, Dublin at 9 and Naples lowest at 4 per cent.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-BAR-03", "family": "bar_chart", "kind": "bar",
        "title": "Freight moved by four transport modes, 1990 and 2020",
        "taskStatement": "The bar chart below shows the volume of freight moved by road, rail, water and air in one country in 1990 and 2020.",
        "unit": "million tonnes", "timeframe": "1990 and 2020",
        "axisLabel": "Freight moved (million tonnes)",
        "categories": ["1990", "2020"],
        "series": [
            {"name": "Road", "values": [620, 980]},
            {"name": "Rail", "values": [310, 240]},
            {"name": "Water", "values": [180, 265]},
            {"name": "Air", "values": [12, 48]},
        ],
        "altText": "A grouped bar chart comparing 1990 with 2020. Road dominates in both years, rising from 620 to 980 million tonnes. Water rises from 180 to 265 and air rises from 12 to 48 million tonnes. Rail is the only mode to fall, from 310 to 240 million tonnes.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    # ---------------------------- pie charts ----------------------------
    {
        "id": "W1V-PIE-01", "family": "pie_chart", "kind": "pie",
        "title": "Household water use in a coastal city, 2024",
        "taskStatement": "The pie chart below shows how household water was used in one coastal city in 2024.",
        "unit": "% of household water use", "timeframe": "2024",
        "snapshots": [
            {"label": "2024", "slices": [
                {"label": "Bathing and showering", "value": 34},
                {"label": "Toilet flushing", "value": 26},
                {"label": "Laundry", "value": 16},
                {"label": "Kitchen and drinking", "value": 12},
                {"label": "Garden watering", "value": 8},
                {"label": "Other", "value": 4},
            ]},
        ],
        "altText": "A single pie chart of household water use in 2024. Bathing and showering is the largest share at 34 per cent, followed by toilet flushing at 26 and laundry at 16 per cent. Kitchen and drinking accounts for 12 per cent, garden watering 8 per cent, and other uses the smallest share at 4 per cent.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-PIE-02", "family": "pie_chart", "kind": "pie",
        "title": "Composition of municipal waste, 2000 and 2020",
        "taskStatement": "The pie charts below show the composition of municipal waste in one city in 2000 and in 2020.",
        "unit": "% of municipal waste", "timeframe": "2000 and 2020",
        "snapshots": [
            {"label": "2000", "slices": [
                {"label": "Organic", "value": 42},
                {"label": "Paper", "value": 24},
                {"label": "Plastics", "value": 12},
                {"label": "Glass", "value": 9},
                {"label": "Metal", "value": 7},
                {"label": "Other", "value": 6},
            ]},
            {"label": "2020", "slices": [
                {"label": "Organic", "value": 31},
                {"label": "Paper", "value": 15},
                {"label": "Plastics", "value": 26},
                {"label": "Glass", "value": 10},
                {"label": "Metal", "value": 8},
                {"label": "Other", "value": 10},
            ]},
        ],
        "altText": "Two pie charts for 2000 and 2020. Organic waste is the largest share in both years but falls from 42 to 31 per cent. Paper falls from 24 to 15 per cent. Plastics more than doubles its share from 12 to 26 per cent. Glass, metal and other categories change only slightly, so the overall composition becomes more evenly spread.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-PIE-03", "family": "pie_chart", "kind": "pie",
        "title": "Reasons for choosing a postgraduate course, 2024",
        "taskStatement": "The pie chart below shows the main reasons given by students for choosing a postgraduate course in 2024.",
        "unit": "% of students surveyed", "timeframe": "2024",
        "snapshots": [
            {"label": "2024", "slices": [
                {"label": "Career advancement", "value": 38},
                {"label": "Interest in the subject", "value": 24},
                {"label": "Employer sponsorship", "value": 14},
                {"label": "Reputation of the institution", "value": 12},
                {"label": "Family expectation", "value": 7},
                {"label": "Other", "value": 5},
            ]},
        ],
        "altText": "A single pie chart of reasons for choosing a postgraduate course. Career advancement is the largest share at 38 per cent, ahead of interest in the subject at 24 per cent. Employer sponsorship accounts for 14 per cent and reputation of the institution 12 per cent. Family expectation is 7 per cent and other reasons the smallest at 5 per cent.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    # ------------------------------ tables ------------------------------
    {
        "id": "W1V-TAB-01", "family": "table", "kind": "table",
        "title": "Tourist arrivals and length of stay in five destinations, 2019 and 2023",
        "taskStatement": "The table below shows tourist arrivals and the average length of stay in five destinations in 2019 and 2023.",
        "unit": "millions of arrivals and nights per visit", "timeframe": "2019 and 2023",
        "columns": ["Arrivals 2019 (m)", "Arrivals 2023 (m)", "Stay 2019 (nights)", "Stay 2023 (nights)"],
        "rows": [
            {"label": "Coastal Bay", "cells": [4.2, 5.1, 6.8, 5.9]},
            {"label": "Lakeside", "cells": [2.7, 3.4, 5.2, 4.6]},
            {"label": "Old Harbour", "cells": [6.5, 7.2, 4.1, 3.7]},
            {"label": "Highland Park", "cells": [1.8, 2.3, 7.4, 7.6]},
            {"label": "Riverford", "cells": [3.9, 3.1, 3.6, 3.2]},
        ],
        "altText": "A table of five destinations with arrivals and average stay in 2019 and 2023. Arrivals rose in four destinations, led by Old Harbour at 7.2 million in 2023, and fell only at Riverford from 3.9 to 3.1 million. Average stay shortened everywhere except Highland Park, which rose slightly from 7.4 to 7.6 nights and remains the longest stay.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-TAB-02", "family": "table", "kind": "table",
        "title": "Cost of living index components in four cities, 2024",
        "taskStatement": "The table below shows four components of a cost of living index in four cities in 2024, where 100 is the national average.",
        "unit": "index points, national average = 100", "timeframe": "2024",
        "columns": ["Housing", "Transport", "Food", "Utilities"],
        "rows": [
            {"label": "Metroport", "cells": [142, 88, 106, 97]},
            {"label": "Rivergate", "cells": [118, 94, 101, 112]},
            {"label": "Northvale", "cells": [86, 71, 92, 84]},
            {"label": "Southcliff", "cells": [103, 120, 98, 90]},
        ],
        "altText": "A table of four cities against four cost components, indexed to a national average of 100. Metroport has the highest housing index at 142 but below-average transport at 88. Southcliff has the highest transport index at 120. Northvale is below the national average on all four components, with the lowest transport figure at 71. Food varies least across the four cities.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-TAB-03", "family": "table", "kind": "table",
        "title": "Employment by sector in one region, 1995-2025",
        "taskStatement": "The table below shows the percentage of the workforce employed in four sectors in one region in 1995, 2005, 2015 and 2025.",
        "unit": "% of the regional workforce", "timeframe": "1995-2025",
        "columns": ["1995", "2005", "2015", "2025"],
        "rows": [
            {"label": "Agriculture", "cells": [18, 13, 9, 6]},
            {"label": "Manufacturing", "cells": [31, 26, 19, 14]},
            {"label": "Services", "cells": [44, 53, 62, 68]},
            {"label": "Public administration", "cells": [7, 8, 10, 12]},
        ],
        "altText": "A table of four employment sectors across 1995, 2005, 2015 and 2025. Services grows continuously from 44 to 68 per cent of the workforce and is the largest sector throughout. Manufacturing falls from 31 to 14 per cent and agriculture from 18 to 6 per cent. Public administration rises gently from 7 to 12 per cent. Each column totals 100 per cent.",
        "sourceNote": "Original dataset authored for this product.",
        "originality": "original",
    },
    # -------------------------- process diagrams --------------------------
    {
        "id": "W1V-PROC-01", "family": "process_diagram", "kind": "process",
        "title": "How glass bottles are recycled",
        "taskStatement": "The diagram below shows how glass bottles are recycled.",
        "unit": "stages", "timeframe": "no dates shown",
        "cyclical": True,
        "input": "used glass bottles",
        "output": "new glass bottles",
        "stages": [
            {"n": 1, "label": "Collection", "detail": "Used bottles are collected from household and public bins."},
            {"n": 2, "label": "Transport", "detail": "The collected glass is taken by lorry to a processing plant."},
            {"n": 3, "label": "Manual sorting", "detail": "Non-glass items are removed by hand from a moving belt."},
            {"n": 4, "label": "Colour separation", "detail": "Clear, green and brown glass are separated into three streams."},
            {"n": 5, "label": "Crushing", "detail": "The separated glass is crushed into small fragments known as cullet."},
            {"n": 6, "label": "Melting", "detail": "The cullet is melted in a furnace until it becomes molten glass."},
            {"n": 7, "label": "Moulding", "detail": "The molten glass is moulded into the shape of new bottles."},
            {"n": 8, "label": "Distribution", "detail": "New bottles are filled, sold, and returned to the collection stage."},
        ],
        "altText": "A cyclical diagram of eight stages. Used bottles are collected, transported to a plant, sorted by hand, separated by colour, crushed into cullet, melted in a furnace, moulded into new bottles, then distributed and returned to the collection stage, so the process forms a closed loop.",
        "sourceNote": "Original diagram authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-PROC-02", "family": "process_diagram", "kind": "process",
        "title": "The life cycle of the Atlantic salmon",
        "taskStatement": "The diagram below shows the life cycle of the Atlantic salmon.",
        "unit": "stages", "timeframe": "no dates shown",
        "cyclical": True,
        "input": "eggs laid in a freshwater river",
        "output": "adults returning upstream to spawn",
        "stages": [
            {"n": 1, "label": "Egg", "detail": "Eggs are laid among gravel in the shallow upper reaches of a river."},
            {"n": 2, "label": "Alevin", "detail": "The alevin hatches and feeds on the yolk sac attached to its body."},
            {"n": 3, "label": "Fry", "detail": "The fry emerges from the gravel and begins to feed in the shallows."},
            {"n": 4, "label": "Smolt", "detail": "The smolt migrates downstream and enters salt water at the river mouth."},
            {"n": 5, "label": "Adult at sea", "detail": "The adult matures in the open ocean over several years."},
            {"n": 6, "label": "Spawning adult", "detail": "The mature adult returns upstream to the river where it hatched."},
        ],
        "altText": "A cyclical diagram of six stages. Eggs are laid in river gravel, hatch into alevins feeding on a yolk sac, develop into fry in the shallows, become smolts that migrate to the sea, mature as adults in the open ocean, and finally return upstream as spawning adults to the river where they hatched, completing the cycle.",
        "sourceNote": "Original diagram authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-PROC-03", "family": "process_diagram", "kind": "process",
        "title": "How rainwater is captured and treated for drinking",
        "taskStatement": "The diagram below shows how rainwater is captured and treated to make it safe to drink.",
        "unit": "stages", "timeframe": "no dates shown",
        "cyclical": False,
        "input": "rainwater falling on a roof",
        "output": "drinking water at household taps",
        "stages": [
            {"n": 1, "label": "Catchment", "detail": "Rainwater is collected on a sloping roof surface and channelled into gutters."},
            {"n": 2, "label": "First-flush diversion", "detail": "The first volume of water, carrying most of the debris, is diverted away."},
            {"n": 3, "label": "Coarse screening", "detail": "The remaining water passes through a mesh screen that removes leaves and grit."},
            {"n": 4, "label": "Storage", "detail": "The screened water is held in a sealed underground tank."},
            {"n": 5, "label": "Sediment filtration", "detail": "Water drawn from the tank passes through a fine sediment filter."},
            {"n": 6, "label": "Ultraviolet disinfection", "detail": "The filtered water is exposed to ultraviolet light in a treatment unit."},
            {"n": 7, "label": "Distribution", "detail": "The treated water is pumped to taps inside the house."},
        ],
        "altText": "A linear diagram of seven stages. Rainwater is caught on a roof, the dirtiest first flush is diverted away, the rest is screened through a mesh, stored in a sealed underground tank, filtered for sediment, disinfected with ultraviolet light, and finally pumped to household taps.",
        "sourceNote": "Original diagram authored for this product.",
        "originality": "original",
    },
    # ----------------------------- maps / plans -----------------------------
    {
        "id": "W1V-MAP-01", "family": "map_plan", "kind": "map",
        "title": "The village of Whitmore in 1985 and today",
        "taskStatement": "The maps below show the village of Whitmore in 1985 and in the present day.",
        "unit": "site features", "timeframe": "1985 and today",
        "periods": ["1985", "today"],
        "features": [
            {"label": "Farmland", "area": "south", "status": "removed", "note": "Cleared to make way for the housing estate."},
            {"label": "Housing estate", "area": "south", "status": "added", "note": "Built on the site of the former farmland."},
            {"label": "Woodland", "area": "northern boundary", "status": "unchanged", "note": "Left untouched across the whole period."},
            {"label": "Village shop", "area": "centre", "status": "replaced", "note": "Converted into a supermarket on the same footprint."},
            {"label": "Cattle market", "area": "centre", "status": "removed", "note": "Demolished and replaced by a car park."},
            {"label": "Primary school", "area": "west", "status": "unchanged", "note": "Retained in its original position."},
            {"label": "Bypass road", "area": "eastern edge", "status": "added", "note": "Constructed along the eastern boundary of the village."},
        ],
        "altText": "Two maps of Whitmore. In the south, farmland has been cleared and a housing estate built in its place. In the centre, the village shop has become a supermarket on the same footprint and the cattle market has been demolished. A bypass road has been added along the eastern edge. The woodland on the northern boundary and the primary school in the west are unchanged.",
        "sourceNote": "Original plan authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-MAP-02", "family": "map_plan", "kind": "map",
        "title": "University library ground floor, current and proposed",
        "taskStatement": "The plans below show the ground floor of a university library as it is now and as it is proposed to be after redevelopment.",
        "unit": "floor plan features", "timeframe": "current and proposed",
        "periods": ["current", "proposed"],
        "features": [
            {"label": "Print journal stacks", "area": "north wing", "status": "removed", "note": "To be cleared to open up the north wing."},
            {"label": "Group study pods", "area": "north wing", "status": "added", "note": "To occupy the space freed by the journal stacks."},
            {"label": "Issue desk", "area": "entrance", "status": "replaced", "note": "To be replaced by a bank of self-service kiosks."},
            {"label": "Microfilm room", "area": "west side", "status": "removed", "note": "To be closed and absorbed into the reading area."},
            {"label": "Cafe", "area": "east side", "status": "added", "note": "To be built beside the main entrance."},
            {"label": "Silent reading room", "area": "south wing", "status": "unchanged", "note": "To be retained in its present form."},
            {"label": "Main staircase", "area": "centre", "status": "unchanged", "note": "To remain in the centre of the floor."},
        ],
        "altText": "Two ground-floor plans of a university library. In the north wing the print journal stacks are to be removed and replaced by group study pods. At the entrance the issue desk is to become a bank of self-service kiosks, and a cafe is to be added on the east side. The microfilm room on the west side is to be closed. The silent reading room in the south wing and the central staircase are to remain unchanged.",
        "sourceNote": "Original plan authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-MAP-03", "family": "map_plan", "kind": "map",
        "title": "A coastal resort in 1990 and 2020",
        "taskStatement": "The maps below show a coastal resort in 1990 and in 2020.",
        "unit": "site features", "timeframe": "1990 and 2020",
        "periods": ["1990", "2020"],
        "features": [
            {"label": "Fishing harbour", "area": "west", "status": "unchanged", "note": "Still in use in its original position."},
            {"label": "Boatyard", "area": "west", "status": "replaced", "note": "Converted into a marina for leisure craft."},
            {"label": "Caravan park", "area": "east", "status": "removed", "note": "Cleared from the eastern side of the resort."},
            {"label": "Hotel complex", "area": "east", "status": "added", "note": "Built on the site of the former caravan park."},
            {"label": "Farmland", "area": "inland to the north", "status": "removed", "note": "Given over to the new golf course."},
            {"label": "Golf course", "area": "inland to the north", "status": "added", "note": "Laid out on the former farmland."},
            {"label": "Coastal footpath", "area": "along the shoreline", "status": "unchanged", "note": "Retained along the full length of the shore."},
        ],
        "altText": "Two maps of a coastal resort. In the west the fishing harbour is unchanged but the boatyard beside it has become a marina. In the east the caravan park has been cleared and a hotel complex built in its place. Inland to the north, farmland has been replaced by a golf course. The coastal footpath along the shoreline is unchanged.",
        "sourceNote": "Original plan authored for this product.",
        "originality": "original",
    },
    # ---------------------------- mixed visuals ----------------------------
    {
        "id": "W1V-MIX-01", "family": "mixed_visual", "kind": "mixed",
        "title": "Electricity consumption and its sources",
        "taskStatement": "The charts below show total electricity consumption in one country between 2010 and 2024, and the sources of that electricity in 2024.",
        "unit": "terawatt-hours and % of supply", "timeframe": "2010-2024",
        "components": [
            {"kind": "line", "title": "Total electricity consumption, 2010-2024",
             "unit": "terawatt-hours", "axisLabel": "Consumption (TWh)",
             "categories": ["2010", "2013", "2016", "2019", "2022", "2024"],
             "series": [{"name": "Total consumption", "values": [310, 335, 356, 372, 374, 376]}]},
            {"kind": "pie", "title": "Sources of electricity, 2024", "unit": "% of supply",
             "snapshots": [{"label": "2024", "slices": [
                 {"label": "Renewables", "value": 38},
                 {"label": "Natural gas", "value": 27},
                 {"label": "Nuclear", "value": 19},
                 {"label": "Coal", "value": 11},
                 {"label": "Other", "value": 5},
             ]}]},
        ],
        "altText": "Two charts. The line graph shows total electricity consumption rising steadily from 310 terawatt-hours in 2010 to 372 in 2019, then levelling off at around 376 by 2024. The pie chart shows the 2024 supply mix, in which renewables form the largest share at 38 per cent, ahead of natural gas at 27, nuclear at 19, coal at 11 and other sources at 5 per cent.",
        "sourceNote": "Original datasets authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-MIX-02", "family": "mixed_visual", "kind": "mixed",
        "title": "Rail passenger numbers and passenger satisfaction",
        "taskStatement": "The table and chart below show passenger journeys on four rail lines in 2018 and 2023, and passenger satisfaction with each line in 2023.",
        "unit": "millions of journeys and % satisfied", "timeframe": "2018 and 2023",
        "components": [
            {"kind": "table", "title": "Passenger journeys, 2018 and 2023", "unit": "millions of journeys",
             "columns": ["2018 (m)", "2023 (m)"],
             "rows": [
                 {"label": "Northern Line", "cells": [42.0, 38.5]},
                 {"label": "Coastal Line", "cells": [18.4, 22.1]},
                 {"label": "Valley Line", "cells": [9.6, 11.3]},
                 {"label": "City Loop", "cells": [61.2, 57.8]},
             ]},
            {"kind": "bar", "title": "Passenger satisfaction, 2023", "unit": "% satisfied",
             "axisLabel": "Passengers satisfied (%)",
             "categories": ["Northern Line", "Coastal Line", "Valley Line", "City Loop"],
             "series": [{"name": "Satisfied", "values": [61, 84, 79, 66]}]},
        ],
        "altText": "A table and a bar chart. The table shows that journeys fell on the Northern Line and the City Loop between 2018 and 2023, while the Coastal Line and Valley Line both grew. The bar chart shows satisfaction in 2023: the two growing lines score highest at 84 and 79 per cent, while the two declining lines score lowest at 61 and 66 per cent.",
        "sourceNote": "Original datasets authored for this product.",
        "originality": "original",
    },
    {
        "id": "W1V-MIX-03", "family": "mixed_visual", "kind": "mixed",
        "title": "Graduate employment by field and graduate destinations",
        "taskStatement": "The charts below show the percentage of graduates in work within six months by field of study, and the destinations of all graduates, in 2024.",
        "unit": "% in work and % of graduates", "timeframe": "2024",
        "components": [
            {"kind": "bar", "title": "In work within six months, by field", "unit": "% of graduates",
             "axisLabel": "In work within six months (%)",
             "categories": ["Engineering", "Health", "Business", "Humanities", "Computing"],
             "series": [{"name": "In work", "values": [88, 92, 81, 68, 90]}]},
            {"kind": "pie", "title": "Destinations of all graduates, 2024", "unit": "% of graduates",
             "snapshots": [{"label": "2024", "slices": [
                 {"label": "Full-time employment", "value": 54},
                 {"label": "Further study", "value": 21},
                 {"label": "Part-time employment", "value": 13},
                 {"label": "Seeking work", "value": 9},
                 {"label": "Other", "value": 3},
             ]}]},
        ],
        "altText": "A bar chart and a pie chart. The bar chart shows health graduates most likely to be in work within six months at 92 per cent, followed by computing at 90 and engineering at 88, with humanities lowest at 68 per cent. The pie chart shows that across all graduates, 54 per cent enter full-time employment, 21 per cent go on to further study, 13 per cent work part time, 9 per cent are seeking work and 3 per cent report other destinations.",
        "sourceNote": "Original datasets authored for this product.",
        "originality": "original",
    },
]

VISUALS_BY_ID = {v["id"]: v for v in VISUALS}


# ---------------------------------------------------------------------------
# Fact engine. Every reportable claim an exercise makes is expressed as a key
# in this dict, so that grounding can be checked mechanically rather than by
# reading the prose. tests/g4_writing1_validation.py re-implements this
# computation from scratch and asserts it reproduces the emitted facts.
# ---------------------------------------------------------------------------
def _round(x, places=2):
    r = round(float(x), places)
    return int(r) if abs(r - int(r)) < 1e-9 else r


def _series_facts(cats, series, prefix=""):
    facts = {}
    for s in series:
        name, vals = s["name"], s["values"]
        for c, v in zip(cats, vals):
            facts[f"{prefix}value.{name}.{c}"] = _round(v)
        hi, lo = max(vals), min(vals)
        facts[f"{prefix}max.{name}"] = _round(hi)
        facts[f"{prefix}min.{name}"] = _round(lo)
        facts[f"{prefix}max_at.{name}"] = cats[vals.index(hi)]
        facts[f"{prefix}min_at.{name}"] = cats[vals.index(lo)]
        facts[f"{prefix}first.{name}"] = _round(vals[0])
        facts[f"{prefix}last.{name}"] = _round(vals[-1])
        facts[f"{prefix}delta.{name}"] = _round(vals[-1] - vals[0])
        if vals[0]:
            facts[f"{prefix}pct_change.{name}"] = _round((vals[-1] - vals[0]) / vals[0] * 100, 1)
        # Any two readings of the same line can legitimately be compared, so
        # every pairwise change is a derivable claim about this visual.
        for i in range(len(cats)):
            for j in range(i + 1, len(cats)):
                facts[f"{prefix}change.{name}.{cats[i]}.{cats[j]}"] = _round(vals[j] - vals[i])
    for i, c in enumerate(cats):
        col = [(s["name"], s["values"][i]) for s in series]
        col_sorted = sorted(col, key=lambda t: -t[1])
        facts[f"{prefix}top.{c}"] = col_sorted[0][0]
        facts[f"{prefix}bottom.{c}"] = col_sorted[-1][0]
        facts[f"{prefix}total.{c}"] = _round(sum(v for _, v in col))
        facts[f"{prefix}rank.{c}"] = " > ".join(n for n, _ in col_sorted)
        # And any two series can be compared at the same point.
        for a in range(len(series)):
            for b in range(a + 1, len(series)):
                na, nb = series[a]["name"], series[b]["name"]
                facts[f"{prefix}gap.{na}.{nb}.{c}"] = _round(series[a]["values"][i] - series[b]["values"][i])
    return facts


def _pie_facts(snapshots, prefix=""):
    facts = {}
    for snap in snapshots:
        lab = snap["label"]
        slices = snap["slices"]
        for sl in slices:
            facts[f"{prefix}share.{sl['label']}.{lab}"] = _round(sl["value"])
        ordered = sorted(slices, key=lambda s: -s["value"])
        facts[f"{prefix}largest.{lab}"] = ordered[0]["label"]
        facts[f"{prefix}smallest.{lab}"] = ordered[-1]["label"]
        facts[f"{prefix}total.{lab}"] = _round(sum(s["value"] for s in slices))
        facts[f"{prefix}rank.{lab}"] = " > ".join(s["label"] for s in ordered)
        for a in range(len(slices)):
            for b in range(a + 1, len(slices)):
                la, lb = slices[a]["label"], slices[b]["label"]
                facts[f"{prefix}gap.{la}.{lb}.{lab}"] = _round(slices[a]["value"] - slices[b]["value"])
                facts[f"{prefix}sum.{la}.{lb}.{lab}"] = _round(slices[a]["value"] + slices[b]["value"])
    if len(snapshots) == 2:
        a, b = snapshots[0], snapshots[1]
        av = {s["label"]: s["value"] for s in a["slices"]}
        for sl in b["slices"]:
            if sl["label"] in av:
                facts[f"{prefix}delta_share.{sl['label']}"] = _round(sl["value"] - av[sl["label"]])
    return facts


def _table_facts(columns, rows, prefix=""):
    facts = {}
    for r in rows:
        for c, v in zip(columns, r["cells"]):
            facts[f"{prefix}value.{r['label']}.{c}"] = _round(v)
    for i, c in enumerate(columns):
        col = [(r["label"], r["cells"][i]) for r in rows]
        ordered = sorted(col, key=lambda t: -t[1])
        facts[f"{prefix}max.{c}"] = ordered[0][0]
        facts[f"{prefix}min.{c}"] = ordered[-1][0]
        facts[f"{prefix}total.{c}"] = _round(sum(v for _, v in col))
    # Any two columns of the same row can legitimately be compared.
    for r in rows:
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                facts[f"{prefix}delta.{r['label']}.{columns[i]}.{columns[j]}"] = _round(r["cells"][j] - r["cells"][i])
    return facts


def _process_facts(v, prefix=""):
    facts = {
        f"{prefix}stage_count": len(v["stages"]),
        f"{prefix}input": v["input"],
        f"{prefix}output": v["output"],
        f"{prefix}cyclical": "yes" if v["cyclical"] else "no",
        f"{prefix}first_stage": v["stages"][0]["label"],
        f"{prefix}last_stage": v["stages"][-1]["label"],
    }
    for st in v["stages"]:
        facts[f"{prefix}stage.{st['n']}"] = st["label"]
    return facts


def _map_facts(v, prefix=""):
    facts = {}
    counts = {"added": 0, "removed": 0, "replaced": 0, "unchanged": 0}
    for f in v["features"]:
        facts[f"{prefix}status.{f['label']}"] = f["status"]
        facts[f"{prefix}area.{f['label']}"] = f["area"]
        counts[f["status"]] += 1
    for k, n in counts.items():
        facts[f"{prefix}count.{k}"] = n
    facts[f"{prefix}feature_count"] = len(v["features"])
    return facts


def compute_facts(v):
    """Derive every checkable claim from a visual's own data."""
    kind = v["kind"]
    if kind in ("line", "bar"):
        return _series_facts(v["categories"], v["series"])
    if kind == "pie":
        return _pie_facts(v["snapshots"])
    if kind == "table":
        return _table_facts(v["columns"], v["rows"])
    if kind == "process":
        return _process_facts(v)
    if kind == "map":
        return _map_facts(v)
    if kind == "mixed":
        facts = {}
        for i, comp in enumerate(v["components"]):
            p = f"c{i}."
            if comp["kind"] in ("line", "bar"):
                facts.update(_series_facts(comp["categories"], comp["series"], p))
            elif comp["kind"] == "pie":
                facts.update(_pie_facts(comp["snapshots"], p))
            elif comp["kind"] == "table":
                facts.update(_table_facts(comp["columns"], comp["rows"], p))
        return facts
    raise ValueError(f"unknown visual kind {kind}")


def support_numbers(v):
    """Every number a claim about this visual is allowed to use."""
    nums = set()
    for val in compute_facts(v).values():
        if isinstance(val, (int, float)):
            nums.add(_round(val))
            nums.add(_round(abs(val)))
    def add_series(cats, series):
        for s in series:
            for x in s["values"]:
                nums.add(_round(x))
        for c in cats:
            # Category labels legitimately carry figures of their own, whether
            # they are plain years ("2015") or banded ("18-29", "50 and over").
            for tok in re.findall(r"\d+(?:\.\d+)?", str(c)):
                nums.add(_round(float(tok)))
    kind = v["kind"]
    if kind in ("line", "bar"):
        add_series(v["categories"], v["series"])
    elif kind == "pie":
        for snap in v["snapshots"]:
            if str(snap["label"]).isdigit():
                nums.add(int(snap["label"]))
            for sl in snap["slices"]:
                nums.add(_round(sl["value"]))
    elif kind == "table":
        for r in v["rows"]:
            for x in r["cells"]:
                nums.add(_round(x))
        for c in v["columns"]:
            for tok in str(c).replace("(", " ").replace(")", " ").split():
                if tok.isdigit():
                    nums.add(int(tok))
    elif kind == "process":
        nums.update(range(1, len(v["stages"]) + 1))
    elif kind == "map":
        for p in v["periods"]:
            if str(p).isdigit():
                nums.add(int(p))
        nums.update(range(0, len(v["features"]) + 1))
    elif kind == "mixed":
        for comp in v["components"]:
            if comp["kind"] in ("line", "bar"):
                add_series(comp["categories"], comp["series"])
            elif comp["kind"] == "pie":
                for snap in comp["snapshots"]:
                    if str(snap["label"]).isdigit():
                        nums.add(int(snap["label"]))
                    for sl in snap["slices"]:
                        nums.add(_round(sl["value"]))
            elif comp["kind"] == "table":
                for r in comp["rows"]:
                    for x in r["cells"]:
                        nums.add(_round(x))
                for c in comp["columns"]:
                    for tok in str(c).replace("(", " ").replace(")", " ").split():
                        if tok.isdigit():
                            nums.add(int(tok))
    # The timeframe and the unit legitimately declare figures of their own,
    # such as an index base of 100 or the years bounding the period.
    for field in ("timeframe", "unit"):
        for tok in str(v.get(field, "")).replace("-", " ").replace("=", " ").split():
            tok = tok.strip("(),%")
            if tok.isdigit():
                nums.add(int(tok))
    return nums

# ---------------------------------------------------------------------------
# Micro-exercises. Every family carries one exercise of each of the ten types
# in MICRO_TYPES, so 7 families x 10 types = 70 items against a benchmark of 60.
#
# Interaction shapes:
#   select : options[] + answer + distractors{option: why it fails}
#   cloze  : sentence containing "____" + answer + accept[]
#   order  : items[{id, text}] + order[] of ids
#
# "grounding" names the fact keys from the item's own visual that make the
# correct answer true. "allowedNumbers" declares figures in an explanation that
# are structural rather than data (paragraph counts, category counts); the
# validator caps them at 10 so the field cannot smuggle in a data claim.
# ---------------------------------------------------------------------------
EXERCISES = [
    # ======================= LINE GRAPHS =======================
    {
        "family": "line_graph", "type": "feature_selection", "visual": "W1V-LINE-01",
        "prompt": "Which detail from this graph most deserves a place in your report?",
        "options": [
            "Tromso overtook both other cities between 2010 and 2015 and finished the period as the highest performer.",
            "Oslo recorded 34 per cent in 2010.",
            "Each city is plotted at five points across the period.",
            "Bergen was ahead of Oslo in 2005.",
        ],
        "answer": "Tromso overtook both other cities between 2010 and 2015 and finished the period as the highest performer.",
        "distractors": {
            "Oslo recorded 34 per cent in 2010.": "A single mid-period reading with nothing remarkable about it. It is accurate, but it carries no pattern, so it cannot earn a place in an overview.",
            "Each city is plotted at five points across the period.": "This describes how the graph was drawn, not what it shows. Structural observations about the graphic itself are never reportable content.",
            "Bergen was ahead of Oslo in 2005.": "True, but the gap is small and it closes and reverses later. Reporting the opening position of the two similar lines without their outcome misses the point of the comparison.",
        },
        "explanation": "This graph is built around Tromso: it starts lowest at 18 per cent, ends highest at 61 per cent, and crosses both other lines on the way. A crossover combined with a change of rank is exactly the feature an examiner expects to see identified, because it cannot be inferred from any single reading.",
        "errorCategory": "list_like_description",
        "grounding": ["first.Tromso", "last.Tromso", "top.2005", "top.2025"],
        "ua": "Ключова ознака — це не найбільше число, а зміна взаємного порядку ліній. Шукайте перетини та зміну лідера.",
    },
    {
        "family": "line_graph", "type": "overview_selection", "visual": "W1V-LINE-01",
        "prompt": "Which sentence works best as the overview paragraph for this graph?",
        "options": [
            "Recycling rates rose in all three cities, but Tromso improved far more steeply than the others and ended the period as the clear leader.",
            "Oslo rose from 28 to 46 per cent, Bergen from 31 to 44 per cent and Tromso from 18 to 61 per cent.",
            "Recycling improved because all three cities introduced new kerbside collection schemes.",
            "Tromso should be regarded as the most environmentally responsible of the three cities.",
        ],
        "answer": "Recycling rates rose in all three cities, but Tromso improved far more steeply than the others and ended the period as the clear leader.",
        "distractors": {
            "Oslo rose from 28 to 46 per cent, Bergen from 31 to 44 per cent and Tromso from 18 to 61 per cent.": "Accurate, but this is body-paragraph detail. An overview states patterns; the moment it starts listing figures it has stopped doing its job.",
            "Recycling improved because all three cities introduced new kerbside collection schemes.": "The graph shows that rates rose, never why. Supplying a cause the graphic cannot evidence is one of the fastest ways to lose marks in Task 1.",
            "Tromso should be regarded as the most environmentally responsible of the three cities.": "This is a judgement, not a report. Task 1 describes what the data shows and stops there.",
        },
        "explanation": "A strong overview names the shared pattern (all three rose), the contrast that matters (Tromso rose far more steeply) and the outcome (it finished in front), all without a single figure. The figures then have somewhere to go in the body paragraphs.",
        "errorCategory": "missing_overview",
        "grounding": ["delta.Oslo", "delta.Bergen", "delta.Tromso", "top.2025"],
        "ua": "Overview — це узагальнення без цифр. Якщо у вашому overview є числа, ви вже пишете body-абзац.",
    },
    {
        "family": "line_graph", "type": "grouping", "visual": "W1V-LINE-01",
        "prompt": "Which plan groups the three lines most effectively for the body paragraphs?",
        "options": [
            "One paragraph for Oslo and Bergen, which followed similar steady paths, and one for Tromso, which behaved differently from both.",
            "One paragraph for each city, taken in the order they appear in the legend.",
            "One paragraph for each year on the horizontal axis.",
            "One paragraph covering 2005 to 2010 and one covering 2015 to 2025.",
        ],
        "answer": "One paragraph for Oslo and Bergen, which followed similar steady paths, and one for Tromso, which behaved differently from both.",
        "distractors": {
            "One paragraph for each city, taken in the order they appear in the legend.": "Legend order is not importance order. Three separate paragraphs produce a list with no comparison in it, which is the defining weakness of a Band 6 Task 1 response.",
            "One paragraph for each year on the horizontal axis.": "Five paragraphs, each describing three cities, forces you to restate every line repeatedly and leaves no room for the pattern.",
            "One paragraph covering 2005 to 2010 and one covering 2015 to 2025.": "Splitting by time means describing all three lines twice. Grouping should follow behaviour, because behaviour is what the reader needs to understand.",
        },
        "explanation": "Oslo and Bergen finish only two points apart after starting three points apart, so they belong together as one steady group. Tromso, which gains 43 points, is the outlier and earns a paragraph of its own. Grouping by behaviour is what converts description into comparison.",
        "errorCategory": "list_like_description",
        "grounding": ["last.Oslo", "last.Bergen", "first.Oslo", "first.Bergen", "delta.Tromso"],
        "ua": "Групуйте лінії за поведінкою, а не за легендою чи роками. Схожі — разом, виняток — окремо.",
    },
    {
        "family": "line_graph", "type": "trend_language", "visual": "W1V-LINE-01",
        "prompt": "Which phrase describes Tromso's line between 2005 and 2025 most accurately?",
        "options": [
            "a steep and sustained climb, more than tripling over the period",
            "a gradual and largely marginal increase",
            "a fluctuating pattern with several reversals",
            "a rise that levelled off after 2015",
        ],
        "answer": "a steep and sustained climb, more than tripling over the period",
        "distractors": {
            "a gradual and largely marginal increase": "'Marginal' is reserved for movements of a point or two. A gain of 43 points is at the opposite end of the scale.",
            "a fluctuating pattern with several reversals": "The line never changes direction. 'Fluctuating' would need the figure to fall and rise again at least once.",
            "a rise that levelled off after 2015": "The line keeps climbing to its highest point of 61 per cent in 2025, so it never levels off.",
        },
        "explanation": "Tromso climbs from 18 to 61 per cent without a single reversal, so the adverb has to carry both the direction and the size. 'More than tripling' is a safe way to express the scale, because 61 is over three times 18. Sizing the adverb to the movement is what separates precise trend language from vague trend language.",
        "errorCategory": "imprecise_quantity",
        "grounding": ["first.Tromso", "last.Tromso", "delta.Tromso", "max_at.Tromso"],
        "ua": "Прислівник має відповідати величині руху: marginally, gradually, steadily, sharply, dramatically.",
    },
    {
        "family": "line_graph", "type": "comparison_building", "visual": "W1V-LINE-02",
        "prompt": "Which comparison is fully supported by this graph?",
        "options": [
            "By 2024 Riverside enrolled more international students than Eastfield, having been the smaller of the two in 2010.",
            "Northgate grew faster than Riverside across the whole period.",
            "Riverside overtook Eastfield in 2020.",
            "Northgate was the largest of the three universities throughout the period.",
        ],
        "answer": "By 2024 Riverside enrolled more international students than Eastfield, having been the smaller of the two in 2010.",
        "distractors": {
            "Northgate grew faster than Riverside across the whole period.": "Both gained exactly 6 thousand students, and in proportional terms Riverside grew more. 'Faster' is not supported in either reading, so the comparison cannot stand.",
            "Riverside overtook Eastfield in 2020.": "The graph is plotted at 2010, 2014, 2018, 2022 and 2024. It never measures 2020, so no event can be placed in that year.",
            "Northgate was the largest of the three universities throughout the period.": "In 2010 Eastfield was larger, at 20 thousand against Northgate's 12 thousand. 'Throughout' is contradicted by the opening reading.",
        },
        "explanation": "A valid comparison needs two points the graph actually plots and a relationship it actually establishes. Riverside starts at 8 thousand against Eastfield's 20 thousand and finishes at 14 thousand against 9.5 thousand, so the reversal of rank is directly readable. The other options each fail on a different count: an unsupported rate claim, an unplotted year, and a contradicted absolute.",
        "errorCategory": "invalid_comparison",
        "grounding": ["first.Riverside", "first.Eastfield", "last.Riverside", "last.Eastfield", "delta.Northgate", "delta.Riverside"],
        "ua": "Порівняння має спиратися на точки, які графік справді показує. Рік між позначками — це вже здогад.",
    },
    {
        "family": "line_graph", "type": "data_to_sentence", "visual": "W1V-LINE-02",
        "prompt": "Complete the sentence with one word so that it reports Eastfield's line accurately.",
        "sentence": "Enrolment at Eastfield fell ____ 20 thousand in 2010 to 9.5 thousand in 2024.",
        "answer": "from",
        "accept": ["from"],
        "explanation": "'Fall from X to Y' names the start and the end value. 'Fall by' names the size of the drop, which here is 10.5 thousand, so the two prepositions report completely different quantities. Choosing between them is one of the most consequential decisions in data language.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["first.Eastfield", "last.Eastfield", "delta.Eastfield"],
        "ua": "'From ... to ...' — початкове і кінцеве значення. 'By' — величина зміни. Українське 'на' відповідає саме 'by'.",
    },
    {
        "family": "line_graph", "type": "paraphrase_no_distortion", "visual": "W1V-LINE-02",
        "prompt": "Original: 'Northgate's enrolment peaked at 19 thousand in 2018 before falling back and then partially recovering.' Which paraphrase preserves the meaning exactly?",
        "options": [
            "Having reached a high of 19 thousand in 2018, Northgate's enrolment dropped and then regained some of the ground it had lost.",
            "Northgate's enrolment reached 19 thousand in 2018 and then declined steadily to the end of the period.",
            "Northgate's enrolment doubled by 2018 before collapsing.",
            "Northgate's enrolment peaked in 2018 and has recovered fully since then.",
        ],
        "answer": "Having reached a high of 19 thousand in 2018, Northgate's enrolment dropped and then regained some of the ground it had lost.",
        "distractors": {
            "Northgate's enrolment reached 19 thousand in 2018 and then declined steadily to the end of the period.": "The line rises again after 2022, so 'declined steadily to the end' contradicts the final segment of the graph.",
            "Northgate's enrolment doubled by 2018 before collapsing.": "Two distortions in one sentence. A rise from 12 to 19 thousand is not a doubling, and a fall to 16.5 thousand is not a collapse.",
            "Northgate's enrolment peaked in 2018 and has recovered fully since then.": "'Fully' overstates the recovery. The line ends at 18 thousand, still below its peak of 19 thousand.",
        },
        "explanation": "A safe paraphrase changes the wording and leaves the magnitude, the direction and the degree of completeness untouched. 'Regained some of the ground' preserves the partial recovery that 'partially recovering' expressed; 'fully' and 'collapsing' both move the figure without licence from the graph.",
        "errorCategory": "lexical_distortion",
        "grounding": ["max.Northgate", "max_at.Northgate", "first.Northgate", "last.Northgate", "value.Northgate.2022"],
        "ua": "Змінюйте слова, а не значення. Найчастіші спотворення — 'fully', 'doubled', 'collapsed'.",
    },
    {
        "family": "line_graph", "type": "sentence_correction", "visual": "W1V-LINE-03",
        "prompt": "This sentence contains two faults: 'Wind generation overtook hydroelectric power in 2012 because governments began subsidising wind farms.' Which correction repairs both?",
        "options": [
            "Wind generation overtook hydroelectric power between 2010 and 2015.",
            "Wind generation overtook hydroelectric power in 2012, which was a positive development.",
            "Wind generation probably overtook hydroelectric power because of government subsidies.",
            "Wind generation overtook hydroelectric power in 2015.",
        ],
        "answer": "Wind generation overtook hydroelectric power between 2010 and 2015.",
        "distractors": {
            "Wind generation overtook hydroelectric power in 2012, which was a positive development.": "The invented year survives, and an evaluation has been added on top of it. This option is worse than the original.",
            "Wind generation probably overtook hydroelectric power because of government subsidies.": "Hedging a causal claim does not make it supportable. The graph still shows only that the crossing happened.",
            "Wind generation overtook hydroelectric power in 2015.": "By 2015 wind is already at 44 against hydroelectric's 35, so the crossing happened before that reading, not at it. Only one of the two faults has been fixed.",
        },
        "explanation": "The graph is plotted at five-year intervals, so a crossing can only be located between two plotted points, never at a year the graph never measures. The second fault is the reason: the lines show that wind overtook hydroelectric power, not why. A correction has to remove both, which is what makes this a timed-practice item rather than a spotting exercise.",
        "errorCategory": "unsupported_causal_claim",
        "grounding": ["value.Wind.2010", "value.Hydroelectric.2010", "value.Wind.2015", "value.Hydroelectric.2015"],
        "deliberateErrorFigures": [2012],
        "deliberateErrorReason": "The faulty sentence the learner has to repair names 2012, a year the graph never plots. That invented year is the fault being trained, so it is declared rather than authorised as data.",
        "ua": "Графік показує, що сталося, а не чому. І подія між позначками не має точного року.",
    },
    {
        "family": "line_graph", "type": "grammar_correction", "visual": "W1V-LINE-03",
        "prompt": "One preposition is wrong. Type the single word that should replace 'by'.",
        "sentence": "Between 2000 and 2020, wind generation rose ____ 68 terawatt-hours.",
        "answer": "to",
        "accept": ["to"],
        "explanation": "Wind generation finishes at 68 terawatt-hours, so 68 is the end point rather than the size of the change. 'Rise to' takes the final value; 'rise by' takes the difference, which here is 66 terawatt-hours. Ukrainian expresses the difference with 'на', which maps onto 'by', so this pair repays deliberate memorisation.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["last.Wind", "first.Wind", "delta.Wind"],
        "ua": "'Rose to 68' — кінцеве значення. 'Rose by 66' — величина зміни. Українське 'на 66' = 'by 66'.",
    },
    {
        "family": "line_graph", "type": "paragraph_ordering", "visual": "W1V-LINE-01",
        "prompt": "Arrange these four paragraphs into a correctly structured Task 1 report.",
        "items": [
            {"id": "p-body-a", "text": "Oslo and Bergen followed almost identical paths. Oslo rose from 28 to 46 per cent and Bergen from 31 to 44 per cent, so the small gap between them narrowed and then reversed."},
            {"id": "p-intro", "text": "The line graph compares the proportion of household waste recycled in Oslo, Bergen and Tromso at five-year intervals between 2005 and 2025."},
            {"id": "p-body-b", "text": "Tromso, by contrast, began lowest at 18 per cent but climbed without interruption to 61 per cent, passing both other cities between 2010 and 2015."},
            {"id": "p-overview", "text": "Overall, recycling rates improved in all three cities, but the increase in Tromso was far steeper than elsewhere and it finished the period as the strongest performer."},
        ],
        "order": ["p-intro", "p-overview", "p-body-a", "p-body-b"],
        "explanation": "A Task 1 report opens by paraphrasing the task statement, follows immediately with an overview containing no figures, and only then divides the detail into grouped body paragraphs. Placing the overview after the detail, or leaving it out entirely, is the single most common structural loss in otherwise competent responses. The two body paragraphs here follow the grouping the graph itself suggests: the two similar cities together, the outlier separately.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["first.Oslo", "last.Oslo", "first.Bergen", "last.Bergen", "first.Tromso", "last.Tromso"],
        "ua": "Порядок завжди той самий: перефразоване завдання, overview без цифр, далі згруповані body-абзаци.",
    },

    # ======================= BAR CHARTS =======================
    {
        "family": "bar_chart", "type": "feature_selection", "visual": "W1V-BAR-01",
        "prompt": "Which detail from this chart most deserves a place in your report?",
        "options": [
            "Cultural visits is the only category that rises with age, and it overtakes live events in the oldest group.",
            "Streaming services cost 15 pounds a week in the 18-29 group.",
            "There are four leisure categories and three age groups.",
            "Eating out is the highest category for the 18-29 group.",
        ],
        "answer": "Cultural visits is the only category that rises with age, and it overtakes live events in the oldest group.",
        "distractors": {
            "Streaming services cost 15 pounds a week in the 18-29 group.": "One bar read in isolation. It is accurate but carries no comparison, and a grouped bar chart is scored on comparison.",
            "There are four leisure categories and three age groups.": "This describes the design of the chart rather than its content. Counting the bars is not reporting the data.",
            "Eating out is the highest category for the 18-29 group.": "True, but eating out leads every age group. Attaching the observation to one group alone understates a pattern that actually runs across the whole chart.",
        },
        "explanation": "The chart is deliberately built so that three categories fall with age and exactly one rises. That reversal, which puts cultural visits at 22 pounds against live events at 8 pounds in the oldest group, is the feature the task was constructed to test. It cannot be seen from any single bar.",
        "errorCategory": "list_like_description",
        "grounding": ["value.Cultural visits.50 and over", "value.Live events.50 and over", "value.Cultural visits.18-29", "value.Live events.18-29"],
        "ua": "У згрупованій діаграмі ключова ознака — це порушення порядку, а не найвищий стовпчик.",
    },
    {
        "family": "bar_chart", "type": "overview_selection", "visual": "W1V-BAR-01",
        "prompt": "Which sentence works best as the overview paragraph for this chart?",
        "options": [
            "Eating out attracted the most spending in every age group, but the ranking of the other categories reversed with age, as live events and streaming fell while cultural visits rose.",
            "Eating out fell from 42 to 31 pounds, live events from 27 to 8 pounds, streaming from 15 to 6 pounds, and cultural visits rose from 9 to 22 pounds.",
            "Younger people clearly enjoy going out more than older people do.",
            "Older people spend less on leisure because they have less disposable income.",
        ],
        "answer": "Eating out attracted the most spending in every age group, but the ranking of the other categories reversed with age, as live events and streaming fell while cultural visits rose.",
        "distractors": {
            "Eating out fell from 42 to 31 pounds, live events from 27 to 8 pounds, streaming from 15 to 6 pounds, and cultural visits rose from 9 to 22 pounds.": "Every figure is correct, but an overview that recites four sets of numbers has become a body paragraph and leaves nothing for the body to do.",
            "Younger people clearly enjoy going out more than older people do.": "The chart measures spending, not enjoyment. Converting a financial measure into a preference is an inference the data does not license.",
            "Older people spend less on leisure because they have less disposable income.": "Income is nowhere in the chart. This supplies a cause the graphic cannot evidence, and it is not even true of every category, since cultural visits rise.",
        },
        "explanation": "The overview has to hold the constant and the variation at the same time: one category leads everywhere, and the rest reorder themselves as age increases. Stating both, with no figures, gives the reader the shape of the chart in a single sentence.",
        "errorCategory": "missing_overview",
        "grounding": ["top.18-29", "top.30-49", "top.50 and over", "delta.Cultural visits", "delta.Live events"],
        "ua": "В overview тримайте одночасно те, що незмінне, і те, що змінюється. Без цифр.",
    },
    {
        "family": "bar_chart", "type": "grouping", "visual": "W1V-BAR-01",
        "prompt": "Which plan groups the four categories most effectively?",
        "options": [
            "One paragraph for the three categories that decline with age, and one for the single category that rises.",
            "One paragraph per category, taken in legend order.",
            "One paragraph per age group, listing all four categories in each.",
            "One paragraph for the highest and lowest figures, and one for everything in between.",
        ],
        "answer": "One paragraph for the three categories that decline with age, and one for the single category that rises.",
        "distractors": {
            "One paragraph per category, taken in legend order.": "Four paragraphs in the order the legend happens to list them produces a list, not a comparison, and legend order carries no meaning.",
            "One paragraph per age group, listing all four categories in each.": "This forces every category to be described three times and buries the one pattern worth reporting under repetition.",
            "One paragraph for the highest and lowest figures, and one for everything in between.": "Grouping by size rather than by behaviour separates categories that move together and joins categories that do not.",
        },
        "explanation": "Eating out, live events and streaming all fall as age rises, so they share a paragraph and a single topic sentence. Cultural visits moves the other way, so it earns the contrast paragraph. Grouping by behaviour is what turns four descriptions into two comparisons.",
        "errorCategory": "list_like_description",
        "grounding": ["delta.Eating out", "delta.Live events", "delta.Streaming services", "delta.Cultural visits"],
        "ua": "Об'єднуйте категорії, що рухаються однаково, і виносьте виняток в окремий абзац.",
    },
    {
        "family": "bar_chart", "type": "trend_language", "visual": "W1V-BAR-01",
        "prompt": "How is spending on live events across the three age groups best described?",
        "options": [
            "falling sharply and consistently, ending at less than a third of its level in the youngest group",
            "falling marginally across the three groups",
            "remaining broadly stable across the three groups",
            "falling and then recovering in the oldest group",
        ],
        "answer": "falling sharply and consistently, ending at less than a third of its level in the youngest group",
        "distractors": {
            "falling marginally across the three groups": "'Marginally' would fit a change of a pound or two. This category loses most of its value between the youngest and oldest groups.",
            "remaining broadly stable across the three groups": "Directly contradicted: the figure moves from 27 pounds to 8 pounds.",
            "falling and then recovering in the oldest group": "There is no recovery. The figure falls at each step, from 27 to 18 to 8 pounds.",
        },
        "explanation": "Live events falls from 27 pounds to 18 and then to 8, so the movement is both large and uninterrupted, and 8 is comfortably under a third of 27. Matching the adverb and the fraction to the actual figures is exactly what quantity language is scored on.",
        "errorCategory": "imprecise_quantity",
        "grounding": ["value.Live events.18-29", "value.Live events.30-49", "value.Live events.50 and over"],
        "ua": "Перед тим як написати частку ('a third', 'half'), перевірте її обчисленням.",
    },
    {
        "family": "bar_chart", "type": "comparison_building", "visual": "W1V-BAR-02",
        "prompt": "Which comparison is fully supported by this chart?",
        "options": [
            "Amsterdam and Copenhagen sat close together at the top, and the gap between Copenhagen and Munich was wider than that between any other neighbouring pair.",
            "Dublin and Naples had almost identical rates.",
            "Lyon's cycling rate rose over the period.",
            "Cycling is more popular in northern Europe than in southern Europe.",
        ],
        "answer": "Amsterdam and Copenhagen sat close together at the top, and the gap between Copenhagen and Munich was wider than that between any other neighbouring pair.",
        "distractors": {
            "Dublin and Naples had almost identical rates.": "Dublin's 9 per cent is more than double Naples's 4 per cent. In a chart where the top figure is 48 per cent the gap looks small, but 'almost identical' misreports the relationship.",
            "Lyon's cycling rate rose over the period.": "There is no period. The chart shows a single year, so no change over time can be claimed from it at all.",
            "Cycling is more popular in northern Europe than in southern Europe.": "Six cities cannot support a claim about two regions. The chart names the cities it measured and nothing beyond them.",
        },
        "explanation": "Amsterdam at 48 and Copenhagen at 44 per cent are four points apart, while Copenhagen to Munich is a drop of 23 points, larger than any other step in the ranking. Identifying where the ranking breaks is far more valuable than reciting the order, and it is directly checkable against the bars.",
        "errorCategory": "invalid_comparison",
        "grounding": ["value.Cycle to work.Amsterdam", "value.Cycle to work.Copenhagen", "value.Cycle to work.Munich", "value.Cycle to work.Dublin", "value.Cycle to work.Naples", "change.Cycle to work.Amsterdam.Copenhagen", "change.Cycle to work.Copenhagen.Munich"],
        "ua": "Одна діаграма за один рік не дозволяє говорити про зміну в часі. І шість міст — це не 'Європа'.",
    },
    {
        "family": "bar_chart", "type": "data_to_sentence", "visual": "W1V-BAR-02",
        "prompt": "Complete the sentence with one word so that it reports the chart accurately.",
        "sentence": "Naples recorded the ____ proportion of cycle commuters, at 4 per cent.",
        "answer": "lowest",
        "accept": ["lowest", "smallest"],
        "explanation": "'Lowest' and 'smallest' both work with a proportion at the bottom of a ranking. 'Fewest' cannot modify an uncountable proportion, and 'least' would need a different structure such as 'the least popular option'. Getting the superlative form right is a small but visible marker of control.",
        "errorCategory": "imprecise_quantity",
        "grounding": ["value.Cycle to work.Naples", "bottom.Naples"],
        "ua": "'Proportion' незлічуваний, тому 'fewest' не підходить. Використовуйте 'lowest' або 'smallest'.",
    },
    {
        "family": "bar_chart", "type": "paraphrase_no_distortion", "visual": "W1V-BAR-03",
        "prompt": "Original: 'Rail was the only mode whose freight volume fell, dropping from 310 to 240 million tonnes.' Which paraphrase preserves the meaning exactly?",
        "options": [
            "Every mode except rail carried more freight in 2020 than in 1990; rail alone declined, shedding 70 million tonnes.",
            "Rail freight halved between 1990 and 2020.",
            "Rail was the smallest freight mode in 2020.",
            "Rail freight declined slightly, from 310 to 240 million tonnes.",
        ],
        "answer": "Every mode except rail carried more freight in 2020 than in 1990; rail alone declined, shedding 70 million tonnes.",
        "distractors": {
            "Rail freight halved between 1990 and 2020.": "A fall from 310 to 240 million tonnes is nowhere near a halving. This is a magnitude distortion, and it is the kind an examiner notices immediately.",
            "Rail was the smallest freight mode in 2020.": "Air carried 48 million tonnes in 2020, well below rail's 240. The paraphrase has replaced a claim about direction with a false claim about rank.",
            "Rail freight declined slightly, from 310 to 240 million tonnes.": "The figures are correct but 'slightly' misrepresents a fall of 70 million tonnes. A synonym that changes the degree changes the data.",
        },
        "explanation": "The safe paraphrase keeps three things fixed: the direction (a fall), the size (70 million tonnes) and the uniqueness (rail alone). Each wrong option preserves the wording and quietly moves one of those three, which is precisely how lexical variation turns into data distortion.",
        "errorCategory": "lexical_distortion",
        "grounding": ["delta.Rail", "first.Rail", "last.Rail", "last.Air", "delta.Road", "delta.Water", "delta.Air"],
        "ua": "Перефразування має зберігати три речі: напрям, величину і винятковість. Змініть одне — і це вже інші дані.",
    },
    {
        "family": "bar_chart", "type": "sentence_correction", "visual": "W1V-BAR-03",
        "prompt": "This sentence contains a reporting fault: 'Road freight increased dramatically because more goods were bought online.' Which correction repairs it?",
        "options": [
            "Road freight increased sharply, from 620 to 980 million tonnes.",
            "Road freight increased dramatically, which shows the growth of online shopping.",
            "Road freight increased slightly, from 620 to 980 million tonnes.",
            "Road freight probably increased because of the growth of online shopping.",
        ],
        "answer": "Road freight increased sharply, from 620 to 980 million tonnes.",
        "distractors": {
            "Road freight increased dramatically, which shows the growth of online shopping.": "The causal claim has been relabelled as evidence, which makes it stronger rather than weaker. The chart shows tonnage, and nothing about how the goods were ordered.",
            "Road freight increased slightly, from 620 to 980 million tonnes.": "The cause has gone but a new fault has arrived: a rise of 360 million tonnes is not slight.",
            "Road freight probably increased because of the growth of online shopping.": "Hedging with 'probably' does not license a cause the chart cannot show, and it also weakens a rise the chart states as fact.",
        },
        "explanation": "The original reports a real movement and then explains it with information the chart does not contain. The repair keeps the movement, sizes it correctly against a rise of 360 million tonnes, and simply stops where the data stops.",
        "errorCategory": "unsupported_causal_claim",
        "grounding": ["first.Road", "last.Road", "delta.Road"],
        "ua": "Діаграма показує обсяг, а не причину. Прибрати причину і залишити точну величину — це і є виправлення.",
    },
    {
        "family": "bar_chart", "type": "grammar_correction", "visual": "W1V-BAR-03",
        "prompt": "One word is missing. Type the single word that belongs in the gap.",
        "sentence": "Road accounted for ____ largest share of freight in both years.",
        "answer": "the",
        "accept": ["the"],
        "explanation": "A superlative always takes the definite article: 'the largest share'. Ukrainian has no articles at all, so this omission survives into otherwise advanced writing and is one of the most visible transfer errors in Task 1. Checking every superlative for its article is a fast, high-value proofreading habit.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["top.1990", "top.2020"],
        "ua": "Перед найвищим ступенем завжди 'the': the largest, the highest, the most significant.",
    },
    {
        "family": "bar_chart", "type": "paragraph_ordering", "visual": "W1V-BAR-01",
        "prompt": "Arrange these four paragraphs into a correctly structured Task 1 report.",
        "items": [
            {"id": "p-body-rise", "text": "Cultural visits reversed this pattern, rising from 9 pounds among the youngest respondents to 22 pounds among those aged 50 and over, and overtaking live events in the process."},
            {"id": "p-overview", "text": "Overall, eating out attracted the highest spending in every age group, while the remaining categories divided sharply: most declined as age increased, but one moved in the opposite direction."},
            {"id": "p-intro", "text": "The bar chart compares average weekly spending on four leisure activities among three age groups."},
            {"id": "p-body-fall", "text": "Spending fell with age in three categories. Eating out declined from 42 to 31 pounds a week, live events from 27 to 8 pounds, and streaming services from 15 to 6 pounds."},
        ],
        "order": ["p-intro", "p-overview", "p-body-fall", "p-body-rise"],
        "explanation": "The introduction paraphrases the task, the overview states the constant and the split without figures, and the two body paragraphs then follow the grouping the overview promised: the declining categories together, the rising one in contrast. Note that the contrast paragraph comes second, so the report ends on the feature that makes the chart interesting.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["value.Eating out.18-29", "value.Eating out.50 and over", "value.Live events.18-29", "value.Live events.50 and over", "value.Cultural visits.18-29", "value.Cultural visits.50 and over", "value.Streaming services.18-29", "value.Streaming services.50 and over"],
        "ua": "Абзац із винятком ставте останнім — так звіт завершується найважливішою ознакою.",
    },

    # ======================= PIE CHARTS =======================
    {
        "family": "pie_chart", "type": "feature_selection", "visual": "W1V-PIE-01",
        "prompt": "Which detail from this chart most deserves a place in your report?",
        "options": [
            "Bathing and toilet flushing together accounted for well over half of all household water use.",
            "Garden watering accounted for 8 per cent.",
            "The chart is divided into six categories.",
            "Kitchen and drinking used more water than garden watering.",
        ],
        "answer": "Bathing and toilet flushing together accounted for well over half of all household water use.",
        "distractors": {
            "Garden watering accounted for 8 per cent.": "A single small slice with no relationship attached. Accurate, but it tells the reader nothing about the shape of the distribution.",
            "The chart is divided into six categories.": "This counts the slices instead of reading them. Describing the graphic is not describing the data.",
            "Kitchen and drinking used more water than garden watering.": "True, but it compares the fourth largest slice with the fifth. The relationship is real and completely unimportant.",
        },
        "explanation": "Bathing and showering at 34 per cent and toilet flushing at 26 per cent are the two dominant uses, and combining them is what converts six separate readings into a single reportable pattern. A pie chart rewards aggregation: the useful sentence is almost always about several slices at once.",
        "errorCategory": "list_like_description",
        "grounding": ["share.Bathing and showering.2024", "share.Toilet flushing.2024", "largest.2024"],
        "ua": "Кругова діаграма винагороджує об'єднання часток. Найкорисніше речення майже завжди про кілька секторів разом.",
    },
    {
        "family": "pie_chart", "type": "overview_selection", "visual": "W1V-PIE-02",
        "prompt": "Which sentence works best as the overview paragraph for these two charts?",
        "options": [
            "Overall, the composition of waste became more evenly spread: organic material remained the largest component but lost ground, while plastics grew to become the second largest.",
            "Organic waste fell from 42 to 31 per cent, paper from 24 to 15 per cent, and plastics rose from 12 to 26 per cent.",
            "The city produced considerably more waste in 2020 than in 2000.",
            "The city's recycling policies clearly failed over the twenty-year period.",
        ],
        "answer": "Overall, the composition of waste became more evenly spread: organic material remained the largest component but lost ground, while plastics grew to become the second largest.",
        "distractors": {
            "Organic waste fell from 42 to 31 per cent, paper from 24 to 15 per cent, and plastics rose from 12 to 26 per cent.": "Correct figures in the wrong paragraph. This is the body of the report, and using it as an overview leaves the overview slot empty.",
            "The city produced considerably more waste in 2020 than in 2000.": "The charts show shares of a total, never the total itself. Nothing here can establish whether the quantity of waste rose, fell or stayed the same.",
            "The city's recycling policies clearly failed over the twenty-year period.": "An evaluation, and one the data cannot support in either direction. Task 1 never assesses whether an outcome was good or bad.",
        },
        "explanation": "The overview should describe what happened to the distribution as a whole. Here the leading share falls from 42 to 31 per cent while the third largest more than doubles, so the mixture flattens out. Naming that flattening, and the change of rank behind it, covers both charts in one sentence without listing a single category.",
        "errorCategory": "missing_overview",
        "grounding": ["largest.2000", "largest.2020", "share.Organic.2000", "share.Organic.2020", "share.Plastics.2000", "share.Plastics.2020"],
        "ua": "Найпоширеніша пастка: сказати, що обсяг сміття зріс. Діаграма показує лише частки, а не загальну кількість.",
    },
    {
        "family": "pie_chart", "type": "grouping", "visual": "W1V-PIE-02",
        "prompt": "Which plan groups the six categories most effectively?",
        "options": [
            "One paragraph for the three categories that shifted by nine percentage points or more, and one for the remainder, which barely moved.",
            "One paragraph for the 2000 chart and one for the 2020 chart.",
            "One paragraph per category, in legend order.",
            "One paragraph for the largest slices and one for the smallest, regardless of how they changed.",
        ],
        "answer": "One paragraph for the three categories that shifted by nine percentage points or more, and one for the remainder, which barely moved.",
        "distractors": {
            "One paragraph for the 2000 chart and one for the 2020 chart.": "This forces all six categories to be described twice and leaves the reader to work out the changes themselves. With paired pies, the change is the content.",
            "One paragraph per category, in legend order.": "Six paragraphs, each about one slice, is the purest form of list-like description and it will not fit the word count either.",
            "One paragraph for the largest slices and one for the smallest, regardless of how they changed.": "Size at a single moment is the wrong grouping criterion for paired charts, because it separates categories that behaved alike.",
        },
        "explanation": "Organic loses 11 points, paper loses 9 and plastics gains 14, while glass and metal each move only 1 point and other gains 4. Splitting the movers from the stable categories gives two paragraphs with a genuine topic sentence each, and it is the grouping the data itself suggests rather than one imposed on it.",
        "errorCategory": "list_like_description",
        "grounding": ["delta_share.Organic", "delta_share.Paper", "delta_share.Plastics", "delta_share.Glass", "delta_share.Metal", "delta_share.Other"],
        "ua": "З парними діаграмами групуйте за величиною зміни, а не за розміром сектора.",
    },
    {
        "family": "pie_chart", "type": "trend_language", "visual": "W1V-PIE-02",
        "prompt": "Which sentence describes the change in the plastics category most accurately?",
        "options": [
            "The share of plastics more than doubled, climbing by 14 percentage points.",
            "Plastic waste more than doubled over the period.",
            "The share of plastics rose by 14 per cent.",
            "The share of plastics rose marginally.",
        ],
        "answer": "The share of plastics more than doubled, climbing by 14 percentage points.",
        "distractors": {
            "Plastic waste more than doubled over the period.": "This converts a share into a quantity. Without the total tonnage, a bigger slice does not prove more plastic, and the charts never show the total.",
            "The share of plastics rose by 14 per cent.": "The difference between two percentages is measured in percentage points, not per cent. A rise 'by 14 per cent' from 12 would reach about 13.7, not 26.",
            "The share of plastics rose marginally.": "A movement from 12 to 26 per cent is the largest change on either chart. 'Marginally' inverts the significance of the finding.",
        },
        "explanation": "Plastics moves from 12 to 26 per cent, so the share more than doubles and the correct unit for the gap is percentage points. Two separate precision decisions are being tested at once here: share against quantity, and percentage points against per cent. Both are routine sources of avoidable loss.",
        "errorCategory": "lexical_distortion",
        "grounding": ["share.Plastics.2000", "share.Plastics.2020", "delta_share.Plastics"],
        "ua": "Різниця між двома відсотками — це 'percentage points', а не 'per cent'. І більша частка не доводить більший обсяг.",
    },
    {
        "family": "pie_chart", "type": "comparison_building", "visual": "W1V-PIE-03",
        "prompt": "Which comparison is fully supported by this chart?",
        "options": [
            "Career advancement was named by well over a third of students, making it the most common reason by a clear margin over interest in the subject.",
            "Career advancement was cited by more than three times as many students as employer sponsorship.",
            "Family expectation and other reasons together accounted for more than a fifth of responses.",
            "Students who chose the institution for its reputation also valued career advancement.",
        ],
        "answer": "Career advancement was named by well over a third of students, making it the most common reason by a clear margin over interest in the subject.",
        "distractors": {
            "Career advancement was cited by more than three times as many students as employer sponsorship.": "38 per cent against 14 per cent is under three times, not more than three. Multipliers should be checked with arithmetic before they are written down.",
            "Family expectation and other reasons together accounted for more than a fifth of responses.": "Those two categories total 12 per cent, well under a fifth. Combining small slices is a good instinct, but the sum still has to be correct.",
            "Students who chose the institution for its reputation also valued career advancement.": "A pie chart of single main reasons cannot show any overlap between categories. This claims a relationship the chart is structurally incapable of containing.",
        },
        "explanation": "At 38 per cent, career advancement is above a third and 14 points clear of interest in the subject at 24 per cent, so both halves of the statement are directly readable. Each wrong option fails on a different kind of arithmetic or logic, which is why comparison building is worth practising as its own skill rather than as part of general description.",
        "errorCategory": "invalid_comparison",
        "grounding": ["share.Career advancement.2024", "share.Interest in the subject.2024", "share.Employer sponsorship.2024", "share.Family expectation.2024", "share.Other.2024", "largest.2024"],
        "ua": "Перед тим як писати 'three times' або 'more than a fifth', перевірте це арифметикою.",
    },
    {
        "family": "pie_chart", "type": "data_to_sentence", "visual": "W1V-PIE-03",
        "prompt": "Complete the sentence with one word so that it uses the standard collocation for describing a share.",
        "sentence": "Employer sponsorship ____ for 14 per cent of responses.",
        "answer": "accounted",
        "accept": ["accounted"],
        "explanation": "'Account for' is the standard academic collocation for a share, and it takes no extra preposition before the figure. 'Composed' and 'consisted' would both need the sentence restructured, and 'comprised for' is not English. Fixing two or three of these frames precisely is worth more than a wide but unreliable range.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["share.Employer sponsorship.2024"],
        "ua": "'Accounted for 14 per cent' — без додаткового прийменника. Українське 'становити' прийменника не має, тому 'for' часто губиться.",
    },
    {
        "family": "pie_chart", "type": "paraphrase_no_distortion", "visual": "W1V-PIE-01",
        "prompt": "Original: 'Bathing and showering was the single largest use of household water, at 34 per cent.' Which paraphrase preserves the meaning exactly?",
        "options": [
            "Just over a third of household water was used for bathing and showering, more than for any other single purpose.",
            "Bathing and showering used almost half of all household water.",
            "Bathing and showering was one of the largest uses of household water, at around 34 per cent.",
            "Roughly a third of households used water mainly for bathing and showering.",
        ],
        "answer": "Just over a third of household water was used for bathing and showering, more than for any other single purpose.",
        "distractors": {
            "Bathing and showering used almost half of all household water.": "34 per cent is not close to half. 'Almost half' would suit a figure in the mid-forties.",
            "Bathing and showering was one of the largest uses of household water, at around 34 per cent.": "'One of the largest' quietly demotes a category that was actually the largest. Hedging can distort just as badly as exaggeration.",
            "Roughly a third of households used water mainly for bathing and showering.": "The subject has changed from water to households. The chart divides up the water, and says nothing about how many homes behave in any particular way.",
        },
        "explanation": "Three things have to survive the rewrite: the size (34 per cent, just over a third), the rank (largest, not merely large) and the subject (water, not households). The distractors each break exactly one of them, which is how a fluent-sounding paraphrase can still be marked as inaccurate.",
        "errorCategory": "lexical_distortion",
        "grounding": ["share.Bathing and showering.2024", "largest.2024"],
        "ua": "У перефразуванні мають вціліти три речі: величина, ранг і підмет. Заміна 'води' на 'домогосподарства' — вже помилка.",
    },
    {
        "family": "pie_chart", "type": "sentence_correction", "visual": "W1V-PIE-02",
        "prompt": "This sentence contains two faults: 'Organic waste decreased significantly, which is a good sign for the environment.' Which correction repairs both?",
        "options": [
            "The share of organic waste decreased significantly, from 42 to 31 per cent.",
            "Organic waste decreased significantly, from 42 to 31 per cent.",
            "The share of organic waste decreased, which is a good sign for the environment.",
            "Organic waste decreased slightly, from 42 to 31 per cent.",
        ],
        "answer": "The share of organic waste decreased significantly, from 42 to 31 per cent.",
        "distractors": {
            "Organic waste decreased significantly, from 42 to 31 per cent.": "The evaluation is gone but the quantity claim survives. Without the total, only the share can be said to have fallen.",
            "The share of organic waste decreased, which is a good sign for the environment.": "The reverse fix: the share is now correctly identified, but the judgement remains, and Task 1 does not judge.",
            "Organic waste decreased slightly, from 42 to 31 per cent.": "Both original faults are still present in effect, and a third has been added, since a fall of 11 points is not slight.",
        },
        "explanation": "Two independent faults have to be repaired together, which is what makes this a timed item. 'A good sign' is an evaluation with no place in a report, and 'organic waste decreased' asserts a fall in quantity when the chart only shows a fall in share. Options b and c each fix one and leave the other.",
        "errorCategory": "personal_opinion",
        "grounding": ["share.Organic.2000", "share.Organic.2020", "delta_share.Organic"],
        "ua": "Дві помилки одночасно: оцінка ('a good sign') і підміна частки обсягом. Виправляти треба обидві.",
    },
    {
        "family": "pie_chart", "type": "grammar_correction", "visual": "W1V-PIE-01",
        "prompt": "One word is missing. Type the single word that belongs in the gap.",
        "sentence": "Laundry accounted ____ 16 per cent of household water use.",
        "answer": "for",
        "accept": ["for"],
        "explanation": "'Account' requires 'for' before the figure. The Ukrainian equivalent 'становити' takes no preposition, so the word is routinely dropped or replaced with 'of' even by strong writers. Because this frame appears in almost every pie chart response, the error is unusually visible when it occurs.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["share.Laundry.2024"],
        "ua": "'Account' завжди з 'for'. Українське 'становити' прийменника не потребує — звідси й помилка.",
    },
    {
        "family": "pie_chart", "type": "paragraph_ordering", "visual": "W1V-PIE-02",
        "prompt": "Arrange these four paragraphs into a correctly structured Task 1 report.",
        "items": [
            {"id": "p-body-stable", "text": "The remaining categories were far more stable. Glass edged up from 9 to 10 per cent and metal from 7 to 8 per cent, while other waste rose from 6 to 10 per cent."},
            {"id": "p-intro", "text": "The two pie charts compare the composition of municipal waste in one city in 2000 and in 2020."},
            {"id": "p-body-movers", "text": "The three categories that moved most were organic, paper and plastics. Organic waste fell from 42 to 31 per cent and paper from 24 to 15 per cent, while plastics climbed from 12 to 26 per cent."},
            {"id": "p-overview", "text": "Overall, the mixture became noticeably more even. Organic material remained the largest component throughout, but its dominance weakened, while plastics rose to become the second largest category."},
        ],
        "order": ["p-intro", "p-overview", "p-body-movers", "p-body-stable"],
        "explanation": "Introduction, then an overview describing the distribution as a whole with no figures, then the detail split by how much each category moved. The movers come before the stable categories because a reader who has just been told the mixture flattened wants to see the evidence for that first; the stable group then closes the report by confirming the contrast.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["share.Organic.2000", "share.Organic.2020", "share.Paper.2000", "share.Paper.2020", "share.Plastics.2000", "share.Plastics.2020", "share.Glass.2000", "share.Glass.2020", "share.Metal.2000", "share.Metal.2020", "share.Other.2000", "share.Other.2020"],
        "ua": "Спершу категорії, що змінилися найбільше, потім стабільні. Так звіт підтверджує overview у правильному порядку.",
    },

    # ========================== TABLES ==========================
    {
        "family": "table", "type": "feature_selection", "visual": "W1V-TAB-01",
        "prompt": "Which detail from this table most deserves a place in your report?",
        "options": [
            "Arrivals rose in every destination except Riverford, while the average stay shortened everywhere except Highland Park.",
            "Lakeside received 2.7 million arrivals in 2019.",
            "The table sets five destinations against four columns of figures.",
            "Coastal Bay's average stay fell from 6.8 to 5.9 nights.",
        ],
        "answer": "Arrivals rose in every destination except Riverford, while the average stay shortened everywhere except Highland Park.",
        "distractors": {
            "Lakeside received 2.7 million arrivals in 2019.": "One cell out of twenty, with no comparison attached. A table is scored on what you leave out as much as what you put in.",
            "The table sets five destinations against four columns of figures.": "This describes the layout rather than the data. Counting rows and columns is not selection.",
            "Coastal Bay's average stay fell from 6.8 to 5.9 nights.": "Accurate, and it is one instance of a pattern that covers four of the five destinations. Reporting the instance instead of the pattern spends the overview on a detail.",
        },
        "explanation": "A table over-supplies data deliberately. The reportable feature is the direction each measure took overall, together with the single exception to each, because that compresses twenty figures into one sentence. Selection, not coverage, is the skill this family tests.",
        "errorCategory": "list_like_description",
        "grounding": ["value.Riverford.Arrivals 2019 (m)", "value.Riverford.Arrivals 2023 (m)", "value.Highland Park.Stay 2019 (nights)", "value.Highland Park.Stay 2023 (nights)", "value.Coastal Bay.Stay 2019 (nights)", "value.Coastal Bay.Stay 2023 (nights)"],
        "allowedNumbers": [4, 5],
        "allowedNumbersReason": "Counts of destinations and columns, not data claims.",
        "ua": "Таблиця навмисно дає більше даних, ніж потрібно. Оцінюється вміння відкинути зайве, а не охопити все.",
    },
    {
        "family": "table", "type": "overview_selection", "visual": "W1V-TAB-01",
        "prompt": "Which sentence works best as the overview paragraph for this table?",
        "options": [
            "Overall, most destinations attracted more visitors in 2023 than in 2019, yet visitors tended to stay for shorter periods, so the two measures generally moved in opposite directions.",
            "Old Harbour had the most arrivals in both years, Highland Park the fewest, and Riverford the shortest average stay in 2023.",
            "Tourism had fully recovered from the disruption of the previous years by 2023.",
            "Highland Park is clearly the best destination for a longer holiday.",
        ],
        "answer": "Overall, most destinations attracted more visitors in 2023 than in 2019, yet visitors tended to stay for shorter periods, so the two measures generally moved in opposite directions.",
        "distractors": {
            "Old Harbour had the most arrivals in both years, Highland Park the fewest, and Riverford the shortest average stay in 2023.": "Three correct superlatives, but an overview is not a list of record holders. Nothing here tells the reader what the table as a whole is doing.",
            "Tourism had fully recovered from the disruption of the previous years by 2023.": "The table gives two dates and no context. Nothing in it establishes what the figures are recovering from, or whether recovery is complete.",
            "Highland Park is clearly the best destination for a longer holiday.": "A recommendation. Task 1 never advises the reader which option to choose.",
        },
        "explanation": "The strongest overview finds the relationship between the two measures rather than describing them separately: arrivals up, stays down. Because that holds for four destinations out of five in each case, 'most' and 'generally' are the honest quantifiers, and the exceptions can then be named in the body.",
        "errorCategory": "missing_overview",
        "grounding": ["value.Coastal Bay.Arrivals 2019 (m)", "value.Coastal Bay.Arrivals 2023 (m)", "value.Riverford.Arrivals 2019 (m)", "value.Riverford.Arrivals 2023 (m)", "value.Highland Park.Stay 2023 (nights)"],
        "ua": "Найсильніше overview для таблиці шукає зв'язок між двома вимірами, а не описує кожен окремо.",
    },
    {
        "family": "table", "type": "grouping", "visual": "W1V-TAB-01",
        "prompt": "Which plan organises this table most effectively?",
        "options": [
            "One paragraph on arrivals across all five destinations, and one on length of stay, naming the exception in each.",
            "One paragraph per destination, covering all four of its figures.",
            "One paragraph for 2019 and one for 2023.",
            "One paragraph for the largest destinations and one for the smallest, leaving length of stay aside.",
        ],
        "answer": "One paragraph on arrivals across all five destinations, and one on length of stay, naming the exception in each.",
        "distractors": {
            "One paragraph per destination, covering all four of its figures.": "Five paragraphs of four figures each is the table read aloud. It has no grouping, no comparison and no chance of fitting the word count.",
            "One paragraph for 2019 and one for 2023.": "This describes every destination twice and hides the changes, which are the only reason two dates were given.",
            "One paragraph for the largest destinations and one for the smallest, leaving length of stay aside.": "Dropping an entire measure means half the table goes unreported, which is a coverage failure regardless of how well the rest is written.",
        },
        "explanation": "When a table holds two distinct measures, the measures are the natural paragraphs: each one has a direction, and each one has an exception worth naming. That structure covers all twenty cells, keeps the comparison explicit, and leaves the word count comfortable.",
        "errorCategory": "list_like_description",
        "grounding": ["max.Arrivals 2023 (m)", "min.Arrivals 2023 (m)", "max.Stay 2023 (nights)", "min.Stay 2023 (nights)"],
        "allowedNumbers": [4, 5],
        "allowedNumbersReason": "Counts of destinations, columns and paragraphs, not data claims.",
        "ua": "Коли в таблиці два різні виміри, саме вони й стають абзацами.",
    },
    {
        "family": "table", "type": "trend_language", "visual": "W1V-TAB-01",
        "prompt": "How is Riverford's change in arrivals best described?",
        "options": [
            "the only destination to lose arrivals, falling by 0.8 million",
            "a marginal decline of 0.8 million, in line with the other destinations",
            "a collapse in visitor numbers",
            "a fall in arrivals caused by the shorter average stay",
        ],
        "answer": "the only destination to lose arrivals, falling by 0.8 million",
        "distractors": {
            "a marginal decline of 0.8 million, in line with the other destinations": "The figure is right but the framing is wrong twice: every other destination gained, so this is not in line with them, and being the sole exception is not marginal.",
            "a collapse in visitor numbers": "A fall from 3.9 to 3.1 million is significant but nowhere near a collapse. The adverb has to be sized to the movement.",
            "a fall in arrivals caused by the shorter average stay": "Length of stay and number of arrivals are separate columns. The table places them side by side; it does not connect them causally.",
        },
        "explanation": "Riverford drops from 3.9 to 3.1 million, a fall of 0.8 million, and it is the only destination to fall at all. What makes the figure worth reporting is its uniqueness, so the description has to carry that as well as the size. Note also how easily two adjacent columns invite an invented cause.",
        "errorCategory": "imprecise_quantity",
        "grounding": ["value.Riverford.Arrivals 2019 (m)", "value.Riverford.Arrivals 2023 (m)", "min.Arrivals 2023 (m)", "delta.Riverford.Arrivals 2019 (m).Arrivals 2023 (m)"],
        "ua": "Сусідні стовпці в таблиці спокушають вигадати причину. Опишіть величину і винятковість — і зупиніться.",
    },
    {
        "family": "table", "type": "comparison_building", "visual": "W1V-TAB-02",
        "prompt": "Which comparison is fully supported by this table?",
        "options": [
            "Northvale fell below the national average on all four components, whereas Metroport exceeded it on housing and food but not on transport or utilities.",
            "Southcliff was the most expensive city overall.",
            "Metroport's housing costs were more than twice Northvale's.",
            "Transport costs rose fastest in Southcliff.",
        ],
        "answer": "Northvale fell below the national average on all four components, whereas Metroport exceeded it on housing and food but not on transport or utilities.",
        "distractors": {
            "Southcliff was the most expensive city overall.": "The table gives four separate component indices and no combined figure. 'Overall' would require a total the table never provides.",
            "Metroport's housing costs were more than twice Northvale's.": "142 against 86 is under 1.7 times. Multipliers read from a chart by eye are frequently wrong and should always be checked.",
            "Transport costs rose fastest in Southcliff.": "There is no time dimension in this table at all. A single year cannot show anything rising.",
        },
        "explanation": "The supported comparison uses the reference point the table actually supplies, an index base of 100, and reports each city against it. Northvale's four figures are all under 100 and Metroport's split either side of it, both of which are directly readable. The distractors invent a total, a multiplier and a timeline that the table does not contain.",
        "errorCategory": "invalid_comparison",
        "grounding": ["value.Northvale.Housing", "value.Northvale.Transport", "value.Northvale.Food", "value.Northvale.Utilities", "value.Metroport.Housing", "value.Metroport.Transport", "value.Metroport.Food", "value.Metroport.Utilities"],
        "ua": "Якщо в таблиці немає підсумку, ви не можете писати 'overall'. Якщо немає часу — не можете писати 'rose'.",
    },
    {
        "family": "table", "type": "data_to_sentence", "visual": "W1V-TAB-02",
        "prompt": "Complete the sentence with one word so that the gap is sized accurately.",
        "sentence": "At 71, Northvale recorded the lowest transport index, ____ below the national average of 100.",
        "answer": "well",
        "accept": ["well", "far", "considerably", "substantially"],
        "explanation": "An intensifier is needed to size the gap: an index of 71 against a base of 100 is well or far below the average, not slightly below. Choosing the intensifier is where quantity language is actually scored, because the figures alone are visible to the reader anyway.",
        "errorCategory": "imprecise_quantity",
        "grounding": ["value.Northvale.Transport", "min.Transport"],
        "ua": "Саме підсилювач ('well', 'far', 'slightly') несе оцінку розміру. Числа читач і так бачить.",
    },
    {
        "family": "table", "type": "paraphrase_no_distortion", "visual": "W1V-TAB-03",
        "prompt": "Original: 'Services grew from 44 to 68 per cent of the workforce, remaining the largest sector throughout.' Which paraphrase preserves the meaning exactly?",
        "options": [
            "Services was the dominant sector in every year shown, and its share of the workforce rose by 24 percentage points.",
            "The number of service workers rose by 24 per cent.",
            "Services grew to become the largest sector by 2025.",
            "Services accounted for around two thirds of the workforce throughout the period.",
        ],
        "answer": "Services was the dominant sector in every year shown, and its share of the workforce rose by 24 percentage points.",
        "distractors": {
            "The number of service workers rose by 24 per cent.": "Two distortions. The table gives shares of the workforce, not numbers of workers, and the difference between two percentages is measured in points.",
            "Services grew to become the largest sector by 2025.": "'Grew to become' implies it was not the largest before. Services already led in 1995 at 44 per cent, so the rank did not change.",
            "Services accounted for around two thirds of the workforce throughout the period.": "68 per cent is close to two thirds, but 44 per cent is not. 'Throughout' applies the final figure to the whole period.",
        },
        "explanation": "The rewrite has to keep the size of the change, the unit it is measured in, the subject (share, not headcount) and the fact that the rank never changed. Each distractor preserves the fluency of the original and quietly breaks one of those four, which is what makes this the hardest paraphrase family to self-check.",
        "errorCategory": "lexical_distortion",
        "grounding": ["value.Services.1995", "value.Services.2025", "delta.Services.1995.2025", "max.1995", "max.2025"],
        "ua": "Перевіряйте чотири речі: величину, одиницю, підмет (частка чи кількість) і ранг.",
    },
    {
        "family": "table", "type": "sentence_correction", "visual": "W1V-TAB-03",
        "prompt": "This sentence contains two faults: 'Agriculture employment falls steadily and will continue to fall in the future.' Which correction repairs both?",
        "options": [
            "Employment in agriculture fell steadily, from 18 to 6 per cent of the workforce.",
            "Agricultural employment falls steadily, from 18 to 6 per cent of the workforce.",
            "Employment in agriculture fell steadily and is likely to continue falling.",
            "Employment in agriculture fell steadily, from 18 to 6 per cent, because farms became mechanised.",
        ],
        "answer": "Employment in agriculture fell steadily, from 18 to 6 per cent of the workforce.",
        "distractors": {
            "Agricultural employment falls steadily, from 18 to 6 per cent of the workforce.": "Figures added, but the present tense survives. Dated data that ends in 2025 requires past simple.",
            "Employment in agriculture fell steadily and is likely to continue falling.": "The tense is fixed but the projection remains. The table covers the years it covers and licenses no claim beyond them.",
            "Employment in agriculture fell steadily, from 18 to 6 per cent, because farms became mechanised.": "One fault has been swapped for another: the prediction is gone, but a cause the table cannot show has taken its place.",
        },
        "explanation": "Dated columns require past simple, and a table that stops at 2025 supports no statement about what happens afterwards. Both faults have to go in the same edit, and options c and d each demonstrate how removing one fault while introducing or retaining another leaves the sentence just as unreportable.",
        "errorCategory": "tense_misuse",
        "grounding": ["value.Agriculture.1995", "value.Agriculture.2025", "delta.Agriculture.1995.2025"],
        "ua": "Датована таблиця — минулий час. І жодних прогнозів за межі останнього стовпця.",
    },
    {
        "family": "table", "type": "grammar_correction", "visual": "W1V-TAB-03",
        "prompt": "One word is missing. Type the single verb form that belongs in the gap.",
        "sentence": "The share of the workforce employed in manufacturing ____ from 31 to 14 per cent between 1995 and 2025.",
        "answer": "fell",
        "accept": ["fell", "dropped", "declined", "decreased"],
        "explanation": "The subject is 'the share', which is singular, and the data is dated, so the verb has to be a past simple singular form. 'Have fallen' and 'falls' are the two most frequent slips, the first because the long noun phrase pulls the writer towards a plural, the second because a table can feel timeless even when its columns are dated.",
        "errorCategory": "tense_misuse",
        "grounding": ["value.Manufacturing.1995", "value.Manufacturing.2025", "delta.Manufacturing.1995.2025"],
        "ua": "Підмет тут 'the share' — однина. Довга іменникова група тягне до множини, і саме там виникає помилка узгодження.",
    },
    {
        "family": "table", "type": "paragraph_ordering", "visual": "W1V-TAB-03",
        "prompt": "Arrange these four paragraphs into a correctly structured Task 1 report.",
        "items": [
            {"id": "p-body-fall", "text": "The two contracting sectors moved in parallel. Manufacturing fell from 31 to 14 per cent and agriculture from 18 to 6 per cent, leaving agriculture as the smallest sector by the end of the period."},
            {"id": "p-overview", "text": "Overall, the region shifted decisively towards services, which expanded in every decade shown, while both agriculture and manufacturing contracted throughout."},
            {"id": "p-body-rise", "text": "Services grew from 44 per cent of the workforce in 1995 to 68 per cent in 2025, and public administration also rose, from 7 to 12 per cent."},
            {"id": "p-intro", "text": "The table shows how the proportion of the regional workforce employed in four sectors changed at ten-year intervals between 1995 and 2025."},
        ],
        "order": ["p-intro", "p-overview", "p-body-rise", "p-body-fall"],
        "explanation": "Introduction, overview without figures, then the detail grouped by direction: the two growing sectors together, the two shrinking sectors together. Grouping by direction rather than by sector turns four separate descriptions into two comparisons and gives each body paragraph a topic sentence it can actually earn.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["value.Services.1995", "value.Services.2025", "value.Public administration.1995", "value.Public administration.2025", "value.Manufacturing.1995", "value.Manufacturing.2025", "value.Agriculture.1995", "value.Agriculture.2025"],
        "ua": "Групуйте за напрямом руху: сектори, що зростають, разом; ті, що скорочуються, разом.",
    },
]

EXERCISES += [
    # ====================== PROCESS DIAGRAMS ======================
    {
        "family": "process_diagram", "type": "feature_selection", "visual": "W1V-PROC-01",
        "prompt": "Which detail from this diagram most deserves a place in your report?",
        "options": [
            "The process is a closed loop: new bottles return to the collection stage at which the diagram began.",
            "The third stage is called manual sorting.",
            "Lorries are used to move the glass to the plant.",
            "The furnace must reach a very high temperature to melt the cullet.",
        ],
        "answer": "The process is a closed loop: new bottles return to the collection stage at which the diagram began.",
        "distractors": {
            "The third stage is called manual sorting.": "Naming one stage in isolation reports a label rather than the process. Every stage will be covered in the body anyway.",
            "Lorries are used to move the glass to the plant.": "A minor implementation detail. It is shown, but it tells the reader nothing about how the process is organised.",
            "The furnace must reach a very high temperature to melt the cullet.": "This is not merely minor, it is invented. The diagram labels a melting stage but gives no temperature, and supplying one fabricates data.",
        },
        "explanation": "The cyclical shape is the one feature that belongs in the overview, because it describes the process as a whole rather than any single step. Note the difference between the three wrong options: two are true but trivial, and the last is not supported by the diagram at all, which is the more serious fault.",
        "errorCategory": "missing_overview",
        "grounding": ["cyclical", "first_stage", "last_stage", "stage_count"],
        "ua": "Для схеми процесу ключова ознака — форма цілого: лінійний він чи циклічний, з чого починається і чим завершується.",
    },
    {
        "family": "process_diagram", "type": "overview_selection", "visual": "W1V-PROC-01",
        "prompt": "Which sentence works best as the overview paragraph for this diagram?",
        "options": [
            "Overall, the recycling of glass bottles is a continuous cycle of eight distinct stages, beginning with the collection of used bottles and ending with new bottles that re-enter the same system.",
            "First the bottles are collected, then they are transported to a plant, and then they are sorted by hand.",
            "Recycling glass is an efficient and environmentally responsible way of reducing waste.",
            "The process consists of eight stages.",
        ],
        "answer": "Overall, the recycling of glass bottles is a continuous cycle of eight distinct stages, beginning with the collection of used bottles and ending with new bottles that re-enter the same system.",
        "distractors": {
            "First the bottles are collected, then they are transported to a plant, and then they are sorted by hand.": "This starts the sequence rather than summarising it. Three stages out of eight is a body paragraph that has begun in the wrong place.",
            "Recycling glass is an efficient and environmentally responsible way of reducing waste.": "An evaluation of the process, not a description of it. The diagram shows how the process works, not whether it is worthwhile.",
            "The process consists of eight stages.": "True but thin. A process overview should give the shape, the input and the output as well as the count.",
        },
        "explanation": "A process overview answers four questions at once: how many stages, what goes in, what comes out, and whether the sequence is linear or cyclical. Answering only one of them, as the last option does, leaves the reader without the framework the body paragraphs will hang on.",
        "errorCategory": "missing_overview",
        "grounding": ["stage_count", "input", "output", "cyclical"],
        "ua": "Overview для процесу: скільки етапів, що на вході, що на виході, лінійний чи циклічний.",
    },
    {
        "family": "process_diagram", "type": "grouping", "visual": "W1V-PROC-01",
        "prompt": "Which plan divides the eight stages most effectively?",
        "options": [
            "One paragraph for the stages that prepare the material, from collection to crushing, and one for the stages that remanufacture it, from melting to distribution.",
            "One paragraph for each of the eight stages.",
            "One paragraph for the stages performed by machines and one for those performed by people.",
            "One paragraph describing the diagram and one giving your assessment of glass recycling.",
        ],
        "answer": "One paragraph for the stages that prepare the material, from collection to crushing, and one for the stages that remanufacture it, from melting to distribution.",
        "distractors": {
            "One paragraph for each of the eight stages.": "Eight paragraphs for a 150-word report is impossible, and single-stage paragraphs cannot show sequence.",
            "One paragraph for the stages performed by machines and one for those performed by people.": "The diagram labels only one stage as manual. Sorting the rest into machine or human work means inventing information it does not give.",
            "One paragraph describing the diagram and one giving your assessment of glass recycling.": "The second paragraph has no place in Task 1 at all. There is no assessment stage in a report.",
        },
        "explanation": "Splitting at the furnace gives two coherent blocks: everything before it changes the form of the old glass, everything after it makes new glass from that material. A natural boundary in the process itself is always a better paragraph break than an arbitrary halfway point.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["stage.1", "stage.5", "stage.6", "stage.8", "stage_count"],
        "ua": "Ділити процес краще за природною межею (тут — піч), а не механічно навпіл.",
    },
    {
        "family": "process_diagram", "type": "trend_language", "visual": "W1V-PROC-01",
        "prompt": "Which sentence uses the correct voice and tense for this diagram?",
        "options": [
            "Once the glass has been separated by colour, it is crushed into cullet.",
            "Once the glass was separated by colour, it was crushed into cullet.",
            "Once workers separate the glass by colour, they crush it into cullet, which is faster than sorting by hand.",
            "Once the glass separates by colour, it crushes into cullet.",
        ],
        "answer": "Once the glass has been separated by colour, it is crushed into cullet.",
        "distractors": {
            "Once the glass was separated by colour, it was crushed into cullet.": "Past simple imports a timeframe the diagram never establishes. A process with no dates on it does not happen in the past.",
            "Once workers separate the glass by colour, they crush it into cullet, which is faster than sorting by hand.": "The voice is defensible but the comparison is invented. Nothing in the diagram measures speed.",
            "Once the glass separates by colour, it crushes into cullet.": "The active voice puts the glass in the agent position, so the material appears to sort and crush itself.",
        },
        "explanation": "A diagram with no dates takes present simple, and a man-made process takes the passive because the agent is unimportant and usually unshown. The present perfect passive in the subordinate clause is what marks one stage as complete before the next begins, which is exactly the sequencing relationship the diagram encodes.",
        "errorCategory": "tense_misuse",
        "grounding": ["stage.4", "stage.5", "cyclical"],
        "ua": "Немає дат — немає минулого часу. Рукотворний процес — пасив: 'is crushed', а не 'crushes'.",
    },
    {
        "family": "process_diagram", "type": "comparison_building", "visual": "W1V-PROC-02",
        "prompt": "Which statement is supported by this diagram?",
        "options": [
            "The salmon spends part of its life in fresh water and part in salt water, returning to fresh water to spawn.",
            "The salmon spends more years at sea than it does in the river.",
            "Most eggs do not survive as far as the smolt stage.",
            "The alevin and the fry are the same stage under two different names.",
        ],
        "answer": "The salmon spends part of its life in fresh water and part in salt water, returning to fresh water to spawn.",
        "distractors": {
            "The salmon spends more years at sea than it does in the river.": "The diagram gives no durations for any stage, so the two periods cannot be compared at all.",
            "Most eggs do not survive as far as the smolt stage.": "Survival rates are not shown. This imports biological knowledge from outside the graphic.",
            "The alevin and the fry are the same stage under two different names.": "They are shown as two separate stages, distinguished by whether the fish is still feeding on its yolk sac.",
        },
        "explanation": "The supported statement uses only what the diagram encodes: the location of each stage and the direction of travel between them. The three wrong options each reach for something the diagram does not carry, namely duration, survival rate and stage identity, and the first of those is the trap most advanced candidates fall into.",
        "errorCategory": "invalid_comparison",
        "grounding": ["stage.1", "stage.4", "stage.5", "stage.6", "cyclical"],
        "ua": "Схема показує послідовність і місце, але не тривалість. Порівняння за часом тут неможливе.",
    },
    {
        "family": "process_diagram", "type": "data_to_sentence", "visual": "W1V-PROC-02",
        "prompt": "Complete the sentence with one word so that the preposition of place is correct.",
        "sentence": "The smolt migrates downstream and enters salt water ____ the mouth of the river.",
        "answer": "at",
        "accept": ["at"],
        "explanation": "'At the mouth of the river' treats the location as a point on a route, which is what a migration stage needs. 'In the mouth' would place the fish inside an opening, and 'on' is not used with 'mouth' in this sense. Fixed prepositions of place are a recurring and easily avoidable loss in process descriptions.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["stage.4"],
        "ua": "'At the mouth of the river' — точка на маршруті. 'In the mouth' означало б усередині отвору.",
    },
    {
        "family": "process_diagram", "type": "paraphrase_no_distortion", "visual": "W1V-PROC-02",
        "prompt": "Original: 'The mature adult returns upstream to the river where it hatched.' Which paraphrase preserves the meaning exactly?",
        "options": [
            "Having matured at sea, the salmon swims back upstream to the same river in which it was born.",
            "The adult salmon returns to a river in order to lay its eggs.",
            "The adult salmon attempts to return to the river where it hatched.",
            "After several years, the adult salmon returns to the sea in order to spawn.",
        ],
        "answer": "Having matured at sea, the salmon swims back upstream to the same river in which it was born.",
        "distractors": {
            "The adult salmon returns to a river in order to lay its eggs.": "'A river' loses the whole point of the stage, which is that the fish returns to its own river of origin.",
            "The adult salmon attempts to return to the river where it hatched.": "'Attempts' introduces uncertainty about the outcome that the diagram does not express. The stage is shown as completed.",
            "After several years, the adult salmon returns to the sea in order to spawn.": "The direction has been reversed. Spawning happens in fresh water, upstream, not at sea.",
        },
        "explanation": "The rewrite must keep the direction of travel, the specificity of the destination and the certainty of the outcome. Losing the definite reference, as the second option does, is the subtlest of the three failures and the easiest to commit while paraphrasing at speed.",
        "errorCategory": "lexical_distortion",
        "grounding": ["stage.5", "stage.6", "output"],
        "ua": "Тут вирішальна деталь — 'та сама річка'. Заміна на 'a river' знищує зміст етапу.",
    },
    {
        "family": "process_diagram", "type": "sentence_correction", "visual": "W1V-PROC-03",
        "prompt": "This sentence contains a reporting fault: 'The water is stored in a tank so that bacteria are killed.' Which correction repairs it?",
        "options": [
            "The screened water is stored in a sealed underground tank before it is filtered.",
            "The water is stored in a tank, where bacteria are killed.",
            "The water was stored in a sealed underground tank.",
            "The water is stored in a tank so that it can be disinfected later.",
        ],
        "answer": "The screened water is stored in a sealed underground tank before it is filtered.",
        "distractors": {
            "The water is stored in a tank, where bacteria are killed.": "The purpose has merely been rephrased as a relative clause. Storage is still being credited with an effect the diagram assigns elsewhere.",
            "The water was stored in a sealed underground tank.": "The invented purpose is gone but a tense error has replaced it: an undated process takes present simple.",
            "The water is stored in a tank so that it can be disinfected later.": "Still a purpose clause, and still wrong. The diagram shows what follows storage, not what storage is for.",
        },
        "explanation": "Disinfection happens at the ultraviolet stage, not in the tank, so attaching that purpose to storage misreads the sequence as well as inventing a rationale. The repaired sentence reports the stage, its input and its position relative to the next stage, which is the full extent of what a process diagram supports.",
        "errorCategory": "unsupported_causal_claim",
        "grounding": ["stage.3", "stage.4", "stage.5", "stage.6"],
        "ua": "Схема показує порядок етапів, а не їхню мету. 'So that' майже завжди означає вигадану інформацію.",
    },
    {
        "family": "process_diagram", "type": "grammar_correction", "visual": "W1V-PROC-03",
        "prompt": "One word is missing. Type the single verb form that belongs in the gap.",
        "sentence": "The filtered water ____ exposed to ultraviolet light before it reaches the taps.",
        "answer": "is",
        "accept": ["is"],
        "explanation": "The process carries no date, so the passive has to be present simple: 'is exposed'. 'Was exposed' imports a past frame the diagram never establishes, and switching to the active 'exposes' reverses the roles so that the water acts on the light rather than the other way round.",
        "errorCategory": "tense_misuse",
        "grounding": ["stage.6", "stage.7"],
        "ua": "Пасив у теперішньому простому: 'is exposed'. Це стандартна форма для опису рукотворного процесу.",
    },
    {
        "family": "process_diagram", "type": "paragraph_ordering", "visual": "W1V-PROC-01",
        "prompt": "Arrange these four paragraphs into a correctly structured Task 1 report.",
        "items": [
            {"id": "p-body-remake", "text": "The remaining stages remanufacture the material. The cullet is melted in a furnace, the molten glass is moulded into new bottles, and these are then filled, distributed and eventually returned to the first stage."},
            {"id": "p-intro", "text": "The diagram illustrates the sequence by which used glass bottles are recycled and returned to use."},
            {"id": "p-body-prepare", "text": "In the first half of the process the material is prepared. Used bottles are collected and transported to a plant, where non-glass items are removed by hand, the glass is separated into clear, green and brown streams, and the sorted glass is crushed into cullet."},
            {"id": "p-overview", "text": "Overall, the process forms a closed loop of eight stages, starting with the collection of used bottles and finishing with new bottles that re-enter the collection system."},
        ],
        "order": ["p-intro", "p-overview", "p-body-prepare", "p-body-remake"],
        "explanation": "Introduction, overview naming the count and the cyclical shape, then the two halves of the sequence in the order they occur. A process report is one of the few Task 1 types where the body paragraphs must follow the order of the diagram rather than an order you choose, because sequence is the content.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["stage_count", "cyclical", "stage.1", "stage.5", "stage.6", "stage.8"],
        "ua": "У процесі body-абзаци йдуть у порядку етапів. Це єдина родина, де порядок задає сама схема.",
    },

    # ========================= MAPS AND PLANS =========================
    {
        "family": "map_plan", "type": "feature_selection", "visual": "W1V-MAP-01",
        "prompt": "Which detail from these maps most deserves a place in your report?",
        "options": [
            "The village changed from an agricultural settlement into a residential one, although the woodland on the northern boundary survived.",
            "The primary school is in the west of the village.",
            "A bypass road now runs along the eastern edge.",
            "The village has become a much more pleasant place to live.",
        ],
        "answer": "The village changed from an agricultural settlement into a residential one, although the woodland on the northern boundary survived.",
        "distractors": {
            "The primary school is in the west of the village.": "An unchanged feature reported on its own, with no indication that it is unchanged. Location alone is not a finding.",
            "A bypass road now runs along the eastern edge.": "A genuine change, but one of several. Reporting a single addition does not tell the reader what happened to the village.",
            "The village has become a much more pleasant place to live.": "An evaluation. Maps show what is where; they cannot show whether the result is pleasant.",
        },
        "explanation": "With maps, the reportable feature is the change in the overall character of the site, together with whatever survived it. Naming both in one sentence gives the reader the framework, and the individual additions and removals then have somewhere to sit in the body paragraphs.",
        "errorCategory": "missing_overview",
        "grounding": ["status.Farmland", "status.Housing estate", "status.Woodland", "area.Woodland"],
        "ua": "Для карти головне — як змінився характер місця в цілому і що при цьому вціліло.",
    },
    {
        "family": "map_plan", "type": "overview_selection", "visual": "W1V-MAP-01",
        "prompt": "Which sentence works best as the overview paragraph for these maps?",
        "options": [
            "Overall, Whitmore has been transformed from a farming village into a residential one, with the largest changes in the south and the centre, while the northern woodland and the school have been left as they were.",
            "The farmland was removed, a housing estate was built, the shop became a supermarket and a bypass was constructed.",
            "Whitmore has grown because of increasing demand for commuter housing.",
            "The changes to Whitmore have damaged its rural character.",
        ],
        "answer": "Overall, Whitmore has been transformed from a farming village into a residential one, with the largest changes in the south and the centre, while the northern woodland and the school have been left as they were.",
        "distractors": {
            "The farmland was removed, a housing estate was built, the shop became a supermarket and a bypass was constructed.": "Four accurate changes in a row, but a list is not an overview. Nothing here says what the village became.",
            "Whitmore has grown because of increasing demand for commuter housing.": "Demand for housing appears nowhere on either map. This supplies a cause the graphic cannot evidence.",
            "The changes to Whitmore have damaged its rural character.": "A judgement about the outcome. Task 1 reports the changes and leaves the reader to evaluate them.",
        },
        "explanation": "The overview names the transformation, locates it broadly so the reader can orient themselves, and records what was retained. Retention is the element weaker responses omit entirely, and on a map task it is often the most efficient thing to say, because it accounts for several features at once.",
        "errorCategory": "missing_overview",
        "grounding": ["count.added", "count.removed", "count.replaced", "count.unchanged", "status.Woodland", "status.Primary school"],
        "ua": "Не забувайте про те, що НЕ змінилося. Слабкі відповіді описують лише зміни.",
    },
    {
        "family": "map_plan", "type": "grouping", "visual": "W1V-MAP-01",
        "prompt": "Which plan organises the changes most effectively?",
        "options": [
            "One paragraph for the residential development in the south, and one for the changes to the village centre and its edges.",
            "One paragraph per building, in the order they appear on the map.",
            "One paragraph for 1985 and one for today, listing every feature in each.",
            "One paragraph for the features that were added and one for your assessment of the result.",
        ],
        "answer": "One paragraph for the residential development in the south, and one for the changes to the village centre and its edges.",
        "distractors": {
            "One paragraph per building, in the order they appear on the map.": "The order features appear on a map is meaningless, and one paragraph per feature produces seven paragraphs.",
            "One paragraph for 1985 and one for today, listing every feature in each.": "This makes the reader compare the two lists themselves. With paired maps, the changes are the content, so they must be stated directly.",
            "One paragraph for the features that were added and one for your assessment of the result.": "Half the changes go unreported, and the second paragraph does not belong in Task 1 at all.",
        },
        "explanation": "Grouping by area works well here because the changes cluster geographically: the south was redeveloped wholesale, while the centre was altered rather than replaced. Grouping by type of change, with additions in one paragraph and removals in another, is an equally defensible alternative; what does not work is following the map feature by feature.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["area.Farmland", "area.Housing estate", "area.Village shop", "area.Cattle market", "area.Bypass road"],
        "ua": "Групуйте або за районами, або за типом зміни (додано / прибрано). Але не за порядком на карті.",
    },
    {
        "family": "map_plan", "type": "trend_language", "visual": "W1V-MAP-01",
        "prompt": "Which sentence locates and classifies the change to the village shop most accurately?",
        "options": [
            "The village shop in the centre was converted into a supermarket occupying the same footprint.",
            "The village shop was demolished and a supermarket was built elsewhere in the village.",
            "A new supermarket was built here, replacing the old shop.",
            "The village shop will be replaced by a supermarket.",
        ],
        "answer": "The village shop in the centre was converted into a supermarket occupying the same footprint.",
        "distractors": {
            "The village shop was demolished and a supermarket was built elsewhere in the village.": "The maps show the same outline in the same place with a new label, which is conversion, not demolition and relocation.",
            "A new supermarket was built here, replacing the old shop.": "'Here' is unusable. A reader who cannot see the map has no idea where the writer is pointing.",
            "The village shop will be replaced by a supermarket.": "The future tense turns a completed change into a proposal. These are two dated maps, so the change has already happened.",
        },
        "explanation": "Three separate decisions are being tested: the classification (replacement rather than addition or removal), the location (stated in words rather than pointed at) and the tense (completed, not proposed). Map tasks fail most often on the second of these, because it feels natural to write as if the reader can see the graphic.",
        "errorCategory": "data_misreading",
        "grounding": ["status.Village shop", "area.Village shop"],
        "ua": "Читач не бачить карти. Слова 'here' і 'this area' не працюють — потрібні сторони світу та орієнтири.",
    },
    {
        "family": "map_plan", "type": "comparison_building", "visual": "W1V-MAP-02",
        "prompt": "Which comparison is fully supported by these plans?",
        "options": [
            "Both the silent reading room and the central staircase are to be retained, while the north wing is to be reconfigured completely.",
            "The library will be considerably larger after the redevelopment.",
            "The cafe is to replace the issue desk.",
            "Students clearly prefer group study pods to printed journals.",
        ],
        "answer": "Both the silent reading room and the central staircase are to be retained, while the north wing is to be reconfigured completely.",
        "distractors": {
            "The library will be considerably larger after the redevelopment.": "The outline of the building is unchanged. Rearranging the interior does not make the floor area larger, and the plans show no extension.",
            "The cafe is to replace the issue desk.": "Two separate changes have been merged. The issue desk is to become a bank of self-service kiosks, and the cafe is a new addition on the east side.",
            "Students clearly prefer group study pods to printed journals.": "A preference is not on the plan. The drawings show what is proposed, not why, and not what anyone thinks about it.",
        },
        "explanation": "The supported statement pairs two retentions against one wholesale change, which is a genuine comparison rather than a list. The second and third options show the two commonest map errors in combination: assuming that internal change implies expansion, and merging two distinct changes because they are near each other on the page.",
        "errorCategory": "data_misreading",
        "grounding": ["status.Silent reading room", "status.Main staircase", "status.Print journal stacks", "status.Group study pods", "status.Issue desk", "status.Cafe"],
        "ua": "Дві помилки, типові для карт: вважати перепланування розширенням і зливати дві різні зміни в одну.",
    },
    {
        "family": "map_plan", "type": "data_to_sentence", "visual": "W1V-MAP-02",
        "prompt": "Complete the sentence with one word so that the tense suits a proposal.",
        "sentence": "A cafe is ____ be built beside the main entrance.",
        "answer": "to",
        "accept": ["to"],
        "explanation": "A change that has not happened yet takes 'is to be built' or 'will be built'. Past simple would state that the cafe already exists, which is exactly what the proposed plan does not show. Getting the tense right on a proposal is the clearest signal that you have read which plan is which.",
        "errorCategory": "tense_misuse",
        "grounding": ["status.Cafe", "area.Cafe"],
        "ua": "Проєкт, а не факт: 'is to be built' або 'will be built'. Минулий час означав би, що кафе вже існує.",
    },
    {
        "family": "map_plan", "type": "paraphrase_no_distortion", "visual": "W1V-MAP-02",
        "prompt": "Original: 'The print journal stacks in the north wing are to be removed and replaced by group study pods.' Which paraphrase preserves the meaning exactly?",
        "options": [
            "Group study pods are to occupy the space in the north wing currently taken up by the print journal stacks.",
            "The print journal stacks are to be moved to another part of the library.",
            "Group study pods are to be added to the north wing alongside the journal stacks.",
            "The north wing is to be closed to make way for group study pods.",
        ],
        "answer": "Group study pods are to occupy the space in the north wing currently taken up by the print journal stacks.",
        "distractors": {
            "The print journal stacks are to be moved to another part of the library.": "The plan shows removal, not relocation. The stacks do not reappear anywhere on the proposed drawing.",
            "Group study pods are to be added to the north wing alongside the journal stacks.": "'Alongside' turns a replacement into an addition, which means both features would be present. Only one will be.",
            "The north wing is to be closed to make way for group study pods.": "The wing is being reconfigured, not closed, and it will be in use once the pods are installed.",
        },
        "explanation": "Replacement means one thing goes and another takes its place. A paraphrase that turns it into relocation, addition or closure changes what the plan actually proposes, and all three are easy slips because the sentences remain fluent and plausible. Classifying each change before you write it is the safeguard.",
        "errorCategory": "lexical_distortion",
        "grounding": ["status.Print journal stacks", "status.Group study pods", "area.Print journal stacks", "area.Group study pods"],
        "ua": "Класифікуйте зміну до того, як писати: додано, прибрано, замінено чи збережено. Заміна — це не переміщення.",
    },
    {
        "family": "map_plan", "type": "sentence_correction", "visual": "W1V-MAP-03",
        "prompt": "This sentence contains three faults: 'The caravan park is removed and a hotel complex is built there, which improved the resort.' Which correction repairs all three?",
        "options": [
            "The caravan park in the east was cleared and a hotel complex was built on the site.",
            "The caravan park was removed and a hotel complex was built there.",
            "The caravan park in the east is removed and a hotel complex is built on the site.",
            "The caravan park was replaced by a hotel complex, which improved the resort.",
        ],
        "answer": "The caravan park in the east was cleared and a hotel complex was built on the site.",
        "distractors": {
            "The caravan park was removed and a hotel complex was built there.": "The tense and the evaluation are fixed, but 'there' still gives the reader no location, and no compass reference has been added.",
            "The caravan park in the east is removed and a hotel complex is built on the site.": "The location is fixed but the present tense remains, which misrepresents two dated maps as a current state.",
            "The caravan park was replaced by a hotel complex, which improved the resort.": "The evaluation survives, and the location is still missing. Only one of the three faults has actually gone.",
        },
        "explanation": "Three faults have to be repaired in a single edit: two dated maps require past simple, 'there' is unusable for a reader who cannot see the graphic, and 'improved the resort' is an evaluation Task 1 never makes. Each wrong option fixes a different subset, which is what makes this worth practising under time pressure.",
        "errorCategory": "tense_misuse",
        "grounding": ["status.Caravan park", "status.Hotel complex", "area.Caravan park", "area.Hotel complex"],
        "ua": "Три помилки одночасно: час, відсутність орієнтира і оцінка. Виправляти треба всі три в одному реченні.",
    },
    {
        "family": "map_plan", "type": "grammar_correction", "visual": "W1V-MAP-03",
        "prompt": "One word is missing. Type the single word that belongs in the gap.",
        "sentence": "A golf course was laid out on the farmland ____ the north of the resort.",
        "answer": "to",
        "accept": ["to"],
        "explanation": "'To the north of' places something outside the area named, which is what 'inland to the north' requires here. 'In the north of' would put the golf course inside the resort itself. The definite article before the compass point is compulsory in both forms, and it is the part Ukrainian speakers most often drop.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["area.Golf course", "area.Farmland", "status.Golf course"],
        "ua": "'To the north of' — поза межами об'єкта; 'in the north of' — всередині нього. Артикль 'the' обов'язковий в обох.",
    },
    {
        "family": "map_plan", "type": "paragraph_ordering", "visual": "W1V-MAP-01",
        "prompt": "Arrange these four paragraphs into a correctly structured Task 1 report.",
        "items": [
            {"id": "p-body-centre", "text": "The centre has been redeveloped rather than expanded. The village shop has become a supermarket on the same footprint and the cattle market has been demolished, although the primary school in the west remains in its original position."},
            {"id": "p-overview", "text": "Overall, Whitmore has changed from a largely agricultural settlement into a residential one, with the most substantial redevelopment in the south and the centre, while the woodland along the northern boundary has been left untouched."},
            {"id": "p-intro", "text": "The two maps compare the village of Whitmore as it was in 1985 with the village as it is today."},
            {"id": "p-body-south", "text": "The greatest change has taken place in the south, where the farmland that once bordered the village has been cleared and a housing estate built in its place. A bypass road has also been constructed along the eastern edge."},
        ],
        "order": ["p-intro", "p-overview", "p-body-south", "p-body-centre"],
        "explanation": "Introduction, overview naming the change in character and what survived, then the detail grouped by area with the largest change first. Working from the most substantial change outwards helps the reader build a mental picture of the site, which is the whole difficulty of writing about a graphic they cannot see.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["status.Farmland", "status.Housing estate", "status.Bypass road", "status.Village shop", "status.Cattle market", "status.Primary school", "status.Woodland"],
        "ua": "Починайте body з найбільшої зміни — так читачеві легше побудувати образ місцевості.",
    },

    # ======================= MIXED VISUALS =======================
    {
        "family": "mixed_visual", "type": "feature_selection", "visual": "W1V-MIX-01",
        "prompt": "Which detail from these two charts most deserves a place in your report?",
        "options": [
            "Consumption stopped growing after 2019, while by 2024 renewables had become the largest single source of supply.",
            "Coal accounted for 11 per cent of supply in 2024.",
            "Consumption stood at 310 terawatt-hours in 2010.",
            "The country should invest more heavily in renewable generation.",
        ],
        "answer": "Consumption stopped growing after 2019, while by 2024 renewables had become the largest single source of supply.",
        "distractors": {
            "Coal accounted for 11 per cent of supply in 2024.": "One slice of one chart. It belongs in a body paragraph, and it says nothing about how the two graphics relate.",
            "Consumption stood at 310 terawatt-hours in 2010.": "A single starting value. Useful as detail, but it carries no pattern and touches only one of the two charts.",
            "The country should invest more heavily in renewable generation.": "A recommendation, which Task 1 never makes, and it is drawn from neither chart.",
        },
        "explanation": "With a mixed task the reportable feature is the relationship between the graphics: demand levelled off at the same time as the supply mix tipped towards renewables. A detail confined to one chart, however accurate, cannot serve that function, and this is the single most common way mixed tasks are underscored.",
        "errorCategory": "missing_overview",
        "grounding": ["c0.value.Total consumption.2019", "c0.value.Total consumption.2024", "c1.largest.2024", "c1.share.Renewables.2024"],
        "ua": "У комбінованому завданні головне — зв'язок між двома візуалами, а не найяскравіша деталь одного з них.",
    },
    {
        "family": "mixed_visual", "type": "overview_selection", "visual": "W1V-MIX-01",
        "prompt": "Which sentence works best as the overview paragraph for both charts?",
        "options": [
            "Overall, electricity consumption rose substantially before levelling off towards the end of the period, and by 2024 renewables had become the largest contributor to supply, ahead of natural gas.",
            "Consumption rose from 310 to 376 terawatt-hours. Renewables accounted for 38 per cent of supply, natural gas 27 per cent and nuclear 19 per cent.",
            "Consumption levelled off because renewable electricity had become cheaper to generate.",
            "Overall, electricity consumption rose steadily throughout the period.",
        ],
        "answer": "Overall, electricity consumption rose substantially before levelling off towards the end of the period, and by 2024 renewables had become the largest contributor to supply, ahead of natural gas.",
        "distractors": {
            "Consumption rose from 310 to 376 terawatt-hours. Renewables accounted for 38 per cent of supply, natural gas 27 per cent and nuclear 19 per cent.": "Both charts are covered, but with figures. This is the body of the report presented as its overview.",
            "Consumption levelled off because renewable electricity had become cheaper to generate.": "Neither chart shows a cost, so the causal link is invented, and it also reduces the overview to one of the two graphics.",
            "Overall, electricity consumption rose steadily throughout the period.": "Two faults: it ignores the pie chart entirely, and 'steadily throughout' misdescribes a line that flattens after 2019.",
        },
        "explanation": "A mixed task takes one overview, not two, and that overview has to reach into both graphics. Here it needs the shape of the line, the leading share in the pie, and ideally the sense that the two belong to the same story. An overview that covers only the first chart is the commonest structural failure in this family.",
        "errorCategory": "missing_overview",
        "grounding": ["c0.first.Total consumption", "c0.last.Total consumption", "c0.value.Total consumption.2019", "c1.largest.2024", "c1.share.Renewables.2024", "c1.share.Natural gas.2024"],
        "ua": "Одне overview на обидва візуали. Найчастіша структурна помилка — overview лише для першого графіка.",
    },
    {
        "family": "mixed_visual", "type": "grouping", "visual": "W1V-MIX-01",
        "prompt": "Which plan organises a report on these two charts most effectively?",
        "options": [
            "One body paragraph on the consumption trend and one on the 2024 supply mix, with a sentence in the second that links the mix back to the demand shown in the first.",
            "Two separate reports, each with its own introduction and overview.",
            "One paragraph per data point across both charts.",
            "One paragraph combining every figure from both charts in numerical order.",
        ],
        "answer": "One body paragraph on the consumption trend and one on the 2024 supply mix, with a sentence in the second that links the mix back to the demand shown in the first.",
        "distractors": {
            "Two separate reports, each with its own introduction and overview.": "This is the defining error of the mixed family. Two mini-reports double the structure, double the word count and never make the connection the task was built to test.",
            "One paragraph per data point across both charts.": "Eleven paragraphs of one figure each. There is no grouping, no comparison and no possibility of staying within the word count.",
            "One paragraph combining every figure from both charts in numerical order.": "Numerical order is not a meaningful organising principle, and mixing terawatt-hours with percentages in one sequence invites exactly the unit confusion this family punishes.",
        },
        "explanation": "Give each graphic its own body paragraph so that the units stay separate, then use one sentence to relate them. That single linking sentence is what distinguishes a mixed-task response from two short reports stapled together, and it costs almost nothing in words.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["c0.last.Total consumption", "c1.largest.2024"],
        "ua": "По абзацу на кожен візуал, плюс одне речення, що їх пов'язує. Це і є різниця між звітом і двома міні-звітами.",
    },
    {
        "family": "mixed_visual", "type": "trend_language", "visual": "W1V-MIX-01",
        "prompt": "How is total consumption between 2019 and 2024 best described?",
        "options": [
            "virtually flat, moving only between 372 and 376 terawatt-hours",
            "continuing to rise strongly",
            "beginning to decline",
            "fluctuating markedly",
        ],
        "answer": "virtually flat, moving only between 372 and 376 terawatt-hours",
        "distractors": {
            "continuing to rise strongly": "This describes the earlier part of the line. Applying it to the final years misreports the point at which the graph changes shape.",
            "beginning to decline": "The figure does not fall at any point after 2019; it edges upwards.",
            "fluctuating markedly": "'Fluctuating' requires movement up and down. The line moves in one direction, and barely.",
        },
        "explanation": "Between 2019 and 2024 the line moves from 372 to 376 terawatt-hours, which on a scale that started at 310 is close enough to no movement that 'levelled off' or 'virtually flat' is the accurate description. Identifying where a line changes character, rather than describing it with one adverb throughout, is what trend language is for.",
        "errorCategory": "imprecise_quantity",
        "grounding": ["c0.value.Total consumption.2019", "c0.value.Total consumption.2024", "c0.first.Total consumption"],
        "ua": "Одна лінія може мати дві різні характеристики. Знайдіть точку, де змінюється її поведінка.",
    },
    {
        "family": "mixed_visual", "type": "comparison_building", "visual": "W1V-MIX-02",
        "prompt": "Which comparison is fully supported by the table and the chart together?",
        "options": [
            "The two lines that gained passengers, the Coastal and Valley lines, also recorded the two highest satisfaction scores.",
            "The City Loop was the least popular line with passengers.",
            "Satisfaction on the Northern Line fell between 2018 and 2023.",
            "Passenger numbers fell on the Northern Line because passengers were dissatisfied.",
        ],
        "answer": "The two lines that gained passengers, the Coastal and Valley lines, also recorded the two highest satisfaction scores.",
        "distractors": {
            "The City Loop was the least popular line with passengers.": "The City Loop carries the most journeys of any line, and its satisfaction score of 66 per cent is above the Northern Line's 61. It is least popular on neither measure.",
            "Satisfaction on the Northern Line fell between 2018 and 2023.": "Satisfaction is given for 2023 only. With a single reading, no change over time can be claimed.",
            "Passenger numbers fell on the Northern Line because passengers were dissatisfied.": "The two graphics coincide; neither shows that one caused the other. This is the trap a mixed task is designed to set.",
        },
        "explanation": "Relating two graphics means noting that patterns coincide, not asserting that one produces the other. The Coastal and Valley lines gained journeys and score 84 and 79 per cent, the highest two figures on the chart, so the association is directly readable. Turning that association into a cause, as the last option does, is the error this family most reliably produces.",
        "errorCategory": "invalid_comparison",
        "grounding": ["c0.delta.Coastal Line.2018 (m).2023 (m)", "c0.delta.Valley Line.2018 (m).2023 (m)", "c0.delta.Northern Line.2018 (m).2023 (m)", "c1.value.Satisfied.Coastal Line", "c1.value.Satisfied.Valley Line", "c1.value.Satisfied.Northern Line", "c1.value.Satisfied.City Loop"],
        "ua": "Збіг двох закономірностей — це не причина. Пишіть 'coincided with', а не 'because'.",
    },
    {
        "family": "mixed_visual", "type": "data_to_sentence", "visual": "W1V-MIX-02",
        "prompt": "Complete the sentence with one word so that it reports the change accurately.",
        "sentence": "Journeys on the Coastal Line rose from 18.4 million in 2018 ____ 22.1 million in 2023.",
        "answer": "to",
        "accept": ["to"],
        "explanation": "'Rise from X to Y' is the fixed frame for a start and an end value. 'Until' would turn 22.1 million into a point in time, and 'by' would make it the size of the increase, when the increase was in fact 3.7 million. One word decides which quantity the reader takes away.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["c0.value.Coastal Line.2018 (m)", "c0.value.Coastal Line.2023 (m)", "c0.delta.Coastal Line.2018 (m).2023 (m)"],
        "ua": "'From ... to ...' — початок і кінець. 'By' — величина зміни, тут 3.7 мільйона.",
    },
    {
        "family": "mixed_visual", "type": "paraphrase_no_distortion", "visual": "W1V-MIX-03",
        "prompt": "Original: 'Health graduates were the most likely to be in work within six months, at 92 per cent, while humanities graduates were the least likely, at 68 per cent.' Which paraphrase preserves the meaning exactly?",
        "options": [
            "At 92 per cent, health topped the employment ranking, and humanities came bottom at 68 per cent.",
            "Health graduates found work faster than humanities graduates.",
            "Nearly all health graduates were employed within six months, unlike most humanities graduates.",
            "Health graduates earned more than humanities graduates.",
        ],
        "answer": "At 92 per cent, health topped the employment ranking, and humanities came bottom at 68 per cent.",
        "distractors": {
            "Health graduates found work faster than humanities graduates.": "The chart measures the proportion in work at a fixed point, not how quickly individuals found it. Speed and proportion are different measures.",
            "Nearly all health graduates were employed within six months, unlike most humanities graduates.": "68 per cent is itself a clear majority, so 'unlike most' inverts the humanities figure. The contrast has been overstated into an error.",
            "Health graduates earned more than humanities graduates.": "Earnings appear on neither graphic. This substitutes a different variable altogether.",
        },
        "explanation": "The rewrite has to keep the measure (proportion in work at six months), the ranking (top and bottom) and the figures. Converting a proportion into a speed, or a majority into a minority, both read fluently and both change what the chart says, which is why paraphrase is worth checking against the data rather than against the original sentence.",
        "errorCategory": "lexical_distortion",
        "grounding": ["c0.value.In work.Health", "c0.value.In work.Humanities", "c0.top.Health", "c0.bottom.Humanities"],
        "ua": "'Частка працевлаштованих' і 'швидкість пошуку роботи' — різні речі. Перефразування не повинно міняти вимір.",
    },
    {
        "family": "mixed_visual", "type": "sentence_correction", "visual": "W1V-MIX-03",
        "prompt": "This sentence contains a reporting fault: 'Humanities graduates struggle to find jobs, which suggests the subject is less useful.' Which correction repairs it?",
        "options": [
            "Humanities recorded the lowest employment rate of the five fields, at 68 per cent.",
            "Humanities graduates struggled to find jobs, at 68 per cent.",
            "Humanities recorded the lowest employment rate, which suggests the subject is less useful.",
            "Only 68 per cent of humanities graduates found work, which is disappointing.",
        ],
        "answer": "Humanities recorded the lowest employment rate of the five fields, at 68 per cent.",
        "distractors": {
            "Humanities graduates struggled to find jobs, at 68 per cent.": "The judgement in 'struggled' survives, and attaching a percentage to it produces a sentence that reads oddly as well as inaccurately.",
            "Humanities recorded the lowest employment rate, which suggests the subject is less useful.": "The rank is now stated correctly, but the evaluation of the subject remains, and the chart cannot support any claim about usefulness.",
            "Only 68 per cent of humanities graduates found work, which is disappointing.": "'Only' and 'disappointing' are both evaluative. The word 'only' is easy to overlook, but it colours the figure just as clearly as the adjective does.",
        },
        "explanation": "'Struggle' and 'less useful' are both judgements the chart cannot support, and 68 per cent is in any case a clear majority rather than evidence of difficulty. A Task 1 sentence gives the rank and the figure and stops. Notice that evaluation can hide inside a single small word such as 'only'.",
        "errorCategory": "personal_opinion",
        "grounding": ["c0.value.In work.Humanities", "c0.bottom.Humanities"],
        "allowedNumbers": [5],
        "allowedNumbersReason": "Count of fields of study shown on the chart, not a data value.",
        "ua": "Оцінка може ховатися в одному слові: 'only 68 per cent' уже несе судження.",
    },
    {
        "family": "mixed_visual", "type": "grammar_correction", "visual": "W1V-MIX-03",
        "prompt": "One word is missing. Type the single word that belongs in the gap.",
        "sentence": "Just over half of all graduates, 54 per cent, went ____ full-time employment.",
        "answer": "into",
        "accept": ["into"],
        "explanation": "'Go into employment' is the standard collocation for entering a destination category, because the pie chart measures where graduates ended up. 'Go to employment' and 'go on employment' are both non-standard, and 'go in employment' would describe a state rather than a movement.",
        "errorCategory": "article_preposition_transfer",
        "grounding": ["c1.share.Full-time employment.2024", "c1.largest.2024"],
        "ua": "'Went into employment' — рух у категорію. 'Went to' або 'in' тут не працюють.",
    },
    {
        "family": "mixed_visual", "type": "paragraph_ordering", "visual": "W1V-MIX-01",
        "prompt": "Arrange these four paragraphs into a correctly structured Task 1 report.",
        "items": [
            {"id": "p-body-mix", "text": "The 2024 mix was led by renewables at 38 per cent, ahead of natural gas at 27 per cent and nuclear at 19 per cent. Coal supplied 11 per cent and other sources the remaining 5 per cent."},
            {"id": "p-intro", "text": "The line graph shows total electricity consumption in one country between 2010 and 2024, while the pie chart breaks down the sources of that electricity in 2024."},
            {"id": "p-body-trend", "text": "Consumption climbed from 310 terawatt-hours in 2010 to 372 in 2019, an increase of around a fifth. After 2019 growth all but stopped, and the figure had reached only 376 terawatt-hours by 2024."},
            {"id": "p-overview", "text": "Overall, consumption grew considerably in the first part of the period before levelling off, and by the end renewables supplied a larger share of that electricity than any other single source."},
        ],
        "order": ["p-intro", "p-overview", "p-body-trend", "p-body-mix"],
        "explanation": "The introduction covers both graphics in one sentence, the overview reaches into both without figures, and the two body paragraphs then take one graphic each in the order the introduction announced them. The phrase 'that electricity' in the overview is what ties the pie chart to the line graph, and it is the kind of small cohesive move that turns two descriptions into one report.",
        "errorCategory": "paragraph_organisation",
        "grounding": ["c0.first.Total consumption", "c0.value.Total consumption.2019", "c0.last.Total consumption", "c1.share.Renewables.2024", "c1.share.Natural gas.2024", "c1.share.Nuclear.2024", "c1.share.Coal.2024", "c1.share.Other.2024"],
        "ua": "Порядок body-абзаців має відповідати порядку, в якому ви назвали візуали у вступі.",
    },
]

# ---------------------------------------------------------------------------
# Full timed prompts. One per visual, so 21 against a benchmark of 20, with a
# guided, an independent and a timed prompt inside every family.
#
# Each prompt carries a planning stage and a drafting stage, a self-review
# checklist, and an annotated model response. The model response is labelled
# training guidance throughout: PROJECT_CHARTER.md section 4.9 forbids
# presenting any of this as official examiner scoring.
# ---------------------------------------------------------------------------
TASK1_MINUTES = 20
TASK1_WORD_MINIMUM = 150

# The self-review criteria are genuinely the same for every Task 1 response,
# so the base list is shared and each family adds the checks its own visual
# makes possible. Criterion names describe what IELTS assesses; they are not
# a score.
BASE_CHECKLIST = [
    {"id": "chk-paraphrase", "criterion": "Task Achievement",
     "text": "Did I paraphrase the task statement rather than copying it?"},
    {"id": "chk-overview", "criterion": "Task Achievement",
     "text": "Is there a clearly separate overview stating the largest patterns?"},
    {"id": "chk-overview-nofig", "criterion": "Task Achievement",
     "text": "Is my overview free of individual figures?"},
    {"id": "chk-keyfeatures", "criterion": "Task Achievement",
     "text": "Have I selected the key features rather than describing everything?"},
    {"id": "chk-grouped", "criterion": "Coherence and Cohesion",
     "text": "Are my body paragraphs grouped by behaviour, not listed one item at a time?"},
    {"id": "chk-nocause", "criterion": "Task Achievement",
     "text": "Have I avoided explaining why anything happened?"},
    {"id": "chk-noopinion", "criterion": "Task Achievement",
     "text": "Have I avoided opinions, recommendations and evaluative words such as 'only' or 'unfortunately'?"},
    {"id": "chk-tense", "criterion": "Grammatical Range and Accuracy",
     "text": "Does my tense match the timeframe of the visual throughout?"},
    {"id": "chk-articles", "criterion": "Grammatical Range and Accuracy",
     "text": "Have I checked every superlative and every singular countable noun for its article?"},
    {"id": "chk-length", "criterion": "Task Achievement",
     "text": "Have I written at least 150 words?"},
    {"id": "chk-timing", "criterion": "Task Achievement",
     "text": "Did I finish planning, writing and checking inside 20 minutes?"},
]

FAMILY_CHECKLIST_EXTRA = {
    "line_graph": [
        {"id": "chk-line-shape", "criterion": "Task Achievement",
         "text": "Have I reported the shape events (peaks, crossovers, plateaus) and not just start and end values?"},
        {"id": "chk-line-size", "criterion": "Lexical Resource",
         "text": "Does each adverb match the size of the movement it describes?"},
    ],
    "bar_chart": [
        {"id": "chk-bar-rank", "criterion": "Task Achievement",
         "text": "Have I stated the ranking, and said whether it holds across every group?"},
        {"id": "chk-bar-like", "criterion": "Task Achievement",
         "text": "Is every comparison between figures measured on the same variable?"},
    ],
    "pie_chart": [
        {"id": "chk-pie-share", "criterion": "Task Achievement",
         "text": "Have I written about shares rather than quantities, given that no total is shown?"},
        {"id": "chk-pie-points", "criterion": "Lexical Resource",
         "text": "Have I used 'percentage points' for differences between percentages?"},
    ],
    "table": [
        {"id": "chk-table-select", "criterion": "Task Achievement",
         "text": "Have I deliberately left most cells out and reported the extremes and exceptions?"},
        {"id": "chk-table-units", "criterion": "Task Achievement",
         "text": "Have I checked the column unit before every comparison?"},
    ],
    "process_diagram": [
        {"id": "chk-proc-count", "criterion": "Task Achievement",
         "text": "Does my overview give the number of stages, the input, the output and whether the process is cyclical?"},
        {"id": "chk-proc-voice", "criterion": "Grammatical Range and Accuracy",
         "text": "Is the voice consistent, and have I avoided starting consecutive sentences with 'Then'?"},
        {"id": "chk-proc-invent", "criterion": "Task Achievement",
         "text": "Have I avoided adding temperatures, durations or purposes the diagram does not label?"},
    ],
    "map_plan": [
        {"id": "chk-map-orient", "criterion": "Coherence and Cohesion",
         "text": "Have I located every change with compass or relative position language rather than 'here'?"},
        {"id": "chk-map-classify", "criterion": "Task Achievement",
         "text": "Have I classified each feature as added, removed, replaced or unchanged?"},
        {"id": "chk-map-retained", "criterion": "Task Achievement",
         "text": "Have I reported what stayed the same, not only what changed?"},
    ],
    "mixed_visual": [
        {"id": "chk-mix-oneover", "criterion": "Task Achievement",
         "text": "Is there one overview covering both visuals, rather than one for each?"},
        {"id": "chk-mix-link", "criterion": "Coherence and Cohesion",
         "text": "Is there at least one sentence that uses both visuals in the same claim?"},
        {"id": "chk-mix-units", "criterion": "Task Achievement",
         "text": "Have I kept the two units distinct instead of equating a share with an amount?"},
    ],
}

PLANNING_STEPS = {
    "line_graph": [
        "Read the title, the axis labels and the unit, and write the timeframe at the top of your plan.",
        "For each line, note only three things: start value, end value, and its most extreme point.",
        "Mark any shape event: a crossover, a peak, a trough, a plateau or a reversal.",
        "Group the lines that behave alike; the odd one out becomes your second body paragraph.",
        "Draft the overview from the grouping alone, with no figures in it.",
    ],
    "bar_chart": [
        "Identify the two variables: what the bars measure, and what splits them into groups.",
        "Rank the categories at the top level and note anything close enough to be a tie.",
        "Check whether that ranking holds inside every group, or whether it flips.",
        "Note the widest and the narrowest gap.",
        "Draft the overview from the ranking plus the exception to it.",
    ],
    "pie_chart": [
        "Confirm what the whole represents, and check whether any total quantity is given.",
        "Note the largest and smallest slice in each chart before anything else.",
        "For each category, note the direction and size of the change in share.",
        "Separate the categories that moved sharply from those that were stable.",
        "Draft the overview from the biggest reordering of shares, in proportion language only.",
    ],
    "table": [
        "Read the row and column headings, and note the unit of each column.",
        "Decide whether the story runs across the columns or down the rows.",
        "Find the largest figure, the smallest, and the biggest change.",
        "Decide which cells you will deliberately leave out.",
        "Draft the overview from the extremes and the exceptions only.",
    ],
    "process_diagram": [
        "Count the stages and decide whether the process is linear or cyclical.",
        "Name the input at the start and the output at the end.",
        "Choose the voice: passive for a man-made process, active for a natural cycle.",
        "Find a natural boundary in the sequence to split your two body paragraphs.",
        "Draft the overview as count plus input plus output plus shape.",
    ],
    "map_plan": [
        "Orient yourself: find the compass, the main road, the water or whatever anchors the site.",
        "Classify every feature as added, removed, replaced or unchanged.",
        "Note what the site was used for overall, and what it is used for now.",
        "Group the changes by area or by type, not by the order your eye found them.",
        "Draft the overview as the change in overall character plus what survived.",
    ],
    "mixed_visual": [
        "Identify what each visual measures and what the two have in common.",
        "Decide which visual carries the main story and which supports it.",
        "Find the link: do the two patterns coincide, or pull against each other?",
        "Plan four paragraphs, not eight. The word count does not double.",
        "Draft one overview that reaches into both visuals.",
    ],
}

# Model responses. Every figure in every model response is checked against the
# item's own visual by tests/g4_writing1_validation.py.
PROMPTS = [
    {
        "visual": "W1V-LINE-01", "mode": "guided",
        "targetFeatures": [
            "All three cities improved across the period.",
            "Tromso rose far more steeply than the other two.",
            "Tromso overtook both other cities between 2010 and 2015.",
            "Oslo and Bergen followed closely comparable paths and their order reversed.",
        ],
        "modelResponse": [
            "The line graph compares the proportion of household waste recycled in three cities at regular intervals between 2005 and 2025.",
            "Overall, recycling rates improved in all three cities across the period, but the increase in Tromso was far steeper than elsewhere, and the city moved from last place to first.",
            "Oslo and Bergen followed closely comparable paths. Bergen began slightly ahead, at 31 per cent against Oslo's 28 per cent, and both climbed gradually throughout. By 2025, however, the order had reversed, with Oslo reaching 46 per cent and Bergen 44 per cent, so the small gap between them had swapped direction rather than widened.",
            "Tromso behaved quite differently. Starting from the lowest figure of 18 per cent, it rose without interruption and had already overtaken both other cities by 2015, when it stood at 41 per cent. It continued to climb thereafter, reaching 61 per cent in 2025, more than three times its opening figure and well clear of the other two.",
        ],
        "modelNotes": [
            "The overview carries the shared pattern, the contrast and the change of rank, and contains no figures at all.",
            "The two similar cities share a paragraph, so the report compares rather than lists.",
            "'More than three times' expresses scale without inventing a percentage the graph does not state.",
        ],
        "errorCategoriesWatched": ["missing_overview", "list_like_description", "imprecise_quantity", "unsupported_causal_claim"],
        "ua": "Зверніть увагу: overview не містить жодної цифри, а два схожі міста описані в одному абзаці.",
    },
    {
        "visual": "W1V-LINE-02", "mode": "independent",
        "targetFeatures": [
            "Eastfield declined continuously while Riverside rose continuously.",
            "Riverside overtook Eastfield between 2018 and 2022.",
            "Northgate peaked in 2018, dipped, then partially recovered.",
            "The final ranking differs from the opening ranking.",
        ],
        "modelResponse": [
            "The line graph shows how many international students were enrolled at three universities between 2010 and 2024, measured in thousands.",
            "Overall, the ranking of the three institutions at the end of the period bore little resemblance to the ranking at the start, as the largest university in 2010 finished smallest and the smallest finished in the middle.",
            "Eastfield began as the largest of the three, with 20 thousand international students in 2010, but its enrolment fell at every reading, reaching 9.5 thousand by 2024. Riverside followed the opposite path, rising steadily from 8 thousand to 14 thousand, and it overtook Eastfield at some point between 2018 and 2022.",
            "Northgate was the least consistent of the three. Its enrolment climbed from 12 thousand in 2010 to a peak of 19 thousand in 2018, then fell back to 16.5 thousand in 2022 before recovering to 18 thousand at the end of the period. Despite that dip, Northgate finished as the largest of the three institutions.",
        ],
        "modelNotes": [
            "The overview describes the reordering without naming a single figure.",
            "'At some point between 2018 and 2022' is the honest way to place a crossover between two plotted readings.",
            "The fluctuating line is given its own paragraph because it does not share a pattern with either of the others.",
        ],
        "errorCategoriesWatched": ["missing_overview", "invalid_comparison", "lexical_distortion", "data_misreading"],
        "ua": "Перетин між двома позначками описується як 'between 2018 and 2022', а не конкретним роком.",
    },
    {
        "visual": "W1V-LINE-03", "mode": "timed",
        "targetFeatures": [
            "Hydroelectric generation stayed almost flat.",
            "Wind grew fastest and finished largest.",
            "Both wind and solar overtook hydroelectricity.",
            "Solar remained marginal until around 2010 before accelerating.",
        ],
        "modelResponse": [
            "The line graph shows electricity generated from wind, solar and hydroelectric sources in one country over a twenty-year period.",
            "Overall, hydroelectric generation remained essentially unchanged while both wind and solar grew from negligible levels, and by the end of the period each of them had overtaken hydroelectricity.",
            "Hydroelectric power was the dominant source at the start, at 34 terawatt-hours in 2000, and it stayed within a narrow band for the whole period, finishing at 37 terawatt-hours in 2020. Its output therefore barely moved across two decades.",
            "Wind and solar behaved very differently. Wind generation rose from 2 terawatt-hours in 2000 to 21 by 2010, overtook hydroelectricity between 2010 and 2015, and reached 68 terawatt-hours by 2020, making it comfortably the largest of the three. Solar started from just 1 terawatt-hour and remained marginal until 2010, but it then accelerated, climbing to 18 terawatt-hours in 2015 and 41 by 2020, passing hydroelectricity in the final years of the period.",
        ],
        "modelNotes": [
            "A flat line still needs reporting; 'barely moved' is a finding, not an absence of one.",
            "The two growing sources share a paragraph because they share a pattern, even though their scales differ.",
            "No reason is offered for any of the movements, because the graph shows none.",
        ],
        "errorCategoriesWatched": ["unsupported_causal_claim", "imprecise_quantity", "tense_misuse", "list_like_description"],
        "ua": "Пласка лінія — це теж результат. 'Barely moved' описує її точно, а не оминає.",
    },
    {
        "visual": "W1V-BAR-01", "mode": "guided",
        "targetFeatures": [
            "Eating out leads in every age group.",
            "Three categories fall with age and one rises.",
            "Cultural visits overtakes live events in the oldest group.",
        ],
        "modelResponse": [
            "The bar chart compares average weekly spending on four leisure activities across three age groups.",
            "Overall, eating out attracted the highest expenditure in every age group, but the relative position of the other three activities changed considerably with age, as most fell while one rose.",
            "Three categories declined as respondents got older. Eating out fell from 42 pounds a week among those aged 18 to 29 to 31 pounds among those aged 50 and over, while live events dropped far more steeply, from 27 pounds to 8 pounds. Spending on streaming services followed the same downward direction, falling from 15 pounds to 6 pounds.",
            "Cultural visits moved the other way. This was the smallest category among the youngest respondents, at 9 pounds a week, but it rose consistently with age to reach 22 pounds in the oldest group. As a result it overtook both live events and streaming services, ending as the second largest category for those aged 50 and over.",
        ],
        "modelNotes": [
            "The overview states the constant and the variation together, which is what a grouped bar chart is built to test.",
            "The three declining categories share one paragraph, so the report compares instead of listing four times.",
            "The final sentence reports a change of rank, which is the feature the chart was constructed around.",
        ],
        "errorCategoriesWatched": ["missing_overview", "list_like_description", "invalid_comparison"],
        "ua": "Три категорії, що падають, — в одному абзаці. Виняток — окремо і в кінці.",
    },
    {
        "visual": "W1V-BAR-02", "mode": "independent",
        "targetFeatures": [
            "Amsterdam and Copenhagen are far ahead of the rest.",
            "The largest step in the ranking is between Copenhagen and Munich.",
            "Rates decline steeply across the remaining cities.",
        ],
        "modelResponse": [
            "The bar chart shows the percentage of working adults who commuted by bicycle in six European cities in 2024.",
            "Overall, cycling was far more common in the two leading cities than anywhere else, and the rate then declined steeply across the remaining four, leaving a very wide gap between the top and the bottom of the ranking.",
            "Amsterdam recorded the highest figure, at 48 per cent, with Copenhagen close behind at 44 per cent. These were the only two cities in which cycling accounted for anything approaching half of commuting journeys, and the difference between them was small.",
            "The picture changed sharply below them. Munich, in third place, reached only 21 per cent, less than half the Amsterdam figure, and this drop was the largest single step anywhere in the ranking. Lyon followed at 14 per cent and Dublin at 9 per cent, while Naples recorded the lowest rate of all at 4 per cent, roughly a twelfth of the Amsterdam figure.",
        ],
        "modelNotes": [
            "Reporting where the ranking breaks is more valuable than reciting the order of six bars.",
            "'Roughly a twelfth' is checked arithmetic, not an impression: 4 is one twelfth of 48.",
            "No claim is made about change over time, because the chart shows a single year.",
        ],
        "errorCategoriesWatched": ["list_like_description", "invalid_comparison", "imprecise_quantity"],
        "ua": "Одна діаграма за один рік не дає підстав говорити про зміни в часі.",
    },
    {
        "visual": "W1V-BAR-03", "mode": "timed",
        "targetFeatures": [
            "Road dominates in both years and accounts for most of the growth.",
            "Rail is the only mode to decline.",
            "Rail loses second place to water.",
        ],
        "modelResponse": [
            "The bar chart compares the volume of freight carried by four transport modes in 1990 and 2020.",
            "Overall, freight movement grew substantially over the three decades, with road transport both dominating throughout and accounting for most of that growth, while rail was the only mode to carry less at the end than at the start.",
            "Road was already the leading mode in 1990, carrying 620 million tonnes, and it strengthened its position by 2020, when the figure reached 980 million tonnes. This increase of 360 million tonnes was larger than the total volume carried by any other mode in either year.",
            "The remaining modes were much smaller. Water freight rose from 180 to 265 million tonnes, and air freight, although still the smallest category by a wide margin, quadrupled from 12 to 48 million tonnes. Rail moved in the opposite direction, falling from 310 million tonnes in 1990 to 240 million tonnes in 2020, and as a result it lost its position as the second largest mode to water transport.",
        ],
        "modelNotes": [
            "The comparison in the third paragraph puts a single change in context by measuring it against the other modes.",
            "'Quadrupled' is exact here, which is why it is safe to use.",
            "The change of rank between rail and water is reported explicitly rather than left for the reader to infer.",
        ],
        "errorCategoriesWatched": ["unsupported_causal_claim", "lexical_distortion", "list_like_description"],
        "ua": "Множники ('quadrupled', 'twice') можна писати лише після перевірки обчисленням.",
    },
    {
        "visual": "W1V-PIE-01", "mode": "guided",
        "targetFeatures": [
            "Bathing and toilet flushing together dominate consumption.",
            "The remaining uses are comparatively minor.",
            "The report uses share language throughout.",
        ],
        "modelResponse": [
            "The pie chart shows how household water was used in one coastal city in 2024.",
            "Overall, personal washing and sanitation together dominated household consumption, accounting for well over half of the total, while outdoor and miscellaneous uses were comparatively minor.",
            "Bathing and showering was the single largest use, at 34 per cent of the total. Toilet flushing followed at 26 per cent, so these two bathroom uses combined took up three fifths of all household water. Laundry, in third place, accounted for a further 16 per cent, meaning that washing of one kind or another was responsible for the great majority of consumption.",
            "The remaining uses were considerably smaller. Kitchen and drinking water made up 12 per cent, less than half the share taken by toilet flushing, while garden watering accounted for 8 per cent. Other uses formed the smallest category, at just 4 per cent, or roughly an eighth of the largest.",
        ],
        "modelNotes": [
            "Aggregating slices ('these two bathroom uses combined') is what turns six readings into a pattern.",
            "Every verb keeps the claim inside shares: 'accounted for', 'made up', 'took up'.",
            "Fractions are used to give the reader a sense of scale that bare percentages do not.",
        ],
        "errorCategoriesWatched": ["list_like_description", "lexical_distortion", "imprecise_quantity"],
        "ua": "Об'єднання секторів — головний прийом для кругової діаграми.",
    },
    {
        "visual": "W1V-PIE-02", "mode": "independent",
        "targetFeatures": [
            "The composition became more evenly spread.",
            "Organic stayed largest but lost share; plastics became second largest.",
            "Glass, metal and other changed only slightly.",
            "No claim is made about total quantity.",
        ],
        "modelResponse": [
            "The two pie charts compare the composition of municipal waste in one city in 2000 and in 2020.",
            "Overall, the mixture became noticeably more evenly distributed over the twenty years. Organic material remained the largest component in both years but lost a substantial part of its share, while plastics grew rapidly to become the second largest category.",
            "The three categories that changed most were organic waste, paper and plastics. Organic material fell from 42 per cent of the total in 2000 to 31 per cent in 2020, and paper declined even more steeply in proportional terms, from 24 per cent to 15 per cent. Plastics moved in the opposite direction, more than doubling its share from 12 per cent to 26 per cent and displacing paper from second place.",
            "The remaining categories were far more stable. Glass edged up from 9 to 10 per cent and metal from 7 to 8 per cent, while other waste rose from 6 to 10 per cent. None of these three shifted by more than four percentage points.",
        ],
        "modelNotes": [
            "Nothing in the response claims the city produced more or less waste, because the totals are not shown.",
            "'Percentage points' is used for the differences, and 'per cent' for the shares themselves.",
            "The stable categories are covered in a single sentence rather than one each.",
        ],
        "errorCategoriesWatched": ["lexical_distortion", "missing_overview", "list_like_description"],
        "ua": "Жодного твердження про загальний обсяг: діаграми показують лише частки.",
    },
    {
        "visual": "W1V-PIE-03", "mode": "timed",
        "targetFeatures": [
            "Career advancement leads by a wide margin.",
            "The two leading reasons together cover well over half of responses.",
            "The three smallest reasons are grouped together.",
        ],
        "modelResponse": [
            "The pie chart shows the main reasons students gave for choosing a postgraduate course in 2024.",
            "Overall, professional motivations were far more common than personal or external ones, with career advancement cited more often than any other reason by a wide margin.",
            "Career advancement was the single most frequently given reason, accounting for 38 per cent of responses. Interest in the subject came second at 24 per cent, meaning that these two reasons together were given by well over half of those surveyed. The gap between first and second place was substantial, at 14 percentage points.",
            "The remaining reasons were considerably less common. Employer sponsorship accounted for 14 per cent and the reputation of the institution for 12 per cent, so these two were close to each other in size. Family expectation was cited by just 7 per cent and other reasons by 5 per cent, making them the two smallest categories on the chart, and together they accounted for only around an eighth of all responses.",
        ],
        "modelNotes": [
            "The overview groups the categories conceptually before any figure is given.",
            "The gap between the top two is quantified in percentage points, which is the correct unit.",
            "'Around an eighth' is checked: the two smallest categories total twelve per cent.",
        ],
        "errorCategoriesWatched": ["missing_overview", "invalid_comparison", "imprecise_quantity"],
        "ua": "Перевіряйте частки арифметикою перед тим, як писати 'an eighth' чи 'a fifth'.",
    },
    {
        "visual": "W1V-TAB-01", "mode": "guided",
        "targetFeatures": [
            "Arrivals rose in four of five destinations.",
            "Average stay shortened in four of five destinations.",
            "Riverford is the arrivals exception; Highland Park the stay exception.",
        ],
        "modelResponse": [
            "The table compares tourist arrivals and the average length of stay in five destinations in 2019 and 2023.",
            "Overall, most destinations received more visitors in 2023 than in 2019, but those visitors tended to stay for shorter periods, so the two measures generally moved in opposite directions. Each measure had a single exception.",
            "Arrivals increased in all but one destination. Old Harbour remained the busiest, rising from 6.5 to 7.2 million, while Coastal Bay grew from 4.2 to 5.1 million and Lakeside from 2.7 to 3.4 million. Highland Park, the smallest destination throughout, also grew, from 1.8 to 2.3 million. Riverford was the only destination to lose visitors, falling from 3.9 to 3.1 million.",
            "Length of stay moved the other way almost everywhere. Coastal Bay recorded the largest reduction, from 6.8 to 5.9 nights, and Lakeside, Old Harbour and Riverford all shortened as well. Highland Park was the exception, edging up from 7.4 to 7.6 nights and retaining the longest average stay of any destination.",
        ],
        "modelNotes": [
            "The two measures become the two body paragraphs, which covers all twenty cells without listing them.",
            "The exception is named in each paragraph, which is what a table rewards.",
            "Three destinations are handled in one clause where they share a direction.",
        ],
        "errorCategoriesWatched": ["list_like_description", "missing_overview", "invalid_comparison"],
        "ua": "У таблиці з двома вимірами саме виміри стають абзацами, а винятки — головним змістом.",
    },
    {
        "visual": "W1V-TAB-02", "mode": "independent",
        "targetFeatures": [
            "Cities differ most on housing and transport.",
            "Northvale is below the average on all four components.",
            "Metroport and Southcliff are each extreme on one component only.",
        ],
        "modelResponse": [
            "The table compares four components of a cost of living index in four cities, where 100 represents the national average.",
            "Overall, the four cities differed far more in housing and transport than in food, and only one city fell below the national average on every component measured.",
            "Metroport was the most expensive city for housing by a considerable margin, with an index of 142, and it was also slightly above average for food at 106. It was below the national figure for both transport, at 88, and utilities, at 97, so its high cost was concentrated in a single component. Rivergate showed a milder version of the same pattern, with housing at 118 and utilities the highest of the four cities at 112.",
            "Southcliff was distinctive for transport, where its index of 120 was the highest recorded, although its other three components were all within a few points of the national average or below it. Northvale, by contrast, was under 100 on all four measures, and its transport index of 71 was the lowest figure anywhere in the table.",
        ],
        "modelNotes": [
            "The index base of 100 gives every comparison a fixed reference point, so the report uses it rather than comparing cities to each other at random.",
            "No overall ranking is attempted, because the table provides no combined figure.",
            "Nothing is described as rising or falling, because the table covers a single year.",
        ],
        "errorCategoriesWatched": ["invalid_comparison", "tense_misuse", "list_like_description"],
        "ua": "Без підсумкового стовпця не можна писати 'the most expensive city overall'.",
    },
    {
        "visual": "W1V-TAB-03", "mode": "timed",
        "targetFeatures": [
            "Services grows continuously and leads throughout.",
            "Agriculture and manufacturing both contract.",
            "Agriculture ends smallest, having begun ahead of public administration.",
        ],
        "modelResponse": [
            "The table shows the percentage of the regional workforce employed in four sectors at ten-year intervals between 1995 and 2025.",
            "Overall, the region shifted decisively towards services over the three decades, while both agriculture and manufacturing contracted continuously. Services was the largest employer at every point measured, and its lead widened steadily.",
            "Services accounted for 44 per cent of the workforce in 1995 and grew at every reading, reaching 68 per cent by 2025. Public administration was the only other sector to expand, although its growth was far more modest, from 7 to 12 per cent across the same period.",
            "The two contracting sectors declined in parallel. Manufacturing was the second largest employer in 1995, at 31 per cent, but it lost roughly half its share by 2025, when it stood at 14 per cent. Agriculture fell even further in proportional terms, from 18 per cent to just 6 per cent, which left it as the smallest of the four sectors by the end of the period, having begun ahead of public administration.",
        ],
        "modelNotes": [
            "Grouping by direction gives two body paragraphs with real topic sentences.",
            "'In proportional terms' is what makes the comparison between the two falls valid, since one starts much lower than the other.",
            "The change of rank between agriculture and public administration is stated, not left implicit.",
        ],
        "errorCategoriesWatched": ["tense_misuse", "list_like_description", "lexical_distortion"],
        "ua": "Порівнюючи два падіння з різних стартових рівнів, уточнюйте: 'in proportional terms'.",
    },
    {
        "visual": "W1V-PROC-01", "mode": "guided",
        "targetFeatures": [
            "Eight stages, closed loop.",
            "Input is used bottles; output is new bottles.",
            "The sequence splits into preparation and remanufacturing.",
        ],
        "modelResponse": [
            "The diagram illustrates the process by which used glass bottles are recycled and returned to use.",
            "Overall, the process consists of eight stages and forms a closed loop, beginning with the collection of used bottles and ending with new bottles that re-enter the same collection system. It can be divided into a preparation phase and a remanufacturing phase.",
            "In the first phase, the material is made ready. Used bottles are collected from household and public bins and transported by lorry to a processing plant. There, non-glass items are removed by hand, after which the glass is separated into clear, green and brown streams. The sorted glass is then crushed into small fragments known as cullet.",
            "The second phase creates the new product. The cullet is melted in a furnace until it becomes molten glass, which is moulded into the shape of new bottles. Once these bottles have been filled and distributed, they are eventually returned to the collection stage, at which point the cycle begins again.",
        ],
        "modelNotes": [
            "Present simple passive throughout, because the process carries no dates and the agent is unimportant.",
            "The sequence linkers vary: 'after which', 'then', 'once', 'at which point'. None of the sentences begins with 'Then'.",
            "No temperature, duration or purpose is supplied, because the diagram labels none.",
        ],
        "errorCategoriesWatched": ["tense_misuse", "unsupported_causal_claim", "paragraph_organisation"],
        "ua": "Жодних температур і тривалостей: якщо схема цього не підписує, це вигадка.",
    },
    {
        "visual": "W1V-PROC-02", "mode": "independent",
        "targetFeatures": [
            "Six stages, cyclical.",
            "The cycle moves between fresh water and salt water.",
            "The adult returns to its river of origin.",
        ],
        "modelResponse": [
            "The diagram illustrates the life cycle of the Atlantic salmon.",
            "Overall, the cycle comprises six stages and moves the fish between fresh water and salt water before returning it to its point of origin. The first half takes place in the river where the salmon hatches, while the second half occurs at sea.",
            "The cycle begins when eggs are laid among gravel in the shallow upper reaches of a river. From each egg an alevin hatches, and at this stage the young fish feeds on the yolk sac still attached to its body rather than seeking food. Once the yolk sac has been absorbed, the fish emerges from the gravel as a fry and begins to feed in the shallows.",
            "The remaining stages take the salmon away from the river and back again. As a smolt, it migrates downstream and enters salt water at the mouth of the river, and it then matures in the open ocean over several years. Finally, the mature adult returns upstream to the river in which it hatched, where the cycle begins once more.",
        ],
        "modelNotes": [
            "A natural cycle takes the active voice, unlike the passive used for man-made processes.",
            "The two body paragraphs split at the freshwater and saltwater boundary, which is a real feature of the diagram.",
            "'Returns to the river in which it hatched' keeps the specificity the diagram shows; 'a river' would lose it.",
        ],
        "errorCategoriesWatched": ["tense_misuse", "lexical_distortion", "invalid_comparison"],
        "ua": "Природний цикл — активний стан, а не пасив. Це відрізняє його від виробничого процесу.",
    },
    {
        "visual": "W1V-PROC-03", "mode": "timed",
        "targetFeatures": [
            "Seven stages, linear rather than cyclical.",
            "Input is rainwater on a roof; output is drinking water at taps.",
            "The early stages remove physical material; the later ones treat what remains.",
        ],
        "modelResponse": [
            "The diagram shows how rainwater is captured from a roof and treated to make it safe to drink.",
            "Overall, the process is a linear sequence of seven stages, beginning with rain falling on a catchment surface and ending with treated water reaching household taps. The earlier stages remove physical material, while the later ones treat what remains.",
            "Water is first collected on a sloping roof and channelled into gutters. The initial volume, which carries most of the accumulated debris, is then diverted away rather than kept, and the remaining water passes through a mesh screen that removes leaves and grit. Once screened, it is held in a sealed underground tank.",
            "The final stages treat the stored water. It is drawn from the tank and passed through a fine sediment filter, after which it is exposed to ultraviolet light in a treatment unit. The treated water is then pumped to taps inside the house, at which point it is ready for use. Unlike the recycling of glass, this sequence does not return to its starting point.",
        ],
        "modelNotes": [
            "Saying explicitly that the process is not cyclical is worth doing, because most process diagrams in this bank are.",
            "The first-flush stage is reported as a diversion, which is what the diagram labels, with no explanation of why it is done.",
            "Each paragraph has a stated function, so the split is not arbitrary.",
        ],
        "errorCategoriesWatched": ["unsupported_causal_claim", "tense_misuse", "paragraph_organisation"],
        "ua": "Якщо процес лінійний, скажіть про це прямо — це частина overview.",
    },
    {
        "visual": "W1V-MAP-01", "mode": "guided",
        "targetFeatures": [
            "Agricultural village becomes residential.",
            "Largest changes in the south and the centre.",
            "Woodland and school retained.",
        ],
        "modelResponse": [
            "The two maps compare the village of Whitmore as it appeared in 1985 with the village as it is today.",
            "Overall, Whitmore has changed from a largely agricultural settlement into a residential one. The most substantial redevelopment has taken place in the south and in the centre, while the woodland along the northern boundary and the school in the west have been left as they were.",
            "The greatest change is in the south. The farmland that once bordered the village on that side has been cleared entirely and a housing estate now occupies the site. A bypass road has also been constructed along the eastern edge of the village.",
            "The centre has been redeveloped rather than expanded. The village shop has been converted into a supermarket occupying the same footprint, and the cattle market that stood nearby has been demolished and replaced by a car park. In the north and west, by contrast, nothing has altered: the woodland remains intact and the primary school stands in its original position.",
        ],
        "modelNotes": [
            "Present perfect is used throughout because one map is dated and the other is the present day.",
            "Every change is located with a compass direction or a named neighbour, never with 'here'.",
            "The retained features close the report, which accounts for the whole site rather than only the parts that changed.",
        ],
        "errorCategoriesWatched": ["tense_misuse", "paragraph_organisation", "missing_overview"],
        "ua": "Датована карта проти 'сьогодні' — present perfect. Дві датовані карти — past simple.",
    },
    {
        "visual": "W1V-MAP-02", "mode": "independent",
        "targetFeatures": [
            "A collection-centred space becomes a study-centred one.",
            "North wing and entrance change most.",
            "Southern part of the floor is retained.",
        ],
        "modelResponse": [
            "The two plans compare the ground floor of a university library as it is now with the layout proposed after redevelopment.",
            "Overall, the proposal converts the library from a collection-centred space into a study-centred one, with the north wing and the entrance area changing most, while the southern part of the floor is to be left as it is.",
            "The north wing is to be reconfigured completely. The print journal stacks that currently occupy it are to be removed and group study pods installed in the space they leave. On the west side, the microfilm room is to be closed and absorbed into the surrounding reading area, which removes a second collection-based facility from the floor.",
            "The entrance area is also to change, although less radically. The issue desk is to be replaced by a bank of self-service kiosks in the same position, and a cafe is to be built on the east side beside the main entrance. The southern part of the floor is unaffected: the silent reading room is to be retained in its present form, as is the staircase at the centre of the building.",
        ],
        "modelNotes": [
            "'Is to be' is used throughout because this is a proposal, not a completed change.",
            "The overview characterises the purpose of the redevelopment from the pattern of changes, which is an inference the plans support.",
            "Replacement is distinguished from addition: the kiosks replace the desk, but the cafe is new.",
        ],
        "errorCategoriesWatched": ["tense_misuse", "data_misreading", "lexical_distortion"],
        "ua": "Проєкт — це 'is to be' або 'will be'. Минулий час означав би, що зміни вже сталися.",
    },
    {
        "visual": "W1V-MAP-03", "mode": "timed",
        "targetFeatures": [
            "The resort shifts from working and low-cost use towards leisure.",
            "Eastern side and inland change most.",
            "Harbour and footpath are retained.",
        ],
        "modelResponse": [
            "The two maps compare a coastal resort as it was in 1990 with the same resort in 2020.",
            "Overall, the resort shifted from a working and low-cost holiday destination towards leisure and tourism, with the most significant changes on the eastern side and inland. The shoreline itself and the fishing harbour were retained throughout.",
            "The eastern side changed most. The caravan park that occupied it in 1990 was cleared, and a hotel complex was built on the same site, replacing low-cost accommodation with something considerably larger. Inland to the north, the farmland was similarly given over to leisure use, with a golf course laid out across it.",
            "The western side changed less but not entirely. The fishing harbour remained in place and in use, although the boatyard beside it was converted into a marina for leisure craft, which follows the same shift from working to recreational use seen elsewhere on the map. Along the shoreline, the coastal footpath was retained over its full length.",
        ],
        "modelNotes": [
            "Two dated maps take past simple, unlike the Whitmore task where the second map is the present day.",
            "The report groups by area, and each area paragraph contains both a change and a retention.",
            "'Follows the same shift' relates two changes to each other, which is description, not causal explanation.",
        ],
        "errorCategoriesWatched": ["tense_misuse", "unsupported_causal_claim", "paragraph_organisation"],
        "ua": "Дві датовані карти — past simple. Порівняйте з завданням про Whitmore, де потрібен present perfect.",
    },
    {
        "visual": "W1V-MIX-01", "mode": "guided",
        "targetFeatures": [
            "Consumption grows then levels off after 2019.",
            "Renewables are the largest single source in 2024.",
            "One overview covers both visuals.",
        ],
        "modelResponse": [
            "The line graph shows total electricity consumption in one country between 2010 and 2024, while the pie chart breaks down the sources of that electricity in 2024.",
            "Overall, consumption grew considerably during the first part of the period before levelling off, and by the end renewables supplied a larger share of that electricity than any other single source.",
            "Consumption climbed steadily in the earlier years, rising from 310 terawatt-hours in 2010 to 335 in 2013 and 356 in 2016, before reaching 372 terawatt-hours in 2019. After that point growth almost stopped: the figure stood at 374 in 2022 and only 376 in 2024, so the final years of the period added very little.",
            "The pie chart shows how that demand was met at the end of the period. Renewables were the largest single source, at 38 per cent of supply, ahead of natural gas at 27 per cent and nuclear at 19 per cent. Coal, at 11 per cent, had become a minor contributor, and other sources supplied the remaining 5 per cent.",
        ],
        "modelNotes": [
            "There is one overview, and it reaches into both graphics.",
            "'That electricity' and 'that demand' are the cohesive links that tie the pie chart back to the line graph.",
            "Terawatt-hours and percentages are never mixed in the same comparison.",
        ],
        "errorCategoriesWatched": ["missing_overview", "invalid_comparison", "paragraph_organisation"],
        "ua": "Слова 'that electricity' і 'that demand' — це і є зв'язок між двома візуалами.",
    },
    {
        "visual": "W1V-MIX-02", "mode": "independent",
        "targetFeatures": [
            "The two busiest lines lost passengers; the two smaller lines grew.",
            "The growing lines also scored highest on satisfaction.",
            "The association is reported without claiming causation.",
        ],
        "modelResponse": [
            "The table shows passenger journeys on four rail lines in 2018 and 2023, while the bar chart shows how satisfied passengers were with each line in 2023.",
            "Overall, the two busiest lines both lost passengers over the period while the two smaller lines grew, and the lines that gained passengers were also the lines whose passengers reported the highest satisfaction.",
            "The City Loop carried by far the most journeys in both years, but its total fell from 61.2 to 57.8 million. The Northern Line, the second busiest, declined on a similar scale, from 42.0 to 38.5 million. The two smaller lines moved the other way: the Coastal Line rose from 18.4 to 22.1 million and the Valley Line from 9.6 to 11.3 million, so both grew by a substantial proportion of their original size.",
            "Satisfaction in 2023 followed the same division. The Coastal Line scored highest at 84 per cent and the Valley Line second at 79 per cent, whereas the City Loop reached only 66 per cent and the Northern Line the lowest figure of all at 61 per cent.",
        ],
        "modelNotes": [
            "'Followed the same division' states that the two patterns coincide without claiming one caused the other.",
            "Journeys and satisfaction are kept in separate paragraphs so the two units never blur.",
            "The lines are grouped by direction of change rather than taken in table order.",
        ],
        "errorCategoriesWatched": ["unsupported_causal_claim", "invalid_comparison", "list_like_description"],
        "ua": "'Followed the same division' описує збіг. 'Because' стверджував би причину, якої дані не показують.",
    },
    {
        "visual": "W1V-MIX-03", "mode": "timed",
        "targetFeatures": [
            "Health, computing and engineering cluster at the top; humanities trails.",
            "Full-time employment is the most common destination overall.",
            "The two graphics measure different populations and are not equated.",
        ],
        "modelResponse": [
            "The bar chart shows the proportion of graduates in work within six months of finishing their course, by field of study, while the pie chart shows the destinations of all graduates in 2024.",
            "Overall, employment outcomes varied considerably by field, with health, computing and engineering graduates all performing strongly and humanities graduates trailing well behind. Across all graduates taken together, full-time employment was much the most common destination.",
            "Health recorded the highest employment rate, at 92 per cent, closely followed by computing at 90 per cent and engineering at 88 per cent. These three fields were separated by only a few percentage points. Business, at 81 per cent, sat some way below them, and humanities was the clear outlier at 68 per cent, roughly twenty-four points below the leading field.",
            "The pie chart shows what happened to graduates overall. Just over half, 54 per cent, entered full-time employment, and a further 21 per cent went on to further study. Part-time employment accounted for 13 per cent, while 9 per cent were still seeking work and the remaining 3 per cent reported other destinations.",
        ],
        "modelNotes": [
            "The three leading fields are grouped because they cluster, which is more useful than ranking them one by one.",
            "The response never suggests that the pie chart explains the bar chart; they measure different things.",
            "'Trailing well behind' is descriptive rather than evaluative, unlike 'only 68 per cent'.",
        ],
        "errorCategoriesWatched": ["personal_opinion", "invalid_comparison", "lexical_distortion"],
        "ua": "Два візуали можуть вимірювати різні сукупності. Не поясняйте один через інший.",
    },
]

# ---------------------------------------------------------------------------
# Foundation modules. These teach what Task 1 asks for before any single
# visual family is opened, mirroring the eight foundation strategies G3 placed
# ahead of its fifteen question families.
# ---------------------------------------------------------------------------
FOUNDATION_MODULES = [
    {
        "id": "W1F-01",
        "title": "What Writing Task 1 actually asks for",
        "subskill": "task_interpretation",
        "difficulty": "foundation",
        "objectives": [
            "Identify what a Task 1 question requires you to report, and what it explicitly does not.",
            "Read the standard instruction as a list of scoring criteria rather than as boilerplate.",
        ],
        "lesson": [
            "Task 1 allows 20 minutes and requires at least 150 words. Task 2 carries twice the weight, so time spent overrunning here is taken directly from a more valuable task.",
            "The instruction is always a version of: summarise the information by selecting and reporting the main features, and make comparisons where relevant. Every clause in that sentence is a criterion.",
            "'Selecting' means leaving things out. A response that reports every figure has failed the instruction even when every figure is accurate.",
            "'Main features' means what a reader notices first: the largest, the smallest, the fastest change, and the exception to the pattern.",
            "'Make comparisons' means relating figures to each other. A sequence of accurate but unrelated statements is a list, not a report.",
            "Task 1 never asks for reasons, opinions, recommendations or predictions. If the visual cannot show it, it does not belong in the answer.",
        ],
        "workedExamples": [
            {
                "title": "Reading the instruction as criteria",
                "analysis": "Given a graph of three lines over twenty years, 'selecting' rules out a sentence per year, 'main features' points you at the crossover and the steepest line, and 'comparisons where relevant' means the two similar lines should be described together rather than one after the other.",
            },
        ],
        "errorCategories": ["personal_opinion", "unsupported_causal_claim", "timing_failure", "list_like_description"],
        "uaSupport": "Task 1 — це звіт, а не есе. Двадцять хвилин, щонайменше 150 слів, жодних причин, оцінок і порад. Вибірковість — це вимога, а не спрощення.",
    },
    {
        "id": "W1F-02",
        "title": "Building the overview",
        "subskill": "overview_construction",
        "difficulty": "foundation",
        "objectives": [
            "Write a separate overview paragraph that states the largest patterns without figures.",
            "Adapt the overview to the kind of visual in front of you.",
        ],
        "lesson": [
            "The overview is a separate paragraph, normally the second, and it is the highest-value paragraph in the response. A report without one is capped regardless of how accurate the detail is.",
            "It states two or three of the largest patterns, and it contains no individual figures. Figures belong in the body.",
            "For data over time, name the overall direction and the biggest exception to it.",
            "For data at a single moment, name the leader, the trailer, and whether the distribution is even or concentrated.",
            "For a process, give the number of stages, the input, the output, and whether the sequence is linear or cyclical.",
            "For a map or plan, name the change in overall character and say what was retained.",
            "Begin the paragraph with 'Overall,' so that it cannot be mistaken for body detail.",
        ],
        "workedExamples": [
            {
                "title": "Two overviews for the same data",
                "analysis": "'Recycling rose from 28 to 46 per cent in Oslo and from 18 to 61 per cent in Tromso' is body detail wearing an overview's position. 'Recycling improved in all three cities, but far more steeply in Tromso, which finished as the leader' is an overview: same information, no figures, and it tells the reader what to expect from the paragraphs that follow.",
            },
        ],
        "errorCategories": ["missing_overview", "list_like_description"],
        "uaSupport": "Overview — окремий абзац, зазвичай другий, без жодної цифри. Якщо у вашому overview є числа, ви вже пишете body-абзац.",
    },
    {
        "id": "W1F-03",
        "title": "The language of data",
        "subskill": "data_language",
        "difficulty": "foundation",
        "objectives": [
            "Match verbs, adverbs and prepositions to the actual direction and size of a movement.",
            "Keep proportion language separate from quantity language.",
        ],
        "lesson": [
            "Verbs carry direction: rise, climb, fall, decline, level off, peak, bottom out, converge, overtake.",
            "Adverbs carry size: marginally, slightly, gradually, steadily, sharply, dramatically. Match the adverb to the figure rather than to your impression of it.",
            "Prepositions carry meaning. 'Rose to 40' gives the end value, 'rose by 12' gives the size of the change, and 'rose from 28 to 40' gives both. Ukrainian expresses the change with 'на', which maps onto 'by'.",
            "Proportion language belongs to shares: accounted for, represented, made up, a quarter, two fifths, just under half.",
            "The difference between two percentages is measured in percentage points, never in per cent.",
            "Approximation is a precision instrument, not a hedge. 'Just over', 'roughly', 'nearly' and 'well over' each place the figure on a different side of a round number.",
            "A larger share does not prove a larger quantity. Unless the total is shown, only the share can be said to have grown.",
        ],
        "workedExamples": [
            {
                "title": "One figure, four wordings",
                "analysis": "For a move from 12 to 26 per cent: 'rose by 14 percentage points' is exact, 'more than doubled' is exact and more vivid, 'rose by 14 per cent' is wrong because it names the wrong unit, and 'plastic waste more than doubled' is wrong because it converts a share into a quantity the chart never shows.",
            },
        ],
        "errorCategories": ["imprecise_quantity", "lexical_distortion", "article_preposition_transfer"],
        "uaSupport": "Три речі вирішують точність: дієслово (напрям), прислівник (величина) і прийменник (до чи на). Різниця між двома відсотками — 'percentage points'.",
    },
    {
        "id": "W1F-04",
        "title": "Planning, timing and self-review",
        "subskill": "planning_and_timing",
        "difficulty": "foundation",
        "objectives": [
            "Produce a usable plan in about three minutes.",
            "Finish, check and correct inside the twenty minutes Task 1 allows.",
        ],
        "lesson": [
            "Budget roughly three minutes planning, fifteen writing and two checking. The checking time is not optional; it is where the cheapest marks are recovered.",
            "The plan is not a draft. It is the timeframe, the grouping, and the two or three features you intend to report.",
            "Decide the tense during planning, from the dates on the visual. Decided once, it stays consistent by itself.",
            "Write the introduction and the overview first. They are the fastest paragraphs and they fix the structure of everything after them.",
            "If time runs short, a missing body detail costs far less than a missing overview.",
            "Spend the final two minutes on articles, subject-verb agreement and data prepositions, which is where a Ukrainian speaker's remaining errors cluster.",
        ],
        "workedExamples": [
            {
                "title": "A three-minute plan",
                "analysis": "Timeframe: 2005 to 2025, past simple. Grouping: Oslo plus Bergen together, Tromso alone. Features: all rise, Tromso steepest, Tromso overtakes both around 2015. That is the entire plan, and it is enough to write four paragraphs from.",
            },
        ],
        "errorCategories": ["timing_failure", "paragraph_organisation", "article_preposition_transfer", "tense_misuse"],
        "uaSupport": "Три хвилини на план, п'ятнадцять на письмо, дві на перевірку. Останні дві хвилини — артиклі, узгодження і прийменники.",
    },
]

FAMILY_CODE = {
    "line_graph": "LINE",
    "bar_chart": "BAR",
    "pie_chart": "PIE",
    "table": "TAB",
    "process_diagram": "PROC",
    "map_plan": "MAP",
    "mixed_visual": "MIX",
}

# Mastery thresholds for Writing Task 1. Modelled on the Reading precedent in
# PRODUCT_SPEC.md section 4, adapted because Task 1 mastery has to include a
# produced response and not only selected answers. Recorded as D-015.
MASTERY_RULES = {
    "scale": ["Not Assessed", "Introduced", "Guided", "Independent", "Timed", "Mastered"],
    "levels": [
        {"level": 1, "name": "Introduced",
         "rule": "The family lesson has been opened and explicitly marked as introduced.",
         "ua": "Урок відкрито і позначено як ознайомлений."},
        {"level": 2, "name": "Guided",
         "rule": "At least 50% accuracy across the four guided micro-exercises in this family.",
         "ua": "Щонайменше 50% у чотирьох guided-вправах цієї родини."},
        {"level": 3, "name": "Independent",
         "rule": "At least 75% accuracy across the three independent micro-exercises in this family.",
         "ua": "Щонайменше 75% у трьох independent-вправах."},
        {"level": 4, "name": "Timed",
         "rule": "At least 75% across the timed micro-exercises, and at least one full prompt submitted inside its 20-minute limit with the self-review checklist completed.",
         "ua": "Щонайменше 75% у timed-вправах і одна повна відповідь у межах 20 хвилин із заповненим чек-листом."},
        {"level": 5, "name": "Mastered",
         "rule": "At least 85% across three or more distinct exercise sets on at least two different dates, including the mastery-mode exercise, plus at least one timed full response.",
         "ua": "Щонайменше 85% у трьох різних наборах у два різні дні, включно з mastery-вправою, і щонайменше одна повна відповідь у часі."},
    ],
    "note": "Opening a lesson never advances mastery beyond level 1. Full written responses are self-assessed against the checklist; they are training guidance and are never converted into an IELTS band.",
}

BAND_SCORING_NOTE = (
    "These three sample responses illustrate the features that typically separate Task 1 "
    "answers at different levels. The band labels describe the samples, not you, and they "
    "are training guidance produced by this application: they are not an official IELTS "
    "band, and only a qualified examiner can award one."
)

SCORING_NOTE = (
    "Feedback in this academy describes performance against the kinds of thing IELTS Writing "
    "criteria reward. It is training guidance produced by this application. It is not an official "
    "IELTS band and only a qualified examiner can award one."
)



# ---------------------------------------------------------------------------
# Canonical claim manifest (defect D4-006).
#
# The first version of this pipeline authorised any figure "derivable from the
# visual", which included every column total and every pairwise sum. That is
# too permissive: a figure can be arithmetically derivable and still not be the
# figure the item intends, so an item could look grounded while being
# pedagogically wrong.
#
# This model replaces it:
#   - an EXERCISE may cite only the values of the fact keys it declares in
#     `grounding` (plus explicitly declared structural numbers). Nothing else.
#   - a PROMPT or BAND RESPONSE reports a whole visual, so it may cite any fact
#     whose operation is in ALLOWED_REPORT_OPS. `total` and `sum` are NOT in
#     that set and must be authorised per item in `extraOps`.
#   - every year mentioned must be a real time label of that visual.
#   - every unit word mentioned must be compatible with that visual's unit.
#
# The generator refuses to build if any of this fails, and
# tests/g4_writing1_claims.py re-derives all of it independently.
# ---------------------------------------------------------------------------

# Operations a full report may perform on its own visual without extra
# authorisation. Deliberately excludes total/sum.
ALLOWED_REPORT_OPS = {
    "value", "first", "last", "max", "min", "max_at", "min_at", "delta",
    "pct_change", "change", "gap", "share", "delta_share", "largest",
    "smallest", "rank", "top", "bottom", "stage", "stage_count",
    "first_stage", "last_stage", "input", "output", "cyclical",
    "status", "area", "count", "feature_count",
}
RESTRICTED_OPS = {"total", "sum"}

# Structural numbers a text may use that are not data at all. Capped at 10 and
# each one has to be declared on the item.
MAX_STRUCTURAL_NUMBER = 10

UNIT_LEXICON = [
    (r"percentage points?", "%"),
    (r"per cent|percent\b|%", "%"),
    (r"million", "million"),
    (r"thousand", "thousand"),
    (r"terawatt-hours?|TWh", "terawatt-hour"),
    (r"pounds?\b", "pound"),
    (r"nights?\b", "night"),
    (r"index", "index"),
    (r"tonnes?\b", "tonne"),
    (r"stages?\b", "stage"),
]

TASK_LABEL_RE = re.compile(r"\bTask\s*[12]\b|\bBand\s*[0-9]\b", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
NUM_RE = re.compile(r"\d+(?:\.\d+)?")


def strip_labels(text):
    """Remove exam-vocabulary labels that are names, not data claims."""
    return TASK_LABEL_RE.sub("Task", str(text))


def figures_in(text):
    return {_round(float(t)) for t in NUM_RE.findall(strip_labels(text))}


def years_in(text):
    return {int(m.group(0)) for m in YEAR_RE.finditer(strip_labels(text))}


def fact_op(key):
    k = key.split(".", 1)[1] if re.match(r"^c\d+\.", key) else key
    return k.split(".", 1)[0]


def visual_time_labels(v):
    """Every time reference this visual legitimately contains."""
    out = set()

    def scan(s):
        for m in YEAR_RE.finditer(str(s)):
            out.add(int(m.group(0)))

    scan(v.get("timeframe", ""))
    for c in [v] + list(v.get("components", [])):
        for cat in c.get("categories", []) or []:
            scan(cat)
        for col in c.get("columns", []) or []:
            scan(col)
        for snap in c.get("snapshots", []) or []:
            scan(snap.get("label", ""))
        for per in c.get("periods", []) or []:
            scan(per)
    return out


def visual_label_figures(v):
    """Figures printed on the visual itself: axis categories, column and row
    headings, snapshot labels, periods, the declared unit (an index base, say)
    and stage numbers. These are labels, not derived claims."""
    out = set()

    def scan(x):
        for t in NUM_RE.findall(str(x)):
            out.add(_round(float(t)))

    for c in [v] + list(v.get("components", []) or []):
        for cat in c.get("categories", []) or []:
            scan(cat)
        for col in c.get("columns", []) or []:
            scan(col)
        for r in c.get("rows", []) or []:
            scan(r.get("label", ""))
        for snap in c.get("snapshots", []) or []:
            scan(snap.get("label", ""))
        scan(c.get("unit", ""))
        scan(c.get("axisLabel", ""))
    for per in v.get("periods", []) or []:
        scan(per)
    scan(v.get("timeframe", ""))
    if v["kind"] == "process":
        out.update(range(1, len(v["stages"]) + 1))
    return out


def visual_unit_corpus(v):
    parts = [v.get("unit", ""), v.get("axisLabel", "")]
    for c in v.get("components", []) or []:
        parts += [c.get("unit", ""), c.get("axisLabel", "")]
        parts += list(c.get("columns", []) or [])
    parts += list(v.get("columns", []) or [])
    if v["kind"] in ("process",):
        parts.append("stages")
    return " ".join(str(x) for x in parts).lower()


def units_in(text):
    found = set()
    low = str(text).lower()
    for pattern, token in UNIT_LEXICON:
        if re.search(pattern, low):
            found.add(token)
    return found


def report_figures(v, extra_ops=()):
    """Figures a whole-visual report may cite without further authorisation."""
    allowed = set(ALLOWED_REPORT_OPS) | set(extra_ops)
    nums = set()
    for key, val in compute_facts(v).items():
        if fact_op(key) in allowed and isinstance(val, (int, float)) and not isinstance(val, bool):
            nums.add(_round(val))
            nums.add(_round(abs(val)))
    nums |= visual_time_labels(v) | visual_label_figures(v)
    return nums


def grounded_figures(v, keys, extra_ops=()):
    """Figures an exercise may cite: only the values of the keys it declares."""
    facts = compute_facts(v)
    nums = set()
    for k in keys:
        if k not in facts:
            raise SystemExit(f"BUILD FAIL: grounding key {k!r} is not derivable from {v['id']}")
        val = facts[k]
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            nums.add(_round(val))
            nums.add(_round(abs(val)))
    # Any op the item explicitly authorises beyond its declared keys.
    if extra_ops:
        for key, val in facts.items():
            if fact_op(key) in set(extra_ops) and isinstance(val, (int, float)) and not isinstance(val, bool):
                nums.add(_round(val))
                nums.add(_round(abs(val)))
    nums |= visual_time_labels(v) | visual_label_figures(v)
    return nums


def check_text(where, v, text, authorised, structural, unit_corpus, time_labels, problems, deliberate=()):
    facts = compute_facts(v)
    deliberate = {_round(x) for x in deliberate}
    for n in figures_in(text):
        if n in authorised or n in structural or n in deliberate:
            continue
        # Name the keys that would authorise it, so the fix is to declare the
        # intended derivation rather than to widen the rule.
        cands = [k for k, val in facts.items()
                 if isinstance(val, (int, float)) and not isinstance(val, bool) and _round(abs(val)) == n][:4]
        hint = f" — declare one of {cands}" if cands else " — no fact of this visual has that value"
        problems.append(f"{where}: cites {n}, which is not an authorised figure for {v['id']}{hint}")
    for y in years_in(text):
        if y in deliberate:
            continue
        if y not in time_labels:
            problems.append(f"{where}: refers to {y}, which is not a time label of {v['id']}")
    for u in units_in(text):
        if u not in unit_corpus:
            problems.append(f"{where}: uses unit {u!r}, which {v['id']} does not measure in")


def unit_tokens_of(v):
    corpus = visual_unit_corpus(v)
    return {tok for _, tok in UNIT_LEXICON if re.search(_unit_pattern(tok), corpus)}


def _unit_pattern(tok):
    return {"%": r"%|per cent|percent", "million": "million", "thousand": "thousand",
            "terawatt-hour": r"terawatt|twh", "pound": "pound", "night": "night",
            "index": "index", "tonne": "tonne", "stage": "stage"}[tok]


# ---------------------------------------------------------------------------
# Band comparison lab (REQ-019). One set per visual family: the same task
# answered three ways, so the learner can see what actually separates the
# levels.
#
# Deliberate design rule: EVERY FIGURE IN EVERY SAMPLE IS ACCURATE. The
# differences between the three responses are structural and linguistic --
# overview, grouping, quantity language, tense, cohesion -- because that is
# what genuinely separates Task 1 responses. Inventing wrong numbers for the
# weaker sample would teach the wrong lesson and would also make the grounding
# check meaningless.
#
# The band labels describe the sample responses, not the learner. Nothing here
# scores anyone (PROJECT_CHARTER.md section 4.9).
# ---------------------------------------------------------------------------
BAND_LEVELS = [
    {"id": "b6", "level": "Band 6", "label": "Developing",
     "ua": "Дані є, але немає структури: перелік замість звіту."},
    {"id": "b7", "level": "Band 7", "label": "Competent",
     "ua": "Є overview і групування, але формулювання ще базові."},
    {"id": "b8", "level": "Band 8", "label": "Strong",
     "ua": "Overview без цифр, впевнене групування, точна мова кількості."},
]

BAND_ASPECTS = ["Overview", "Selection and grouping", "Quantity language", "Cohesion", "Grammar and tense"]

BAND_SETS = [
    # ------------------------------- line graph -------------------------------
    {
        "family": "line_graph", "visual": "W1V-LINE-01",
        "focus": "What separates a year-by-year list from a report about shape.",
        "responses": {
            "b6": {
                "text": [
                    "The line graph shows the recycling of household waste in three cities from 2005 to 2025.",
                    "In 2005, Oslo was 28 per cent, Bergen was 31 per cent and Tromso was 18 per cent. In 2010, Oslo was 34 per cent, Bergen was 36 per cent and Tromso was 27 per cent. In 2015, Oslo was 39 per cent, Bergen was 40 per cent and Tromso was 41 per cent.",
                    "In 2020, Oslo was 43 per cent, Bergen was 42 per cent and Tromso was 52 per cent. In 2025, Oslo was 46 per cent, Bergen was 44 per cent and Tromso was 61 per cent.",
                    "So we can see that all the cities increased their recycling and Tromso increased the most.",
                ],
                "does": ["Reports accurate figures.", "Covers the whole period."],
                "missing": ["No separate overview; the general statement is buried at the end.",
                            "Organised by year, so the three cities are never compared with each other.",
                            "The crossover, which is the point of the graph, is never mentioned.",
                            "Repetitive sentence pattern throughout."],
            },
            "b7": {
                "text": [
                    "The line graph compares the percentage of household waste that was recycled in Oslo, Bergen and Tromso between 2005 and 2025.",
                    "Overall, recycling increased in all three cities during the period, and Tromso increased the most, rising from 18 per cent to 61 per cent.",
                    "Oslo and Bergen were quite similar. Oslo rose steadily from 28 per cent in 2005 to 46 per cent in 2025, while Bergen rose from 31 per cent to 44 per cent. Bergen was higher than Oslo at the start but lower at the end.",
                    "Tromso was different. It started at the lowest point of 18 per cent, but it grew quickly and passed the other two cities by 2015, when it reached 41 per cent. After that it continued to rise to 61 per cent.",
                ],
                "does": ["Has a clearly separate overview.", "Groups the two similar cities together and contrasts the outlier.",
                         "Reports the crossover."],
                "missing": ["The overview spends figures that belong in the body.",
                            "Quantity language stays general: 'grew quickly', 'quite similar'.",
                            "Sentence openings are simple and repeat."],
            },
            "b8": {
                "text": [
                    "The line graph compares the proportion of household waste recycled in Oslo, Bergen and Tromso at regular intervals between 2005 and 2025.",
                    "Overall, recycling rates improved in all three cities, but the increase in Tromso was far steeper than elsewhere, and the city moved from last place to first.",
                    "Oslo and Bergen followed closely comparable paths. Bergen began marginally ahead, at 31 per cent against Oslo's 28 per cent, and both climbed gradually throughout, so that by 2025 the small gap between them had reversed rather than widened, at 46 and 44 per cent respectively.",
                    "Tromso behaved quite differently. Starting from the lowest figure of 18 per cent, it rose without interruption, had already overtaken both other cities by 2015, and finished at 61 per cent, more than three times its opening figure.",
                ],
                "does": ["Overview states the shared pattern, the contrast and the change of rank, with no figures.",
                         "Grouping is announced and then delivered.",
                         "Adverbs are sized to the movement: 'marginally', 'gradually', 'far steeper'.",
                         "Varied structures, including a participle opening and 'respectively'."],
                "missing": [],
            },
        },
        "comparison": [
            {"aspect": "Overview", "b6": "Absent; a conclusion-like sentence at the end.", "b7": "Present but carries figures.", "b8": "Present, figure-free, states pattern plus change of rank."},
            {"aspect": "Selection and grouping", "b6": "Organised by year, so nothing is compared.", "b7": "Two similar cities grouped, outlier contrasted.", "b8": "Same grouping, but the contrast is signposted and sustained."},
            {"aspect": "Quantity language", "b6": "'Increased the most' only.", "b7": "'Grew quickly', 'steadily'.", "b8": "'Marginally', 'gradually', 'far steeper', 'more than three times'."},
            {"aspect": "Cohesion", "b6": "'In 2005... In 2010... In 2015...'", "b7": "'while', 'but', 'After that'.", "b8": "'so that', 'rather than', 'had already', referencing across sentences."},
            {"aspect": "Grammar and tense", "b6": "Correct but very limited range.", "b7": "Correct, mostly simple sentences.", "b8": "Past perfect used deliberately to sequence the overtaking."},
        ],
        "takeaway": "The figures are identical in all three responses. What changes is whether the report is organised by time or by behaviour, and whether the overview earns its place.",
        "ua": "Цифри в усіх трьох відповідях однакові. Різниця — в структурі: організація за роками чи за поведінкою ліній, і чи є справжнє overview.",
    },
    # ------------------------------- bar chart -------------------------------
    {
        "family": "bar_chart", "visual": "W1V-BAR-01",
        "focus": "What separates reading four bars per group from reporting a ranking and its exception.",
        "responses": {
            "b6": {
                "text": [
                    "The bar chart gives information about the spending on leisure of three age groups.",
                    "The 18-29 group spent 42 pounds on eating out, 27 pounds on live events, 9 pounds on cultural visits and 15 pounds on streaming services.",
                    "The 30-49 group spent 38 pounds on eating out, 18 pounds on live events, 14 pounds on cultural visits and 12 pounds on streaming services.",
                    "The 50 and over group spent 31 pounds on eating out, 8 pounds on live events, 22 pounds on cultural visits and 6 pounds on streaming services. Eating out is the biggest in all the groups.",
                ],
                "does": ["Every figure is accurate.", "Covers all twelve bars."],
                "missing": ["No overview paragraph.",
                            "One paragraph per age group means each category is described three separate times.",
                            "The reversal, which is the feature the chart was built around, is never stated.",
                            "'Is' for a dated survey; tense is inconsistent with the rest."],
            },
            "b7": {
                "text": [
                    "The bar chart compares how much three age groups spent each week on four leisure activities.",
                    "Overall, eating out was the highest category for every age group, at 42, 38 and 31 pounds, and most categories fell as people got older.",
                    "Eating out, live events and streaming services all decreased with age. Live events fell the most, from 27 pounds in the youngest group to 8 pounds in the oldest, and streaming services fell from 15 pounds to 6 pounds.",
                    "Cultural visits was the opposite. It was only 9 pounds for the 18-29 group, but it rose to 14 pounds and then 22 pounds, so it became bigger than live events in the oldest group.",
                ],
                "does": ["Separate overview.", "Groups the three falling categories together and contrasts the riser.",
                         "Reports the change of rank."],
                "missing": ["Overview carries three figures.",
                            "'Bigger than' and 'fell the most' are imprecise where a proportion would be sharper.",
                            "Limited range of comparative structures."],
            },
            "b8": {
                "text": [
                    "The bar chart compares average weekly spending on four leisure activities across three age groups.",
                    "Overall, eating out attracted the highest expenditure in every age group, but the relative position of the other three activities changed considerably with age, as most fell while one rose.",
                    "Three categories declined as respondents got older. Eating out fell from 42 pounds a week among those aged 18 to 29 to 31 pounds among those aged 50 and over, while live events dropped far more steeply, from 27 pounds to 8 pounds, ending at under a third of its original level. Streaming services followed the same direction, falling from 15 pounds to 6 pounds.",
                    "Cultural visits moved the other way, rising from 9 pounds among the youngest respondents to 22 pounds among the oldest, and overtaking live events in the process.",
                ],
                "does": ["Overview holds the constant and the variation together, with no figures.",
                         "Grouping by behaviour, so four descriptions become two comparisons.",
                         "'Under a third' is checked arithmetic, not an impression.",
                         "The change of rank closes the report."],
                "missing": [],
            },
        },
        "comparison": [
            {"aspect": "Overview", "b6": "None.", "b7": "Present, but spends three figures.", "b8": "Present, figure-free, names the constant and the exception."},
            {"aspect": "Selection and grouping", "b6": "One paragraph per age group; every category described three times.", "b7": "Grouped by direction of change.", "b8": "Same grouping, with the exception deliberately placed last."},
            {"aspect": "Quantity language", "b6": "'Biggest'.", "b7": "'Fell the most', 'bigger than'.", "b8": "'Far more steeply', 'under a third of its original level'."},
            {"aspect": "Cohesion", "b6": "Three parallel paragraphs with no linking.", "b7": "'but', 'so', 'the opposite'.", "b8": "'while', 'followed the same direction', 'in the process'."},
            {"aspect": "Grammar and tense", "b6": "Slips into present ('is the biggest') for dated data.", "b7": "Consistent past simple.", "b8": "Consistent past simple with participle and comparative structures."},
        ],
        "takeaway": "A grouped bar chart is scored on comparison. Organising by age group guarantees a list; organising by behaviour guarantees a comparison.",
        "ua": "Згрупована діаграма оцінюється за порівнянням. Абзац на вікову групу гарантує перелік; абзац на поведінку категорії гарантує порівняння.",
    },
    # ------------------------------- pie charts -------------------------------
    {
        "family": "pie_chart", "visual": "W1V-PIE-02",
        "focus": "What separates a share claim from an unsupported claim about quantity.",
        "responses": {
            "b6": {
                "text": [
                    "The pie charts show the municipal waste of a city in 2000 and 2020.",
                    "In 2000 organic was 42 per cent, paper was 24 per cent, plastics was 12 per cent, glass was 9 per cent, metal was 7 per cent and other was 6 per cent.",
                    "In 2020 organic was 31 per cent, paper was 15 per cent, plastics was 26 per cent, glass was 10 per cent, metal was 8 per cent and other was 10 per cent.",
                    "We can see that the city produced much more plastic waste in 2020 and less organic waste, so the situation became worse for the environment.",
                ],
                "does": ["All twelve percentages are accurate."],
                "missing": ["No overview; one paragraph per chart means the reader has to work out the changes.",
                            "'Produced much more plastic waste' converts a share into a quantity the charts never show.",
                            "'The situation became worse' is an evaluation, which Task 1 does not make.",
                            "No grouping of the categories that barely moved."],
            },
            "b7": {
                "text": [
                    "The two pie charts compare the composition of municipal waste in one city in 2000 and 2020.",
                    "Overall, the share of organic waste fell from 42 per cent to 31 per cent while the share of plastics rose from 12 per cent to 26 per cent, so the composition became more balanced.",
                    "Organic material was the largest category in both years, but it lost 11 percentage points. Paper also fell, from 24 per cent to 15 per cent. Plastics more than doubled its share and became the second largest category in 2020.",
                    "The other categories did not change much. Glass went from 9 to 10 per cent, metal from 7 to 8 per cent and other waste from 6 to 10 per cent.",
                ],
                "does": ["Separate overview.", "Keeps every claim inside 'share', never 'amount'.",
                         "Uses 'percentage points' correctly.", "Groups the stable categories."],
                "missing": ["Overview carries four figures.",
                            "'Did not change much' is vaguer than the data allows.",
                            "The change of rank between paper and plastics is implied rather than stated."],
            },
            "b8": {
                "text": [
                    "The two pie charts compare the composition of municipal waste in one city in 2000 and in 2020.",
                    "Overall, the mixture became noticeably more evenly distributed over the twenty years. Organic material remained the largest component in both years but lost a substantial part of its share, while plastics grew rapidly to become the second largest category.",
                    "The three categories that changed most were organic waste, paper and plastics. Organic material fell from 42 per cent of the total in 2000 to 31 per cent in 2020, and paper declined even more steeply in proportional terms, from 24 per cent to 15 per cent. Plastics moved in the opposite direction, more than doubling its share from 12 per cent to 26 per cent and displacing paper from second place.",
                    "The remaining categories were far more stable. Glass edged up from 9 to 10 per cent and metal from 7 to 8 per cent, while other waste rose from 6 to 10 per cent. None of these three shifted by more than four percentage points.",
                ],
                "does": ["Figure-free overview describing the distribution as a whole.",
                         "Grouped by size of movement, which is what paired pies reward.",
                         "'In proportional terms' makes the comparison between two falls valid.",
                         "The change of rank is stated explicitly."],
                "missing": [],
            },
        },
        "comparison": [
            {"aspect": "Overview", "b6": "None; a conclusion that evaluates.", "b7": "Present, but four figures in it.", "b8": "Present, figure-free, describes the whole distribution."},
            {"aspect": "Selection and grouping", "b6": "One paragraph per chart.", "b7": "Movers and stable categories separated.", "b8": "Same split, with the threshold made explicit."},
            {"aspect": "Quantity language", "b6": "'Much more plastic waste' — a quantity claim the chart cannot support.", "b7": "Correct 'share' language and 'percentage points'.", "b8": "Adds 'in proportional terms' to compare two unequal falls."},
            {"aspect": "Cohesion", "b6": "Two parallel lists.", "b7": "'but', 'also', 'did not change much'.", "b8": "'while', 'in the opposite direction', 'displacing', 'None of these three'."},
            {"aspect": "Grammar and tense", "b6": "Evaluative language; 'we can see'.", "b7": "Consistent past simple.", "b8": "Consistent past simple with participle clauses."},
        ],
        "takeaway": "A pie chart shows shares. Unless the total is given, a bigger slice never proves a bigger quantity, and this is the single most common way Task 1 pie responses lose marks.",
        "ua": "Кругова діаграма показує частки. Якщо загальна сума не вказана, більший сектор не доводить більший обсяг — це найчастіша втрата балів у цій родині.",
    },
    # --------------------------------- table ---------------------------------
    {
        "family": "table", "visual": "W1V-TAB-01",
        "focus": "What separates reciting twenty cells from selecting the pattern and its exception.",
        "responses": {
            "b6": {
                "text": [
                    "The table is about tourists in five destinations in 2019 and 2023.",
                    "Coastal Bay had 4.2 million arrivals in 2019 and 5.1 million in 2023, and the stay was 6.8 nights and then 5.9 nights. Lakeside had 2.7 million and 3.4 million, with 5.2 and 4.6 nights.",
                    "Old Harbour had 6.5 million and 7.2 million, with 4.1 and 3.7 nights. Highland Park had 1.8 million and 2.3 million, with 7.4 and 7.6 nights.",
                    "Riverford had 3.9 million and 3.1 million, with 3.6 and 3.2 nights. Old Harbour had the most arrivals.",
                ],
                "does": ["Every one of the twenty cells is accurate."],
                "missing": ["No overview.",
                            "One paragraph per destination, so nothing is selected and nothing is compared.",
                            "Neither exception is identified.",
                            "The relationship between the two measures is never noticed."],
            },
            "b7": {
                "text": [
                    "The table shows the number of tourist arrivals and the average length of stay in five destinations in 2019 and 2023.",
                    "Overall, arrivals rose in four of the five destinations, but the average stay became shorter in four of them, so the two measures moved in different directions.",
                    "Arrivals increased in Coastal Bay, Lakeside, Old Harbour and Highland Park. Old Harbour had the most arrivals in both years, with 6.5 million and then 7.2 million. Riverford was the only destination where arrivals fell, from 3.9 million to 3.1 million.",
                    "For length of stay, Coastal Bay had the biggest fall, from 6.8 nights to 5.9 nights. Highland Park was the only destination where the stay became longer, from 7.4 to 7.6 nights.",
                ],
                "does": ["Separate overview that relates the two measures.",
                         "Organised by measure, not by destination.",
                         "Both exceptions named."],
                "missing": ["The overview states the counts, which is body detail.",
                            "'Biggest fall' is accurate but unquantified.",
                            "Several destinations are listed rather than grouped."],
            },
            "b8": {
                "text": [
                    "The table compares tourist arrivals and the average length of stay in five destinations in 2019 and 2023.",
                    "Overall, most destinations received more visitors in 2023 than in 2019, but those visitors tended to stay for shorter periods, so the two measures generally moved in opposite directions. Each measure had a single exception.",
                    "Arrivals increased in all but one destination. Old Harbour remained the busiest, rising from 6.5 to 7.2 million, while Coastal Bay grew from 4.2 to 5.1 million and Lakeside from 2.7 to 3.4 million. Riverford was the only destination to lose visitors, falling from 3.9 to 3.1 million.",
                    "Length of stay moved the other way almost everywhere, with Coastal Bay recording the largest reduction, from 6.8 to 5.9 nights. Highland Park was the exception, edging up from 7.4 to 7.6 nights and retaining the longest average stay of any destination.",
                ],
                "does": ["Figure-free overview that names the relationship and flags that each measure has an exception.",
                         "Twenty cells covered in two paragraphs by reporting direction plus exception.",
                         "'Edging up' sized to a 0.2-night movement."],
                "missing": [],
            },
        },
        "comparison": [
            {"aspect": "Overview", "b6": "None.", "b7": "Present, but counts belong in the body.", "b8": "Present, figure-free, and predicts the structure of the body."},
            {"aspect": "Selection and grouping", "b6": "Row by row; nothing left out.", "b7": "By measure, with exceptions named.", "b8": "By measure, with destinations grouped inside each."},
            {"aspect": "Quantity language", "b6": "'The most arrivals'.", "b7": "'Biggest fall', 'only destination'.", "b8": "'Largest reduction', 'edging up', 'retaining the longest'."},
            {"aspect": "Cohesion", "b6": "'and then', repeated.", "b7": "'For length of stay', 'was the only'.", "b8": "'while', 'the other way almost everywhere', 'the exception'."},
            {"aspect": "Grammar and tense", "b6": "Simple past throughout, very limited range.", "b7": "Correct, some variety.", "b8": "Participle clauses and a non-finite closing structure."},
        ],
        "takeaway": "A table over-supplies data on purpose. Leaving cells out is not laziness; it is the skill being scored.",
        "ua": "Таблиця навмисно дає надлишок даних. Відкидати зайве — це не лінощі, а саме те вміння, яке оцінюється.",
    },
    # ---------------------------- process diagram ----------------------------
    {
        "family": "process_diagram", "visual": "W1V-PROC-01",
        "focus": "What separates a chain of 'then' from a sequenced report with the right voice.",
        "responses": {
            "b6": {
                "text": [
                    "The diagram showed how the glass bottles were recycled.",
                    "First people collected the used bottles from the bins. Then a lorry transported them to a plant. Then workers removed the items which were not glass by hand.",
                    "Then they separated the glass into clear, green and brown. Then they crushed it into cullet. Then they melted the cullet in a furnace.",
                    "Then they moulded the molten glass into new bottles. Then the bottles were filled and they were sold in the shops.",
                    "Then the empty bottles came back to the collection again and the whole process started one more time from the beginning. So it is a circle with eight steps in total.",
                ],
                "does": ["The sequence is complete and in the right order.", "Notices that the process returns to the start."],
                "missing": ["No overview: no stage count, no input or output, no statement that the process is cyclical.",
                            "Past tense throughout for a diagram that carries no dates.",
                            "Seven consecutive sentences begin with 'Then'.",
                            "Active voice with an invented agent ('people', 'workers') where the diagram names none."],
            },
            "b7": {
                "text": [
                    "The diagram shows the process of recycling glass bottles.",
                    "Overall, there are eight stages in the process. It starts with the collection of used bottles and ends with new bottles, which go back to the collection stage, so it is a cycle.",
                    "At the first stage, used bottles are collected from household and public bins, and they are transported by lorry to a processing plant. After that, items which are not glass are removed by hand, and the glass is separated into clear, green and brown.",
                    "The separated glass is then crushed into cullet and melted in a furnace. The molten glass is moulded into new bottles, and finally these bottles are filled, distributed and returned to the collection stage.",
                ],
                "does": ["Overview gives the stage count, the input, the output and the cyclical shape.",
                         "Present simple passive, correct for an undated man-made process.",
                         "Varied sequencing linkers."],
                "missing": ["The two paragraphs split at an arbitrary point rather than a real boundary in the process.",
                            "'It is a cycle' is plainer than the sentence needs to be.",
                            "Some clauses are joined with 'and' where subordination would be tighter."],
            },
            "b8": {
                "text": [
                    "The diagram illustrates the process by which used glass bottles are recycled and returned to use.",
                    "Overall, the process consists of eight stages and forms a closed loop, beginning with the collection of used bottles and ending with new bottles that re-enter the same collection system. It can be divided into a preparation phase and a remanufacturing phase.",
                    "In the first phase, the material is made ready. Used bottles are collected from household and public bins and transported by lorry to a processing plant. There, non-glass items are removed by hand, after which the glass is separated into clear, green and brown streams. The sorted glass is then crushed into small fragments known as cullet.",
                    "The second phase creates the new product. The cullet is melted in a furnace until it becomes molten glass, which is moulded into the shape of new bottles. Once these bottles have been filled and distributed, they are eventually returned to the collection stage, at which point the cycle begins again.",
                ],
                "does": ["Overview adds the structural split the body then delivers.",
                         "Paragraph break falls at the furnace, a real boundary in the process.",
                         "Present simple passive throughout, with present perfect passive to sequence.",
                         "No temperature, duration or purpose is invented."],
                "missing": [],
            },
        },
        "comparison": [
            {"aspect": "Overview", "b6": "None.", "b7": "Count, input, output and cycle.", "b8": "Same, plus the structural split that organises the body."},
            {"aspect": "Selection and grouping", "b6": "Stage by stage, no grouping.", "b7": "Two paragraphs, arbitrary split.", "b8": "Two phases divided at a real boundary."},
            {"aspect": "Quantity language", "b6": "Not applicable; no data in a process.", "b7": "'Eight stages'.", "b8": "'Eight stages', 'closed loop', phase naming."},
            {"aspect": "Cohesion", "b6": "'Then' seven times.", "b7": "'At the first stage', 'After that', 'finally'.", "b8": "'after which', 'Once... have been', 'at which point'."},
            {"aspect": "Grammar and tense", "b6": "Past simple for an undated process; invented human agents.", "b7": "Present simple passive, correct.", "b8": "Present simple passive plus present perfect passive for sequence."},
        ],
        "takeaway": "A diagram with no dates has no past tense, and the agent is almost never shown, which is why the passive is the default. Varying the linkers is what stops the report reading as a chain of 'then'.",
        "ua": "Схема без дат не має минулого часу, а виконавця зазвичай не показано — тому пасив є типовим. Різні сполучники рятують текст від ланцюжка 'then'.",
    },
    # ------------------------------- map / plan -------------------------------
    {
        "family": "map_plan", "visual": "W1V-MAP-01",
        "focus": "What separates pointing at a map from describing it to someone who cannot see it.",
        "responses": {
            "b6": {
                "text": [
                    "The maps show the village of Whitmore in 1985 and now.",
                    "Here there was farmland before and now there are houses. This building was the shop and now it is a supermarket.",
                    "The cattle market is not here any more, they demolished it and made a car park. There is a new road on this side of the village now.",
                    "The woodland is still there and the school also, they did not change them at all.",
                    "So the village had farms before and now it has houses instead, and there are more shops and roads than before. The village is much more modern now and it is better for the people who live there.",
                ],
                "does": ["Identifies most of the changes.", "Notices that the woodland and the school were retained."],
                "missing": ["'Here', 'this side', 'this building' are unusable for a reader who cannot see the map.",
                            "No overview stating what the village became.",
                            "No compass directions anywhere.",
                            "'Better for the people who live there' is an evaluation."],
            },
            "b7": {
                "text": [
                    "The two maps show how the village of Whitmore changed between 1985 and the present day.",
                    "Overall, Whitmore changed from a farming village into a residential village, and most of the changes happened in the south and in the centre.",
                    "In the south, the farmland was removed and a housing estate was built in its place. A new bypass road was also built on the eastern side of the village.",
                    "In the centre, the village shop became a supermarket and the cattle market was demolished and replaced by a car park. In the north the woodland was not changed, and the primary school in the west also stayed the same.",
                ],
                "does": ["Overview names the change in character and locates it broadly.",
                         "Every change is located with a compass direction.",
                         "Retained features are reported."],
                "missing": ["Two dated maps, one of which is 'the present day', so present perfect would be more accurate than past simple.",
                            "'Was not changed' and 'stayed the same' are plainer than needed.",
                            "The supermarket occupying the same footprint is not distinguished from a rebuild."],
            },
            "b8": {
                "text": [
                    "The two maps compare the village of Whitmore as it appeared in 1985 with the village as it is today.",
                    "Overall, Whitmore has changed from a largely agricultural settlement into a residential one. The most substantial redevelopment has taken place in the south and in the centre, while the woodland along the northern boundary and the school in the west have been left as they were.",
                    "The greatest change is in the south. The farmland that once bordered the village on that side has been cleared entirely and a housing estate now occupies the site. A bypass road has also been constructed along the eastern edge of the village.",
                    "The centre has been redeveloped rather than expanded. The village shop has been converted into a supermarket occupying the same footprint, and the cattle market that stood nearby has been demolished and replaced by a car park.",
                ],
                "does": ["Overview names the change in character and what survived, in one sentence.",
                         "Present perfect throughout, correct for a dated map against today.",
                         "Distinguishes conversion on the same footprint from demolition and rebuilding.",
                         "'Redeveloped rather than expanded' characterises the centre before describing it."],
                "missing": [],
            },
        },
        "comparison": [
            {"aspect": "Overview", "b6": "None; an evaluation instead.", "b7": "Present, names the change in character.", "b8": "Present, and adds what was retained."},
            {"aspect": "Selection and grouping", "b6": "Random order.", "b7": "Grouped by area.", "b8": "Grouped by area, largest change first."},
            {"aspect": "Quantity language", "b6": "Not applicable; classification language instead.", "b7": "'Removed', 'built', 'demolished'.", "b8": "'Cleared entirely', 'converted', 'occupying the same footprint', 'left as they were'."},
            {"aspect": "Cohesion", "b6": "'Here', 'this', 'also'.", "b7": "'In the south', 'In the centre', 'In the north'.", "b8": "'that once bordered', 'rather than', 'while'."},
            {"aspect": "Grammar and tense", "b6": "Present and past mixed; evaluative closing.", "b7": "Past simple, though the second map is the present day.", "b8": "Present perfect, correct for a dated map against today."},
        ],
        "takeaway": "The reader cannot see the map. Every change needs a compass direction or a named neighbour, and every feature needs classifying as added, removed, replaced or unchanged.",
        "ua": "Читач не бачить карти. Кожна зміна потребує сторони світу або орієнтира, а кожен об'єкт — класифікації: додано, прибрано, замінено чи збережено.",
    },
    # ------------------------------ mixed visuals ------------------------------
    {
        "family": "mixed_visual", "visual": "W1V-MIX-01",
        "focus": "What separates two mini-reports from one report about two graphics.",
        "responses": {
            "b6": {
                "text": [
                    "The line graph shows the electricity consumption and the pie chart shows the sources.",
                    "Overall, the consumption of electricity increased a lot during the period. It was 310 terawatt-hours in 2010, 335 in 2013, 356 in 2016, 372 in 2019, 374 in 2022 and 376 in 2024.",
                    "Now I will describe the second chart. Overall, renewables were the biggest source of electricity in 2024.",
                    "Renewables were 38 per cent, natural gas was 27 per cent, nuclear was 19 per cent, coal was 11 per cent and other sources were 5 per cent.",
                ],
                "does": ["All figures are accurate.", "Both graphics are covered."],
                "missing": ["Two separate overviews, one per chart, instead of one covering both.",
                            "No sentence uses both graphics in the same claim.",
                            "'Increased a lot' misses that the line flattens after 2019.",
                            "'Now I will describe' announces the structure instead of using it."],
            },
            "b7": {
                "text": [
                    "The line graph shows total electricity consumption between 2010 and 2024, and the pie chart shows where that electricity came from in 2024.",
                    "Overall, consumption increased during the period but stopped growing near the end, and by 2024 renewables provided more electricity than any other source.",
                    "Consumption rose from 310 terawatt-hours in 2010 to 372 terawatt-hours in 2019. After 2019 the increase was very small, and the figure only reached 376 terawatt-hours in 2024.",
                    "In 2024, renewables provided 38 per cent of the electricity, which was more than natural gas at 27 per cent and nuclear at 19 per cent. Coal provided only 11 per cent and other sources 5 per cent.",
                ],
                "does": ["One overview that reaches into both graphics.",
                         "Notices that the line flattens.",
                         "Keeps terawatt-hours and percentages separate."],
                "missing": ["No sentence explicitly links the demand in chart one to the mix in chart two.",
                            "'Only 11 per cent' is a small evaluative slip.",
                            "'Very small' is vaguer than the figures allow."],
            },
            "b8": {
                "text": [
                    "The line graph shows total electricity consumption in one country between 2010 and 2024, while the pie chart breaks down the sources of that electricity in 2024.",
                    "Overall, consumption grew considerably during the first part of the period before levelling off, and by the end renewables supplied a larger share of that electricity than any other single source.",
                    "Consumption climbed steadily in the earlier years, rising from 310 terawatt-hours in 2010 to 335 in 2013 and 356 in 2016, before reaching 372 terawatt-hours in 2019. After that point growth almost stopped: the figure stood at 374 in 2022 and only 376 in 2024.",
                    "The pie chart shows how that demand was met at the end of the period. Renewables were the largest single source, at 38 per cent of supply, ahead of natural gas at 27 per cent and nuclear at 19 per cent. Coal, at 11 per cent, had become a minor contributor, and other sources supplied the remaining 5 per cent.",
                ],
                "does": ["One overview covering both graphics and no figures in it.",
                         "'That electricity' and 'that demand' tie the pie chart back to the line graph.",
                         "'Levelling off' names where the line changes character.",
                         "Units are never mixed in a single comparison."],
                "missing": [],
            },
        },
        "comparison": [
            {"aspect": "Overview", "b6": "Two overviews, one per chart.", "b7": "One overview covering both.", "b8": "One overview covering both, with no figures."},
            {"aspect": "Selection and grouping", "b6": "Every data point listed.", "b7": "One paragraph per graphic.", "b8": "One per graphic, plus an explicit link between them."},
            {"aspect": "Quantity language", "b6": "'Increased a lot'.", "b7": "'Very small' increase.", "b8": "'Climbed steadily', 'levelling off', 'growth almost stopped'."},
            {"aspect": "Cohesion", "b6": "'Now I will describe the second chart'.", "b7": "'After 2019', 'In 2024'.", "b8": "'while', 'that electricity', 'that demand', 'After that point'."},
            {"aspect": "Grammar and tense", "b6": "Correct but announced structure.", "b7": "Correct; one evaluative 'only'.", "b8": "Past simple with past perfect to mark the end state."},
        ],
        "takeaway": "Two visuals do not mean two reports and do not double the word count. One overview, and at least one sentence that uses both graphics together.",
        "ua": "Два візуали — це не два звіти і не подвійний обсяг. Одне overview і хоча б одне речення, яке використовує обидва джерела разом.",
    },
]


def build_exercise(spec, index):
    """Turn an authored exercise spec into a schema-valid exercise record."""
    fam = spec["family"]
    meta = MICRO_TYPE_BY_ID[spec["type"]]
    visual = VISUALS_BY_ID[spec["visual"]]
    ex = {
        "id": f"W1X-{FAMILY_CODE[fam]}-{index:02d}",
        "type": meta["interaction"],
        "skill": SKILL,
        "questionFamily": fam,
        "visualFamily": fam,
        "microType": spec["type"],
        "microTypeLabel": meta["label"],
        "microTypeUa": meta["ua"],
        "skillFocus": meta["focus"],
        "mode": meta["mode"],
        "modeLabel": MODE_LABELS[meta["mode"]],
        "difficulty": FAMILY_META[fam]["difficulty"],
        "visualId": visual["id"],
        "prompt": spec["prompt"],
        "explanation": spec["explanation"],
        "errorCategory": spec["errorCategory"],
        "grounding": spec["grounding"],
        "uaSupport": spec["ua"],
        "estimatedMinutes": meta["minutes"],
        "originality": "original",
        "tags": [fam, spec["type"], meta["mode"]],
    }
    if spec.get("allowedNumbers"):
        ex["allowedNumbers"] = spec["allowedNumbers"]
        ex["allowedNumbersReason"] = spec["allowedNumbersReason"]
    if spec.get("deliberateErrorFigures"):
        ex["deliberateErrorFigures"] = spec["deliberateErrorFigures"]
        ex["deliberateErrorReason"] = spec["deliberateErrorReason"]
    if spec.get("extraOps"):
        ex["extraOps"] = spec["extraOps"]
    if meta["interaction"] == "select":
        ex["options"] = spec["options"]
        ex["correctAnswer"] = spec["answer"]
        ex["distractorReasoning"] = spec["distractors"]
    elif meta["interaction"] == "cloze":
        ex["sentence"] = spec["sentence"]
        ex["correctAnswer"] = spec["answer"]
        ex["acceptableAnswers"] = spec["accept"]
    elif meta["interaction"] == "order":
        ex["items"] = spec["items"]
        ex["correctAnswer"] = spec["order"]
    return ex


def build_prompt(spec, index):
    visual = VISUALS_BY_ID[spec["visual"]]
    fam = visual["family"]
    return {
        "id": f"W1P-{FAMILY_CODE[fam]}-{index:02d}",
        "type": "full_prompt",
        "skill": SKILL,
        "questionFamily": fam,
        "visualFamily": fam,
        "difficulty": FAMILY_META[fam]["difficulty"],
        "visualId": visual["id"],
        "mode": spec["mode"],
        "modeLabel": MODE_LABELS[spec["mode"]],
        "prompt": (
            f"{visual['taskStatement']} Summarise the information by selecting and reporting "
            f"the main features, and make comparisons where relevant. Write at least "
            f"{TASK1_WORD_MINIMUM} words."
        ),
        "taskStatement": visual["taskStatement"],
        "estimatedMinutes": TASK1_MINUTES,
        "wordMinimum": TASK1_WORD_MINIMUM,
        "planning": {
            "minutes": 3,
            "steps": PLANNING_STEPS[fam],
            "placeholder": "Timeframe and tense / grouping / the two or three features you will report",
        },
        "checklist": BASE_CHECKLIST + FAMILY_CHECKLIST_EXTRA[fam],
        "targetFeatures": spec["targetFeatures"],
        "modelResponse": spec["modelResponse"],
        "modelNotes": spec["modelNotes"],
        "errorCategory": spec["errorCategoriesWatched"][0],
        "errorCategoriesWatched": spec["errorCategoriesWatched"],
        "explanation": " ".join(spec["modelNotes"]),
        "uaSupport": spec["ua"],
        "scoringNote": SCORING_NOTE,
        "originality": "original",
        "tags": [fam, "full_prompt", spec["mode"]],
    }


def build_band_sets():
    out = []
    for spec in BAND_SETS:
        v = VISUALS_BY_ID[spec["visual"]]
        fam = spec["family"]
        if v["family"] != fam:
            raise SystemExit(f"BUILD FAIL: band set for {fam} points at a {v['family']} visual")
        responses = []
        for lv in BAND_LEVELS:
            r = spec["responses"][lv["id"]]
            responses.append({
                "id": f"W1B-{FAMILY_CODE[fam]}-{lv['id']}",
                "level": lv["level"], "label": lv["label"], "levelUa": lv["ua"],
                "text": r["text"],
                "wordCount": sum(len(p.split()) for p in r["text"]),
                "does": r["does"], "missing": r["missing"],
            })
        out.append({
            "id": f"W1B-{FAMILY_CODE[fam]}-01", "type": "band_comparison", "skill": SKILL,
            "questionFamily": fam, "visualFamily": fam,
            "difficulty": FAMILY_META[fam]["difficulty"], "visualId": v["id"],
            "focus": spec["focus"], "aspects": BAND_ASPECTS, "comparison": spec["comparison"],
            "responses": responses, "takeaway": spec["takeaway"], "uaSupport": spec["ua"],
            "prompt": f"Three responses to the same task, compared: {v['taskStatement']}",
            "explanation": spec["takeaway"], "errorCategory": "missing_overview",
            "estimatedMinutes": 8, "originality": "original",
            "scoringNote": BAND_SCORING_NOTE, "tags": [fam, "band_comparison"],
        })
    return out


def attach_claims(exercises, prompts, bands):
    """Build the canonical claim manifest and refuse to ship if it fails."""
    problems = []

    for e in exercises:
        v = VISUALS_BY_ID[e["visualId"]]
        structural = {_round(n) for n in (e.get("allowedNumbers") or [])}
        extra = list(e.get("extraOps") or [])
        auth = grounded_figures(v, e["grounding"], extra)
        units, times = unit_tokens_of(v), visual_time_labels(v)
        opt_figs = set()
        for o in (e.get("options") or []):
            opt_figs |= figures_in(o)
        texts = [("prompt", e["prompt"]), ("explanation", e["explanation"])]
        if e["type"] == "select":
            texts.append(("correctAnswer", e["correctAnswer"]))
        if e["type"] == "cloze":
            texts.append(("sentence", e["sentence"]))
        if e["type"] == "order":
            texts += [(f"item[{i}]", it["text"]) for i, it in enumerate(e["items"])]
        for label, t in texts:
            # Only an explanation may quote a figure a wrong option offered.
            allowed = auth | (opt_figs if label == "explanation" else set())
            check_text(f"{e['id']}.{label}", v, t, allowed, structural, units, times, problems,
                       e.get("deliberateErrorFigures") or ())
        e["claim"] = {
            "intent": e["skillFocus"],
            "groundingKeys": e["grounding"],
            "datasetFields": sorted({".".join(k.split(".")[1:3]) for k in e["grounding"]}),
            "permittedOperations": sorted({fact_op(k) for k in e["grounding"]} | set(extra)),
            "authorisedFigures": sorted(auth - visual_time_labels(v)),
            "structuralNumbers": sorted(structural),
            "unit": v["unit"], "period": v["timeframe"],
            "timeReferences": sorted(times),
            "acceptedResponses": (e.get("acceptableAnswers") or
                                  ([e["correctAnswer"]] if e["type"] == "select" else e["correctAnswer"])),
            "distractorFaults": e.get("distractorReasoning", {}),
            "deliberateErrorFigures": e.get("deliberateErrorFigures") or [],
            "deliberateErrorReason": e.get("deliberateErrorReason", ""),
        }

    for p in prompts:
        v = VISUALS_BY_ID[p["visualId"]]
        extra = list(p.get("extraOps") or [])
        auth = report_figures(v, extra)
        structural = {_round(n) for n in (p.get("allowedNumbers") or [])}
        units, times = unit_tokens_of(v), visual_time_labels(v)
        for i, par in enumerate(p["modelResponse"]):
            check_text(f"{p['id']}.model[{i}]", v, par, auth, structural, units, times, problems)
        for i, n in enumerate(p["modelNotes"]):
            check_text(f"{p['id']}.note[{i}]", v, n, auth, structural, units, times, problems)
        for i, t in enumerate(p["targetFeatures"]):
            check_text(f"{p['id']}.target[{i}]", v, t, auth, structural, units, times, problems)
        p["claim"] = {
            "intent": "Full report of this visual.",
            "permittedOperations": sorted(ALLOWED_REPORT_OPS | set(extra)),
            "restrictedOperationsAuthorised": sorted(set(extra) & RESTRICTED_OPS),
            "authorisedFigures": sorted(auth - times),
            "structuralNumbers": sorted(structural),
            "unit": v["unit"], "period": v["timeframe"], "timeReferences": sorted(times),
        }

    for b in bands:
        v = VISUALS_BY_ID[b["visualId"]]
        extra = list(b.get("extraOps") or [])
        auth = report_figures(v, extra)
        units, times = unit_tokens_of(v), visual_time_labels(v)
        for r in b["responses"]:
            for i, par in enumerate(r["text"]):
                check_text(f"{b['id']}.{r['level']}[{i}]", v, par, auth, set(), units, times, problems)
        b["claim"] = {
            "intent": "Three reports of the same visual at different quality levels.",
            "permittedOperations": sorted(ALLOWED_REPORT_OPS | set(extra)),
            "authorisedFigures": sorted(auth - times),
            "unit": v["unit"], "period": v["timeframe"], "timeReferences": sorted(times),
        }

    if problems:
        print(f"BUILD FAIL: {len(problems)} canonical-claim violations")
        for pr in problems[:60]:
            print("  ", pr)
        raise SystemExit(1)


def build():
    exercises = []
    for fam in FAMILY_ORDER:
        fam_specs = [e for e in EXERCISES if e["family"] == fam]
        by_type = {e["type"]: e for e in fam_specs}
        for i, tid in enumerate(MICRO_TYPE_IDS, start=1):
            if tid not in by_type:
                raise SystemExit(f"BUILD FAIL: {fam} is missing micro-type {tid}")
            exercises.append(build_exercise(by_type[tid], i))

    prompts = []
    per_family_index = {f: 0 for f in FAMILY_ORDER}
    for spec in PROMPTS:
        fam = VISUALS_BY_ID[spec["visual"]]["family"]
        per_family_index[fam] += 1
        prompts.append(build_prompt(spec, per_family_index[fam]))

    bands = build_band_sets()
    attach_claims(exercises, prompts, bands)

    modules = []
    foundation_ids = [m["id"] for m in FOUNDATION_MODULES]
    for m in FOUNDATION_MODULES:
        modules.append({
            "id": m["id"],
            "title": m["title"],
            "skill": SKILL,
            "subskill": m["subskill"],
            "kind": "foundation",
            "difficulty": m["difficulty"],
            "objectives": m["objectives"],
            "lesson": m["lesson"],
            "workedExamples": m["workedExamples"],
            "exercises": [],
            "masteryCheck": [],
            "prerequisites": [],
            "relatedModules": [],
            "errorCategories": m["errorCategories"],
            "uaSupport": m["uaSupport"],
            "minutes": 10,
        })

    for fam in FAMILY_ORDER:
        meta = FAMILY_META[fam]
        fam_exercises = [e for e in exercises if e["questionFamily"] == fam]
        fam_prompts = [p for p in prompts if p["questionFamily"] == fam]
        fam_visuals = [v["id"] for v in VISUALS if v["family"] == fam]
        mastery_exercise = [e["id"] for e in fam_exercises if e["mode"] == "mastery"]
        timed_prompt = [p["id"] for p in fam_prompts if p["mode"] == "timed"]
        error_cats = []
        for c in meta["commonErrors"]:
            if c["errorId"] not in error_cats:
                error_cats.append(c["errorId"])
        for e in fam_exercises:
            if e["errorCategory"] not in error_cats:
                error_cats.append(e["errorCategory"])
        modules.append({
            "id": f"W1M-{FAMILY_CODE[fam]}",
            "title": meta["title"],
            "skill": SKILL,
            "subskill": fam,
            "kind": "visual_family",
            "difficulty": meta["difficulty"],
            "objectives": [
                meta["whatItTests"],
                f"Report a {meta['title'].lower().rstrip('s')} task with a figure-free overview, grouped body paragraphs and accurate data language.",
            ],
            "lesson": meta["strategy"],
            "strategySteps": meta["strategy"],
            "whatItTests": meta["whatItTests"],
            "howIeltsConstructs": meta["howIeltsConstructs"],
            "trap": meta["trap"],
            "commonErrors": meta["commonErrors"],
            "workedExamples": [meta["workedExample"]],
            "workedExample": meta["workedExample"]["analysis"],
            "languageBank": meta["languageBank"],
            "tenseRule": meta["tenseRule"],
            "uaTransferNote": meta["uaTransferNote"],
            "uaSupport": meta["uaSupport"],
            "exercises": [e["id"] for e in fam_exercises],
            "prompts": [p["id"] for p in fam_prompts],
            "bandComparisons": [b["id"] for b in bands if b["questionFamily"] == fam],
            "visuals": fam_visuals,
            "masteryCheck": mastery_exercise + timed_prompt,
            "prerequisites": foundation_ids,
            "relatedModules": [f"W1M-{FAMILY_CODE[f]}" for f in FAMILY_ORDER if f != fam],
            "errorCategories": error_cats,
            "minutes": sum(e["estimatedMinutes"] for e in fam_exercises) + TASK1_MINUTES,
        })

    visuals = []
    for v in VISUALS:
        record = dict(v)
        record["facts"] = compute_facts(v)
        visuals.append(record)

    family_meta = {}
    for fam in FAMILY_ORDER:
        m = FAMILY_META[fam]
        family_meta[fam] = {
            "title": m["title"],
            "ua": m["ua"],
            "skill": m["skill"],
            "difficulty": m["difficulty"],
            "whatItTests": m["whatItTests"],
            "howIeltsConstructs": m["howIeltsConstructs"],
            "trap": m["trap"],
            "commonErrors": m["commonErrors"],
            "tenseRule": m["tenseRule"],
            "uaTransferNote": m["uaTransferNote"],
            "moduleId": f"W1M-{FAMILY_CODE[fam]}",
        }

    data = {
        "meta": {
            "gate": "G4",
            "skill": SKILL,
            "version": "1.0.0-phase4",
            "familyCount": len(FAMILY_ORDER),
            "visualCount": len(visuals),
            "microExerciseCount": len(exercises),
            "promptCount": len(prompts),
            "moduleCount": len(modules),
            "bandComparisonCount": len(bands),
            "bandResponseCount": sum(len(b["responses"]) for b in bands),
            "workedExampleCount": sum(len(m.get("workedExamples", [])) for m in modules),
            "annotatedModelCount": sum(1 for p in prompts if p.get("modelResponse") and p.get("modelNotes")),
            "foundationModuleCount": len(FOUNDATION_MODULES),
            "microTypeCount": len(MICRO_TYPES),
            "errorCategoryCount": len(ERROR_TAXONOMY),
            "taskMinutes": TASK1_MINUTES,
            "wordMinimum": TASK1_WORD_MINIMUM,
            "benchmarks": {
                "familiesRequired": 7,
                "microExercisesRequired": 60,
                "promptsRequired": 20,
                "bandComparisonsRequired": 7,
            },
            "originality": "All visuals, datasets and text are original to this product.",
            "scoringNote": SCORING_NOTE,
        },
        "familyOrder": FAMILY_ORDER,
        "familyMeta": family_meta,
        "microTypes": MICRO_TYPES,
        "modeLabels": MODE_LABELS,
        "errorTaxonomy": ERROR_TAXONOMY,
        "masteryRules": MASTERY_RULES,
        "modules": modules,
        "visuals": visuals,
        "exercises": exercises,
        "prompts": prompts,
        "bandComparisons": bands,
        "bandLevels": BAND_LEVELS,
        "bandAspects": BAND_ASPECTS,
    }
    return data


def main():
    data = build()
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(f"window.WRITING1_DATA={payload};\n", encoding="utf-8")
    m = data["meta"]
    print("WRITING TASK 1 CURRICULUM BUILD")
    print("==============================")
    print(f"Visual families : {m['familyCount']}")
    print(f"Visuals         : {m['visualCount']}")
    print(f"Micro-exercises : {m['microExerciseCount']} (benchmark {m['benchmarks']['microExercisesRequired']})")
    print(f"Full prompts    : {m['promptCount']} (benchmark {m['benchmarks']['promptsRequired']})")
    print(f"Modules         : {m['moduleCount']} ({m['foundationModuleCount']} foundation)")
    print(f"Band comparisons: {m['bandComparisonCount']} sets, {m['bandResponseCount']} sample responses")
    print(f"Worked examples : {m['workedExampleCount']}")
    print(f"Error categories: {m['errorCategoryCount']}")
    print(f"Written to      : {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
