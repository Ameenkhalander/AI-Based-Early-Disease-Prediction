"""Services wrap external/IO-heavy concerns (speech model, image model,
PDF generation, database access) behind a clean interface so routes and
the inference engine never talk to these systems directly."""
