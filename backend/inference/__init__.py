"""Clinical inference engine.

This package contains the ENTIRE decision-making pipeline for the symptom
assessment feature: text -> symptoms -> negation -> normalization ->
emergency check -> prediction -> follow-up questions -> explanation.

Nothing in api/routes/ is allowed to contain this logic directly. Routes
only call functions/classes exposed here. This separation means:
  - the inference engine can be unit-tested without spinning up FastAPI
  - the same engine can be reused by both the /assessment and /voice routes
  - ml/ can import and evaluate these same modules offline
"""
