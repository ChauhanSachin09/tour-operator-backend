---
name: recurring-issues
description: Anti-patterns and issues found consistently across this codebase during first full review (2026-06-13)
metadata:
  type: project
---

Patterns found across all Java files in the first full-codebase scan:

1. **Hardcoded secrets** — JWT secret in `JwtUtil.java` line 9; admin credentials in `AuthController.java` line 16. Neither is externalized to `application.properties` or environment variables.
2. **No `application.properties`** — The file does not exist at all; there is no externalized config whatsoever.
3. **Static utility anti-pattern** — `JwtUtil` is a static utility class used directly from controllers. Not Spring-managed, not injectable, not testable in isolation.
4. **Manual JWT validation in controller** — `ContentController.updateContent()` manually extracts and validates the Bearer token instead of delegating to Spring Security.
5. **No JWT filter wired into Spring Security** — `SecurityConfig` configures `.httpBasic()` but there is no `OncePerRequestFilter` for JWT, meaning the `anyRequest().authenticated()` rule is enforced by HTTP Basic, not JWT. The manual check in `ContentController` is the only JWT gate.
6. **Throws `IOException` from controller methods** — `getContent()`, `getDestinationByName()`, `updateContent()`, and even `WelcomeController.getHealth()` declare `throws IOException`. Spring will return a 500 with no client-friendly message.
7. **`RuntimeException` for auth failures** — Both `AuthController` and `ContentController` throw bare `RuntimeException` for invalid credentials/token. Should be `ResponseStatusException(HttpStatus.UNAUTHORIZED)`.
8. **No input validation on `updateContent()`** — Raw string body is written directly to `data/content.json` with no JSON validity check, no size limit, no sanitization.
9. **`token.replace("Bearer ", "")` is fragile** — Does not handle mixed-case "bearer", extra whitespace, or a missing prefix. Should use `startsWith` + `substring`.
10. **Deprecated Spring Security API** — `http.csrf().disable()` and `.httpBasic()` use the deprecated chaining API. Spring Boot 3.x prefers lambda DSL (`csrf(AbstractHttpConfigurer::disable)`, `httpBasic(Customizer.withDefaults())`).
11. **`WelcomeController` declares `throws IOException`** — The method body returns a literal string; it can never throw `IOException`. The declaration is dead noise.
12. **`ObjectMapper` is static final in `ContentController`** — Fine for this architecture, but it is not the Spring-managed `ObjectMapper` bean, so Jackson configuration from `application.properties` is ignored.
13. **`jjwt` version 0.11.5** — Latest is 0.12.x which has an improved API (drops deprecated `setSubject`, `setIssuedAt` etc. in favour of `subject()`, `issuedAt()`).
14. **No `spring-boot-starter-test` in `pom.xml`** — Zero test infrastructure. Should be flagged whenever touching the POM.

**How to apply:** Flag all of the above whenever the relevant file is in scope. Items 1, 5, 7, 8 are Critical. Items 3, 4, 6, 9, 10 are Major.
