# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Spring Boot 3.3.0 REST API (Java 17, Maven) for managing tour operator content with JWT-based admin authentication.

## Commands

```bash
# Run the application (serves on port 8080)
mvn spring-boot:run

# Build executable JAR
mvn clean package

# Run tests
mvn test

# Compile only
mvn compile
```

## Architecture

**Monolithic, file-backed, no database.** Content is stored in `data/content.json` and served/updated via REST endpoints.

### Layers

- `controller/` — REST endpoints (no service layer; controllers call utilities directly)
- `config/SecurityConfig.java` — Spring Security setup; CSRF disabled, HTTP Basic + JWT filter
- `util/JwtUtil.java` — HMAC-SHA JWT generation and validation (1-hour expiration)
- `data/content.json` — runtime content store (read/written by `ContentController`)

### API surface

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/healthcheck` | none | Health probe |
| POST | `/api/auth/login` | none | Returns JWT; credentials hardcoded (`admin`/`admin123`) |
| GET | `/api/content` | none | Returns `data/content.json` |
| POST | `/api/content/update` | Bearer JWT | Overwrites `data/content.json` |

### Security model

Public routes are `/api/auth/**` and `/healthcheck`; everything else requires a valid JWT as a `Bearer` token. The JWT secret and admin credentials are currently hardcoded in `JwtUtil.java` and `AuthController.java` — not production-ready.

### No test directory

There are no existing tests. `mvn test` compiles but finds nothing to run.
