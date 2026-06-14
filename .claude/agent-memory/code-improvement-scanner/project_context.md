---
name: project-context
description: Core architectural facts about the tour-operator-backend that shape every review suggestion
metadata:
  type: project
---

Spring Boot 3.3.0, Java 17, Maven. Monolithic, file-backed — all content lives in `data/content.json`. No database, no service layer; controllers call utilities directly. No `src/main/resources/application.properties` file exists at all.

Key files: `AuthController`, `ContentController`, `WelcomeController`, `SecurityConfig`, `JwtUtil`, `TourOperatorApplication`.

**Why:** Architectural constraints mean suggestions must stay within the monolith and file-backed model. No service layer additions unless user requests it.

**How to apply:** Never suggest adding a database, service layer, or caching infrastructure. Do suggest externalized config via `application.properties` since that file is simply missing and needs to be created anyway.
