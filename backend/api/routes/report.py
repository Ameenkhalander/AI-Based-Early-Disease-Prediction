"""report.py -- GET /api/report/{session_id}

WHY: generates and returns the downloadable PDF report for a completed
assessment session (text and/or image results).
INPUT: session_id (path param).
OUTPUT: application/pdf file stream.
CALLS: services.report_service.generate_pdf(), services.storage_service
       (to fetch the full session history to put in the report).
"""

# Implementation added in Phase 18.
