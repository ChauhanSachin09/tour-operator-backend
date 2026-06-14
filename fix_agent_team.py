"""
Fix Agent Team — Tour Operator Backend
=======================================
Two sub-agents fix the 14 issues found by the code improvement scanner.

Sub-agent 1: Security Fixer
  Issues 1,2,9  — convert JwtUtil to @Component, externalize secrets
  Issues 3,10   — add JwtAuthenticationFilter, remove manual JWT check
  Issue  11     — upgrade jjwt 0.11→0.12 API

Sub-agent 2: API Quality Fixer  (runs AFTER Security Fixer finishes)
  Issues 4,5,6  — input validation, HTTP status codes, Bearer parsing
  Issue  7      — remove throws IOException, wrap with ResponseStatusException
  Issue  8      — SecurityConfig lambda DSL (Spring Security 6)
  Issue  12     — inject ObjectMapper instead of static field
  Issue  14     — add spring-boot-starter-test to pom.xml

All fixed files are written to /mnt/session/outputs/<relative-path>
and downloaded back to the local project tree after the session ends.

Usage
-----
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...

First run (creates agents + environment):
    python fix_agent_team.py

Save the printed IDs, then subsequent runs skip setup:
    export COORDINATOR_ID=agent_...
    export ENVIRONMENT_ID=env_...
    python fix_agent_team.py
"""

import os
import sys
import pathlib
import anthropic

ROOT = pathlib.Path(__file__).parent
JAVA_SRC = ROOT / "src" / "main" / "java" / "com" / "touroperator"
RESOURCES = ROOT / "src" / "main" / "resources"
TEST_SRC  = ROOT / "src" / "test" / "java" / "com" / "touroperator"

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ---------------------------------------------------------------------------
# Files to upload into the session container
# ---------------------------------------------------------------------------

FILES_TO_UPLOAD = {
    "JwtUtil.java":         JAVA_SRC / "util" / "JwtUtil.java",
    "AuthController.java":  JAVA_SRC / "controller" / "AuthController.java",
    "SecurityConfig.java":  JAVA_SRC / "config" / "SecurityConfig.java",
    "ContentController.java": JAVA_SRC / "controller" / "ContentController.java",
    "WelcomeController.java": JAVA_SRC / "controller" / "WelcomeController.java",
    "TourOperatorApplication.java": JAVA_SRC / "TourOperatorApplication.java",
    "pom.xml":              ROOT / "pom.xml",
}

# Where the agents should write their output files inside the container.
# Key = logical name, value = path under /mnt/session/outputs/
OUTPUT_PATHS = {
    # Security Fixer outputs
    "JwtUtil.java":               "util/JwtUtil.java",
    "JwtAuthenticationFilter.java": "filter/JwtAuthenticationFilter.java",
    "application.properties":     "resources/application.properties",
    # API Quality Fixer outputs
    "AuthController.java":        "controller/AuthController.java",
    "ContentController.java":     "controller/ContentController.java",
    "SecurityConfig.java":        "config/SecurityConfig.java",
    "WelcomeController.java":     "controller/WelcomeController.java",
    "pom.xml":                    "pom.xml",
}

# Where each output maps back to on disk
LOCAL_WRITE_PATHS = {
    "util/JwtUtil.java":                JAVA_SRC / "util" / "JwtUtil.java",
    "filter/JwtAuthenticationFilter.java": JAVA_SRC / "filter" / "JwtAuthenticationFilter.java",
    "resources/application.properties": RESOURCES / "application.properties",
    "controller/AuthController.java":   JAVA_SRC / "controller" / "AuthController.java",
    "controller/ContentController.java": JAVA_SRC / "controller" / "ContentController.java",
    "config/SecurityConfig.java":       JAVA_SRC / "config" / "SecurityConfig.java",
    "controller/WelcomeController.java": JAVA_SRC / "controller" / "WelcomeController.java",
    "pom.xml":                          ROOT / "pom.xml",
}

# ---------------------------------------------------------------------------
# Agent system prompts
# ---------------------------------------------------------------------------

SECURITY_FIXER_PROMPT = """
You are a senior Spring Boot / Java security engineer.
Your task: apply security fixes to a Spring Boot 3.3 / Spring Security 6 project.
All source files are mounted read-only at /workspace/.
Write every output file to /mnt/session/outputs/<relative-path> exactly as shown below.

FIXES TO APPLY
==============

[1+2+9] Convert JwtUtil to @Component and externalize secrets
- Read /workspace/util/JwtUtil.java and /workspace/TourOperatorApplication.java for package info.
- Rewrite JwtUtil as a Spring @Component with constructor injection:
    @Component
    public class JwtUtil {
        private final Key key;
        public JwtUtil(@Value("${app.jwt.secret}") String secret) {
            this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        }
        public String generateToken(String username) { ... }
        public boolean validateToken(String token) { ... }
    }
- Write the rewritten class to: /mnt/session/outputs/util/JwtUtil.java

[11] Upgrade jjwt API in JwtUtil from 0.11.x to 0.12.x
- Replace deprecated builder methods:
    setSubject  → subject
    setIssuedAt → issuedAt
    setExpiration → expiration
    parserBuilder().setSigningKey(key).build().parseClaimsJws(token)
    → parser().verifyWith((SecretKey) key).build().parseSignedClaims(token)
- Apply these changes in the same JwtUtil.java output above.

[3+10] Add JwtAuthenticationFilter; remove manual JWT check from ContentController
- Create a new class JwtAuthenticationFilter extends OncePerRequestFilter.
    It must: extract the Authorization header, call jwtUtil.validateToken(),
    build a UsernamePasswordAuthenticationToken and set it on SecurityContextHolder.
    Skip if the request path matches /api/auth/** or /healthcheck.
- Write it to: /mnt/session/outputs/filter/JwtAuthenticationFilter.java
  (package: com.touroperator.filter)
- Read /workspace/controller/ContentController.java.
    Remove lines that manually extract the token and call JwtUtil.validateToken
    (the @RequestHeader("Authorization") param and the if-block that validates it).
    The method signature becomes simply:
        @PostMapping("/update")
        public ResponseEntity<String> updateContent(@RequestBody String newContent)
    Write the modified controller to: /mnt/session/outputs/controller/ContentController.java

[application.properties]
- Create /mnt/session/outputs/resources/application.properties containing:
    # JWT secret — replace with a real random 256-bit value in production
    app.jwt.secret=CHANGE_ME_USE_A_REAL_256BIT_SECRET_IN_PRODUCTION
    # Admin credentials — replace with env vars or a secrets manager in production
    app.admin.username=admin
    app.admin.password=CHANGE_ME_USE_A_BCRYPT_HASH_IN_PRODUCTION

OUTPUT CHECKLIST (create ALL of these):
  /mnt/session/outputs/util/JwtUtil.java
  /mnt/session/outputs/filter/JwtAuthenticationFilter.java
  /mnt/session/outputs/controller/ContentController.java   (manual JWT check removed)
  /mnt/session/outputs/resources/application.properties

Write complete, compilable Java. Include all necessary imports.
Package declarations must match the originals.
""".strip()


QUALITY_FIXER_PROMPT = """
You are a senior Spring Boot / Java engineer focused on API quality and correctness.
Your task: apply code quality fixes to a Spring Boot 3.3 / Spring Security 6 project.
Source files are at /workspace/ (read-only).
The Security Fixer sub-agent has already written a partial ContentController.java to
/mnt/session/outputs/controller/ContentController.java — read THAT file as your
base for ContentController changes, falling back to /workspace/controller/ContentController.java
if the output file doesn't exist yet.

Write every output to /mnt/session/outputs/<relative-path>.

FIXES TO APPLY
==============

[4] Input validation on updateContent (ContentController)
- Before writing, validate the body:
    try { mapper.readTree(newContent); } catch (JsonProcessingException e) {
        return ResponseEntity.badRequest().body("Invalid JSON");
    }
    if (newContent.length() > 1_048_576) {
        return ResponseEntity.status(HttpStatus.PAYLOAD_TOO_LARGE).body("Request body too large");
    }

[5] Fix Bearer token parsing (ContentController — if it still has a token param)
  Replace token.replace("Bearer ", "") with:
    if (token == null || !token.startsWith("Bearer ")) {
        throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Missing or malformed Authorization header");
    }
    String jwt = token.substring(7);
  (Note: the Security Fixer may have already removed the token param entirely.
   If so, skip this fix — do not re-add the token parameter.)

[6] Replace RuntimeException with ResponseStatusException
- AuthController line 20:
    throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid credentials");
- ContentController: if the token-validation block still exists, replace its RuntimeException too.
- Read /workspace/controller/AuthController.java and apply fix [6] to it.
  Write fixed file to: /mnt/session/outputs/controller/AuthController.java
  Also inject @Value("${app.admin.username}") and @Value("${app.admin.password}")
  for the credential comparison (replacing the hardcoded strings).
  Inject JwtUtil via constructor instead of calling static methods:
    private final JwtUtil jwtUtil;
    public AuthController(JwtUtil jwtUtil, ...) { this.jwtUtil = jwtUtil; ... }

[7] Remove throws IOException; wrap I/O in try/catch with ResponseStatusException
- ContentController: wrap all Files.readString / Files.writeString calls.
- WelcomeController: remove the dead `throws IOException` from getHealth().
- Read /workspace/controller/WelcomeController.java, apply fix, write to:
    /mnt/session/outputs/controller/WelcomeController.java

[8] SecurityConfig — update to Spring Security 6 lambda DSL
- Read /workspace/config/SecurityConfig.java.
  Replace .csrf().disable() with .csrf(AbstractHttpConfigurer::disable)
  Replace .httpBasic() with .httpBasic(Customizer.withDefaults())
  Add imports for Customizer and AbstractHttpConfigurer.
  Also add .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
  after injecting JwtAuthenticationFilter via constructor.
- Write to: /mnt/session/outputs/config/SecurityConfig.java

[12] Inject ObjectMapper instead of static field (ContentController)
- Remove the static final ObjectMapper field.
  Add constructor injection:
    private final ObjectMapper mapper;
    public ContentController(ObjectMapper mapper) { this.mapper = mapper; }

[14] Add spring-boot-starter-test to pom.xml
- Read /workspace/pom.xml.
  Add inside <dependencies>:
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
  Also update all three io.jsonwebtoken dependencies from 0.11.5 to 0.12.6.
- Write the full updated pom.xml to: /mnt/session/outputs/pom.xml

OUTPUT CHECKLIST (create ALL of these):
  /mnt/session/outputs/controller/ContentController.java  (validation, IOException handling, ObjectMapper injection)
  /mnt/session/outputs/controller/AuthController.java     (ResponseStatusException, @Value creds, inject JwtUtil)
  /mnt/session/outputs/config/SecurityConfig.java         (lambda DSL, JWT filter wired)
  /mnt/session/outputs/controller/WelcomeController.java  (dead IOException removed)
  /mnt/session/outputs/pom.xml                            (test dep + jjwt 0.12.6)

Write complete, compilable Java. Include all necessary imports.
""".strip()


COORDINATOR_PROMPT = """
You are a code-review coordinator managing an agent team that fixes a Spring Boot backend.
You have two sub-agents available:
  - "Security Fixer"    — handles JWT infrastructure and security hardening
  - "API Quality Fixer" — handles API correctness, error handling, and configuration

Your job:
1. Delegate to Security Fixer FIRST with its task. Wait for it to finish.
2. Then delegate to API Quality Fixer with its task.
   (The Quality Fixer reads the Security Fixer's outputs from /mnt/session/outputs/.)
3. After both finish, summarise all changes made, grouped by file.

Be explicit in what you tell each sub-agent — include their full system-prompt task
description so they have complete context.
""".strip()


# ---------------------------------------------------------------------------
# Helper: upload source files, return {filename: file_id}
# ---------------------------------------------------------------------------

def upload_sources() -> dict[str, str]:
    print("Uploading source files …")
    ids = {}
    for name, path in FILES_TO_UPLOAD.items():
        if not path.exists():
            print(f"  WARN: {path} not found — skipping")
            continue
        with open(path, "rb") as f:
            meta = client.beta.files.upload(
                file=(name, f, "text/plain"),
            )
        ids[name] = meta.id
        print(f"  uploaded {name} → {meta.id}")
    return ids


# ---------------------------------------------------------------------------
# One-time setup
# ---------------------------------------------------------------------------

def setup(file_ids: dict[str, str]) -> tuple[str, str]:
    print("\nCreating sub-agents and coordinator …")

    security_agent = client.beta.agents.create(
        name="Security Fixer",
        model="claude-opus-4-8",
        system=SECURITY_FIXER_PROMPT,
        tools=[{"type": "agent_toolset_20260401"}],
    )
    print(f"  security_agent.id   = {security_agent.id}")

    quality_agent = client.beta.agents.create(
        name="API Quality Fixer",
        model="claude-opus-4-8",
        system=QUALITY_FIXER_PROMPT,
        tools=[{"type": "agent_toolset_20260401"}],
    )
    print(f"  quality_agent.id    = {quality_agent.id}")

    coordinator = client.beta.agents.create(
        name="Fix Coordinator",
        model="claude-opus-4-8",
        system=COORDINATOR_PROMPT,
        tools=[{"type": "agent_toolset_20260401"}],
        multiagent={
            "type": "coordinator",
            "agents": [security_agent.id, quality_agent.id],
        },
    )
    print(f"  coordinator.id      = {coordinator.id}")

    env = client.beta.environments.create(
        name="tour_api_fix_env",
        config={"type": "cloud", "networking": {"type": "unrestricted"}},
    )
    print(f"  environment.id      = {env.id}")

    return coordinator.id, env.id


# ---------------------------------------------------------------------------
# Runtime: start session, stream events, download results
# ---------------------------------------------------------------------------

def run_fixes(coordinator_id: str, environment_id: str, file_ids: dict[str, str]):
    # Build resource list — mount each uploaded file at /workspace/<name>
    resources = [
        {
            "type": "file",
            "file_id": fid,
            "mount_path": f"/workspace/{name}",
        }
        for name, fid in file_ids.items()
    ]

    session = client.beta.sessions.create(
        agent=coordinator_id,
        environment_id=environment_id,
        title="Tour Backend Fix Run",
        resources=resources,
    )
    print(f"\nSession: {session.id}")
    print(f"Live view: https://platform.claude.com/workspaces/default/sessions/{session.id}\n")
    print("=" * 70)

    # Open the stream BEFORE sending the kickoff
    stream = client.beta.sessions.events.stream(session_id=session.id)

    client.beta.sessions.events.send(
        session_id=session.id,
        events=[{
            "type": "user.message",
            "content": [{"type": "text", "text": (
                "Begin the fix run. "
                "Delegate to Security Fixer first, then API Quality Fixer. "
                "All source files are at /workspace/. "
                "Write all fixed files under /mnt/session/outputs/. "
                "When both sub-agents are done, summarise every changed file."
            )}],
        }],
    )

    # Drain events; show agent output and thread activity
    for event in stream:
        if event.type == "agent.message":
            for block in event.content:
                if hasattr(block, "text") and block.text:
                    print(block.text, end="", flush=True)

        elif event.type == "agent.thinking":
            pass  # suppress raw thinking

        elif event.type == "session.thread_created":
            agent_name = getattr(event, "agent_name", "sub-agent")
            print(f"\n\n── Thread created: {agent_name} ──")

        elif event.type == "session.thread_status_running":
            agent_name = getattr(event, "agent_name", "sub-agent")
            print(f"[{agent_name} working …]")

        elif event.type == "session.thread_status_idle":
            agent_name = getattr(event, "agent_name", "sub-agent")
            print(f"[{agent_name} done]")

        elif event.type == "agent.thread_message_sent":
            to_name = getattr(event, "to_agent_name", "sub-agent")
            print(f"\n── Coordinator → {to_name}: delegating ──")

        elif event.type == "agent.thread_message_received":
            from_name = getattr(event, "from_agent_name", "sub-agent")
            print(f"── {from_name} → Coordinator: returned ──")

        elif event.type == "session.status_terminated":
            break

        elif event.type == "session.status_idle":
            stop_type = getattr(event.stop_reason, "type", None)
            if stop_type != "requires_action":
                break

    print("\n" + "=" * 70)

    # Download outputs and write back to the local project tree
    _download_outputs(session.id)


def _download_outputs(session_id: str):
    import time
    print("\nDownloading fixed files …")
    time.sleep(2)  # brief indexing lag before scope_id is queryable

    downloaded = 0
    try:
        for f in client.beta.files.list(
            betas=["managed-agents-2026-04-01"],
            extra_query={"scope_id": session_id},
        ):
            # f.filename is e.g. "controller/ContentController.java"
            fname = f.filename
            local_path = LOCAL_WRITE_PATHS.get(fname)
            if local_path is None:
                print(f"  SKIP (no local mapping): {fname}")
                continue

            resp = client.beta.files.download(f.id)
            content = resp.text if hasattr(resp, "text") else resp.read().decode()

            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_text(content, encoding="utf-8")
            print(f"  wrote {fname} → {local_path.relative_to(ROOT)}")
            downloaded += 1

    except Exception as e:
        print(f"  ERROR during download: {e}")

    if downloaded == 0:
        print("  No output files found. Check the session live-view URL above.")
    else:
        print(f"\n{downloaded} file(s) written. Run `mvn compile` to verify.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    coordinator_id = os.environ.get("COORDINATOR_ID")
    environment_id = os.environ.get("ENVIRONMENT_ID")

    file_ids = upload_sources()
    if not file_ids:
        print("No source files found — check that you're running from the project root.")
        sys.exit(1)

    if not coordinator_id or not environment_id:
        print("\nNo agent/env IDs in env — running one-time setup …")
        coordinator_id, environment_id = setup(file_ids)
        print(
            f"\nSave these so setup is skipped on the next run:\n"
            f"  export COORDINATOR_ID={coordinator_id}\n"
            f"  export ENVIRONMENT_ID={environment_id}\n"
        )

    run_fixes(coordinator_id, environment_id, file_ids)
