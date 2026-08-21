"""symptom_extractor.py

WHY THIS FILE EXISTS
    Converts raw user text ("I have had a high fever for three days and a
    bad headache") into a list of *candidate* symptom mentions found in
    the text, before we know whether each one is affirmed or negated.

INPUT
    raw_text: str  -- what the user typed, or what faster-whisper transcribed.

OUTPUT
    list[SymptomMention]  -- each mention has the matched symptom concept,
    the exact text span, and its position in the sentence (needed by
    negation_detector.py to decide scope).

HOW IT CONNECTS
    text (or speech_service.py output) -> THIS FILE -> negation_detector.py
    -> symptom_normalizer.py -> predictor.py

DESIGN NOTE
    This is implemented as a medical-term matcher (e.g. scispaCy NER +
    a curated symptom synonym dictionary built from the Symptom2Disease
    dataset), NOT a black-box classifier. On ~1,200 training rows, a
    rule/dictionary + NER approach is more reliable and far more
    explainable than trying to fine-tune a sequence-labeling model from
    scratch. This is a defensible interview answer: "why not deep learning
    here?" -> not enough data, and the task doesn't need it.
"""

# Implementation added in Phase 7.
