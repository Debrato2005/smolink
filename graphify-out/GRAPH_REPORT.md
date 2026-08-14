# Graph Report - smolink  (2026-08-14)

## Corpus Check
- 97 files · ~58,446 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 810 nodes · 1112 edges · 78 communities (67 shown, 11 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 185 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `faf5ef53`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Auth API and Sessions|Auth API and Sessions]]
- [[_COMMUNITY_Auth Repository Tests|Auth Repository Tests]]
- [[_COMMUNITY_Database Models|Database Models]]
- [[_COMMUNITY_Auth Endpoint Tests|Auth Endpoint Tests]]
- [[_COMMUNITY_Authentication Service|Authentication Service]]
- [[_COMMUNITY_Dependency Security Audits|Dependency Security Audits]]
- [[_COMMUNITY_App and Rate Limiting|App and Rate Limiting]]
- [[_COMMUNITY_Graphify Tooling|Graphify Tooling]]
- [[_COMMUNITY_Security Utilities Tests|Security Utilities Tests]]
- [[_COMMUNITY_FastAPI Design Guidance|FastAPI Design Guidance]]
- [[_COMMUNITY_Authentication Design|Authentication Design]]
- [[_COMMUNITY_Python Testing Guidance|Python Testing Guidance]]
- [[_COMMUNITY_Alembic Async Migrations|Alembic Async Migrations]]
- [[_COMMUNITY_Sliding Window Limiting|Sliding Window Limiting]]
- [[_COMMUNITY_Email Verification Delivery|Email Verification Delivery]]
- [[_COMMUNITY_Application Configuration|Application Configuration]]
- [[_COMMUNITY_URL and Analytics Design|URL and Analytics Design]]
- [[_COMMUNITY_Redirect Caching Design|Redirect Caching Design]]
- [[_COMMUNITY_Compose Infrastructure|Compose Infrastructure]]
- [[_COMMUNITY_Layered Monolith Architecture|Layered Monolith Architecture]]
- [[_COMMUNITY_Concurrent Testing|Concurrent Testing]]
- [[_COMMUNITY_Cross Version Testing|Cross Version Testing]]
- [[_COMMUNITY_Backend Project|Backend Project]]
- [[_COMMUNITY_Graph Database Export|Graph Database Export]]
- [[_COMMUNITY_AGENTS Integration|AGENTS Integration]]
- [[_COMMUNITY_HTTP Client Dependency|HTTP Client Dependency]]
- [[_COMMUNITY_SQLModel Dependency|SQLModel Dependency]]
- [[_COMMUNITY_Cluster Refresh|Cluster Refresh]]
- [[_COMMUNITY_Frontend Serving|Frontend Serving]]
- [[_COMMUNITY_Short Code Design|Short Code Design]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]

## God Nodes (most connected - your core abstractions)
1. `SnowflakeGenerator` - 24 edges
2. `Smolink Codebase Walkthrough` - 23 edges
3. `User` - 20 edges
4. `get_settings()` - 17 edges
5. `register_user()` - 16 edges
6. `issue_token_pair()` - 16 edges
7. `FastAPI` - 16 edges
8. `Free-Threaded Python Testing` - 15 edges
9. `rotate_refresh_token()` - 13 edges
10. `Smolink — Engineering Context` - 13 edges

## Surprising Connections (you probably didn't know these)
- `Exact Sliding-Window Log` --semantically_similar_to--> `Strict Redis Rate Limiting`  [INFERRED] [semantically similar]
  docs/superpowers/specs/2026-07-29-sliding-window-rate-limiter-design.md → README.md
- `Layered Backend Architecture` --semantically_similar_to--> `Layered Modular Monolith`  [INFERRED] [semantically similar]
  docs/ENGINEERING_PLAYBOOK.md → README.md
- `test_token_identifier_hash_is_deterministic_and_keyed()` --calls--> `hash_token_identifier()`  [INFERRED]
  backend/tests/test_auth_service.py → backend/app/utils/security.py
- `Async and Concurrency Testing` --semantically_similar_to--> `Async and Sync Path Operations`  [INFERRED] [semantically similar]
  .agents/skills/python-testing/references/async-and-concurrency-testing.md → .agents/skills/fastapi/SKILL.md
- `Local Password Authentication` --implements--> `Optional Authentication`  [EXTRACTED]
  docs/superpowers/specs/2026-08-01-authentication-authorization-design.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI API Conventions** — skills_skill_annotated, skills_skill_response_models, skills_skill_router_configuration, skills_skill_dependency_injection, skills_skill_streaming [EXTRACTED 1.00]
- **Graphify Build Pipeline** — skills_skill_file_detection, skills_skill_structural_extraction, skills_skill_semantic_extraction, skills_skill_graph_building, skills_skill_community_labels, skills_skill_html_export [EXTRACTED 1.00]
- **Async Reliability Testing** — skills_skill_python_testing, references_async_and_concurrency_testing_async_concurrency_testing, references_async_and_concurrency_testing_leak_diagnostics [EXTRACTED 1.00]
- **Authentication Token Lifecycle** — specs_2026_08_01_authentication_authorization_design_local_password_auth, specs_2026_08_01_authentication_authorization_design_refresh_token_rotation, specs_2026_08_01_authentication_authorization_design_email_verification, specs_2026_08_01_authentication_authorization_design_google_oidc_flow [EXTRACTED 1.00]
- **Durable URL Data Model** — specs_2026_07_20_initial_data_model_design_user_model, specs_2026_07_20_initial_data_model_design_url_model, specs_2026_07_20_initial_data_model_design_click_event_model, specs_2026_07_20_initial_data_model_design_database_constraints [EXTRACTED 1.00]
- **Rate Limit Enforcement Flow** — specs_2026_07_29_sliding_window_rate_limiter_design_exact_sliding_window, specs_2026_07_29_sliding_window_rate_limiter_design_redis_sorted_set, specs_2026_07_29_sliding_window_rate_limiter_design_redis_outage_contract, plans_2026_07_29_sliding_window_rate_limiter_implementation_plan [EXTRACTED 1.00]

## Communities (78 total, 11 thin omitted)

### Community 0 - "Auth API and Sessions"
Cohesion: 0.12
Nodes (28): BaseModel, forgot_password(), login(), logout(), me(), refresh(), register(), verify_email_endpoint() (+20 more)

### Community 1 - "Auth Repository Tests"
Cohesion: 0.07
Nodes (25): test_email_verification_token_repository_creates_and_locks_record(), test_refresh_token_repository_creates_and_looks_up_record(), test_revoke_refresh_token_family_revokes_only_that_family(), test_authenticate_user_locks_account_after_five_failed_attempts(), test_authenticate_user_rejects_currently_locked_account(), test_authenticate_user_rejects_invalid_credentials(), test_authenticate_user_rejects_unverified_password_account(), test_authenticate_user_resets_failure_state_after_successful_login() (+17 more)

### Community 2 - "Database Models"
Cohesion: 0.07
Nodes (27): datetime, Base, DeclarativeBase, create_url(), AuthIdentity, ClickEvent, OAuthAuthorizationRequest, Url (+19 more)

### Community 3 - "Auth Endpoint Tests"
Cohesion: 0.12
Nodes (36): MonkeyPatch, TestClient, client(), create_pending_verification(), create_verified_user(), suppress_verification_email(), test_forgot_password_always_returns_202(), test_login_rejects_unverified_password_account() (+28 more)

### Community 4 - "Authentication Service"
Cohesion: 0.08
Nodes (61): AsyncSession, get_settings(), get_session(), get_current_user(), EmailVerificationToken, Exception, User, PasswordResetToken (+53 more)

### Community 5 - "Dependency Security Audits"
Cohesion: 0.12
Nodes (24): Path, _find_workspace_root(), _format_fix_versions(), _ignore_vuln_args(), Security audit tests using pip-audit to detect known vulnerabilities.  This test, Run pip-audit to check for known security vulnerabilities.      Detected vulnera, Verify that pip-audit can run successfully (even if vulnerabilities are found)., Walk up from ``start`` to the nearest ancestor containing ``uv.lock``.      The (+16 more)

### Community 6 - "App and Rate Limiting"
Cohesion: 0.14
Nodes (9): create_app(), RateLimitResult, SlidingWindowRateLimiter, get_redis_client(), limit_auth_write(), limit_guest_creation(), FastAPI, Redis (+1 more)

### Community 7 - "Graphify Tooling"
Cohesion: 0.11
Nodes (19): Folder Watching, URL Ingestion, Wiki Export, Cross-Repository Merge, Post-Commit Graph Hook, Concept Explanation, Graph Traversal, Path Query (+11 more)

### Community 8 - "Security Utilities Tests"
Cohesion: 0.07
Nodes (26): Basic Configuration, Built-in uv Backend, Caching, CI Patterns (GitHub Actions), Common Pitfalls, Dependency resolution across versions, Documentation Links, Interpreter discovery (+18 more)

### Community 9 - "FastAPI Design Guidance"
Cohesion: 0.25
Nodes (9): Dependency Injection, Class Dependencies, Yield Dependencies, No Ellipsis Defaults, No Pydantic RootModels, Response Model Selection, Annotated Declarations, FastAPI Best Practices (+1 more)

### Community 10 - "Authentication Design"
Cohesion: 0.33
Nodes (7): Production Authentication and Authorization, Optional Authentication, Session-Backed JWT Authentication, Email Verification Lifecycle, Google OIDC Authorization-Code Flow, Local Password Authentication, Refresh Token Family Rotation

### Community 11 - "Python Testing Guidance"
Cohesion: 0.07
Nodes (25): Change-Specific Diagnostics, Common Mistakes, Invocation Notice, Overview, Python Testing, Quick Reference, References, Test Doubles (+17 more)

### Community 12 - "Alembic Async Migrations"
Cohesion: 0.40
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection

### Community 13 - "Sliding Window Limiting"
Cohesion: 0.06
Nodes (35): Alembic migration environment, `backend/app/core/config.py`, `backend/app/db/base.py`, `backend/app/db/session.py`, `backend/app/main.py`, `backend/.env`, `backend/.env.example`, `backend/pyproject.toml` (+27 more)

### Community 14 - "Email Verification Delivery"
Cohesion: 0.08
Nodes (26): A. Foundation cleanup — 20 minutes, B. Local infrastructure — 60 minutes, C. Database foundation — 90 minutes, Current verified state, D. Initial data model and migration — 120 minutes, Day 1 — Foundation, persistence, and URL creation, Day 2 — Security, Redis behavior, and complete URL experience, E. Short-code utilities — 90 minutes (+18 more)

### Community 15 - "Application Configuration"
Cohesion: 0.40
Nodes (3): BaseSettings, Settings, test_settings_reads_environment_variables()

### Community 16 - "URL and Analytics Design"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "Redirect Caching Design"
Cohesion: 0.40
Nodes (5): Cache-Aside Redirect Pattern, Redirect Flow, PostgreSQL Source of Truth, Redis Cache and Ephemeral State, Durable Database Constraints

### Community 18 - "Compose Infrastructure"
Cohesion: 0.67
Nodes (3): Local Compose Infrastructure, PostgreSQL Compose Service, Redis Compose Service

### Community 19 - "Layered Monolith Architecture"
Cohesion: 0.67
Nodes (3): Layered Backend Architecture, Layered Modular Monolith, Service Layer Transaction Coordination

### Community 20 - "Concurrent Testing"
Cohesion: 0.08
Nodes (23): Background, C Extension Compatibility, CI Setup, Common Pitfalls, Concurrent Data Structures, Free-Threaded Python Testing, GitHub Actions, Installing Free-Threaded Python (+15 more)

### Community 21 - "Cross Version Testing"
Cohesion: 0.67
Nodes (3): Nox Multi-Python Test Matrix, Behavior-Oriented Tests, Contract-First Testing

### Community 34 - "HTTP Client Dependency"
Cohesion: 0.08
Nodes (24): 10. All application APIs remain versioned under `/api/v1`, 11. Services coordinate multi-record transactions; handlers translate HTTP, 1. Layered modular monolith, not microservices (current), 2. Auth is optional, 3. PostgreSQL is the source of truth; Redis is cache-only for durable data, 4. Short code generation: Snowflake ID + Base62 encoding, 5. No dedicated alias-availability endpoint, 6. Route identifier convention (+16 more)

### Community 41 - "Community 41"
Cohesion: 0.12
Nodes (17): 1. Mission, 2. Agent Workflow, 3. Documentation Order, 4. Development Rules, 5. Working Process, 6. Editing Rules, 7. Decision Framework, 8. Anti-Patterns (+9 more)

### Community 42 - "Community 42"
Cohesion: 0.13
Nodes (15): Async vs Sync *path operations*, Do not use Ellipsis for *path operations* or Pydantic models, Do not use Pydantic RootModels, FastAPI, Including Routers, Other Libraries, Performance, Quick Reference (+7 more)

### Community 43 - "Community 43"
Cohesion: 0.15
Nodes (12): Contract-First Rules, Coverage Expectations, Derived-pair invariants across composition boundaries, Determine Intent and Contracts, Determinism and Flake Control, Multi-Path and Derived-Field Patterns, Multiple write-sites for the same contract, Outcome (+4 more)

### Community 44 - "Community 44"
Cohesion: 0.15
Nodes (12): ClickEvent, Explicit deferrals, Indexes and relationships, Initial data model design, Migration and verification, Model layout, Purpose, Scope (+4 more)

### Community 45 - "Community 45"
Cohesion: 0.15
Nodes (12): API contract, Email and reset flow, Google OAuth2/OpenID Connect flow, Implementation status (2026-08-04), Modules and boundaries, Persistence model, Product decisions, Production authentication and authorization design (+4 more)

### Community 46 - "Community 46"
Cohesion: 0.18
Nodes (10): Async and Reliability, Baseline Commands, Determinism, Fixtures, Mocking and Patching, Parametrization, Pytest Practices, Structure and Naming (+2 more)

### Community 47 - "Community 47"
Cohesion: 0.20
Nodes (10): Engineering Principles, Functional Requirements, High-Level Architecture, Non-Functional Requirements, Objectives, Part 1 — Project Foundation, Problem Statement & Target Users, Project Constraints (+2 more)

### Community 49 - "Community 49"
Cohesion: 0.22
Nodes (9): 0. How the Internet Works, 10. REST API Design, 11. Request Lifecycle, 12. Folder Structure, 13. Layered Architecture (within each module), 14. Dependency Injection, 15. Configuration Management, 9. HTTP Fundamentals (+1 more)

### Community 50 - "Community 50"
Cohesion: 0.22
Nodes (9): 31. URL Shortening, 32. Snowflake IDs, 33. Base62 Encoding, 34. Custom Aliases, 35. Expiring Links, 36. Redirect Flow, 37. QR Code Generation, 38. Click Analytics (+1 more)

### Community 51 - "Community 51"
Cohesion: 0.22
Nodes (9): 53. Git Workflow, 54. Docker, 55. Docker Compose, 56. Environment Variables, 57. NGINX Reverse Proxy, 58. HTTPS, Common Production Problems, Deployment Checklist (+1 more)

### Community 52 - "Community 52"
Cohesion: 0.22
Nodes (5): Dependencies with `yield` and `scope`, Dependency Injection, Including Routers, Path Operations and Routing, Use one HTTP operation per function

### Community 53 - "Community 53"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 54 - "Community 54"
Cohesion: 0.29
Nodes (7): Build, Test, and Development Commands, Coding Style & Naming Conventions, Commit & Pull Request Guidelines, Project Structure & Module Organization, Repository Guidelines, Skills and Graphify, Testing Guidelines

### Community 55 - "Community 55"
Cohesion: 0.29
Nodes (6): Lifecycle Scenarios to Test, Outcome, Reliability and Lifecycle Testing, Reliability Scenarios to Test, Review Gate, Test Layer Guidance

### Community 56 - "Community 56"
Cohesion: 0.29
Nodes (6): Algorithm, Decision, Interface and verification, Policies and failure behavior, Scope, Sliding-window rate limiter design

### Community 57 - "Community 57"
Cohesion: 0.33
Nodes (6): Agent Skills and Graphify, Available skills, Build or refresh the graph, Generated files, Graphify workflow, Query the graph first

### Community 58 - "Community 58"
Cohesion: 0.33
Nodes (6): 16. Database Design, 17. SQLAlchemy Models, 18. Pydantic Schemas, 19. Repository Pattern, 20. Database Migrations (Alembic), Part 3 — Data Layer

### Community 59 - "Community 59"
Cohesion: 0.33
Nodes (6): 21. Service Layer, 22. Utility Layer, 23. Validation Strategy — defense in depth, never just one layer, 24. Error Handling, 25. Logging, Part 4 — Business Logic

### Community 60 - "Community 60"
Cohesion: 0.33
Nodes (6): 26. Route Organization, 27. API Endpoints, 28. Authentication & Authorization, 29. File Uploads *(future)*, 30. API Versioning, Part 5 — API Layer

### Community 61 - "Community 61"
Cohesion: 0.33
Nodes (6): 39. Redis Caching — Cache-Aside Pattern, 40. Background Tasks, 41. Rate Limiting, 42. Async Programming, 43. Performance Optimization — measure before optimizing, Part 7 — Performance & Scalability

### Community 62 - "Community 62"
Cohesion: 0.33
Nodes (6): 44. Frontend Project Structure, 45. Frontend ↔ Backend Communication, 46. Authentication Flow, 47. Frontend Error Handling, 48. State Management, Part 8 — Frontend Architecture & Integration

### Community 63 - "Community 63"
Cohesion: 0.33
Nodes (6): 49. Unit Testing, 50. Integration Testing, 51. API Testing, 52. Debugging Strategy, Part 9 — Quality Assurance & Testing, Testing Pyramid

### Community 64 - "Community 64"
Cohesion: 0.33
Nodes (5): Global Constraints, Sliding-window rate limiter Implementation Plan, Task 1: Sliding-window Redis primitive, Task 2: Guest-creation FastAPI dependency, Task 3: Redis outage contract and documentation

### Community 65 - "Community 65"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 66 - "Community 66"
Cohesion: 0.40
Nodes (4): Documentation and agent tooling, Parts 11–14 — Planned (content pending), Smolink Engineering Playbook, Table of Contents

### Community 67 - "Community 67"
Cohesion: 0.40
Nodes (4): Server-Sent Events (SSE), Stream bytes, Stream JSON Lines, Streaming

### Community 68 - "Community 68"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 69 - "Community 69"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 70 - "Community 70"
Cohesion: 0.50
Nodes (3): Do not use Ellipsis, Do not use Pydantic RootModels, Pydantic

### Community 71 - "Community 71"
Cohesion: 0.50
Nodes (3): Responses, Return Type or Response Model, When to use `response_model`

### Community 72 - "Community 72"
Cohesion: 0.50
Nodes (4): Byte Streaming, JSON Lines Streaming, Server-Sent Events, Streaming Responses

### Community 73 - "Community 73"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 75 - "Community 75"
Cohesion: 0.67
Nodes (3): Router-Level Configuration, Single Operation Functions, Router Configuration

## Knowledge Gaps
- **362 isolated node(s):** `backend`, `Quick Reference`, `Use the `fastapi` CLI`, `Use `Annotated``, `Do not use Ellipsis for *path operations* or Pydantic models` (+357 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Smolink Codebase Walkthrough` connect `Sliding Window Limiting` to `Community 48`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `Smolink Backend Build Checklist` connect `Email Verification Delivery` to `Community 48`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Why does `create_short_url()` connect `Database Models` to `Authentication Service`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `SnowflakeGenerator` (e.g. with `AccountLockedError` and `EmailTakenError`) actually correct?**
  _`SnowflakeGenerator` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Security audit tests using pip-audit to detect known vulnerabilities.  This test`, `Walk up from ``start`` to the nearest ancestor containing ``uv.lock``.      The`, `Return True when ``uv audit`` can run for this project (uv installed and a lockf` to the rest of the system?**
  _384 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth API and Sessions` be split into smaller, more focused modules?**
  _Cohesion score 0.11742424242424243 - nodes in this community are weakly interconnected._
- **Should `Auth Repository Tests` be split into smaller, more focused modules?**
  _Cohesion score 0.06829268292682927 - nodes in this community are weakly interconnected._