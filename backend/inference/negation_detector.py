"""negation_detector.py

WHY THIS FILE EXISTS
    Determines whether each symptom mention found by symptom_extractor.py
    is AFFIRMED or NEGATED in the sentence. This is the file that makes
    "no cough" correctly produce a NEGATIVE cough symptom instead of a
    positive one -- one of the explicit correctness requirements of this
    project.

INPUT
    raw_text: str
    mentions: list[SymptomMention]  -- from symptom_extractor.py

OUTPUT
    list[SymptomMention]  -- same mentions, each tagged as
    polarity="affirmed" | "negated" | "uncertain"

HOW IT CONNECTS
    symptom_extractor.py -> THIS FILE -> symptom_normalizer.py

DESIGN NOTE
    Implemented with a NegEx-style rule algorithm: negation trigger terms
    ("no", "denies", "without", "not experiencing") define a scope window
    around a symptom mention. This is a well-known, well-tested clinical
    NLP technique (see: negex, pyConTextNLP) and is far more auditable
    than asking a neural model to "just learn" negation from 1,200 rows.
"""

# Implementation added in Phase 7.
