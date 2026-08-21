One test file per inference/ module is planned:
  test_symptom_extractor.py, test_negation_detector.py,
  test_symptom_normalizer.py, test_emergency_detector.py,
  test_question_engine.py, test_predictor.py, plus API tests
  (test_routes_assessment.py etc.) and image/report tests.
The canonical negation example from the brief:
  input: "I have fever and headache but no cough."
  expected positive: {fever, headache}; expected negative: {cough}
will be the first test written in Phase 7, alongside the feature itself
(test-driven, not bolted on afterward).
