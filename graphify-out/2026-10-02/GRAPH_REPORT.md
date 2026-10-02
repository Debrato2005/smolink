# Graph Report - smolink  (2026-10-02)

## Corpus Check
- 103 files · ~50,626 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 5, .example 1, .ini 1)

## Summary
- 989 nodes · 1988 edges · 79 communities (63 shown, 16 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 127 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `48c23468`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- auth_service.py
- get_settings
- test_models.py
- test_auth.py
- test_security.py
- test_pypi_security_audit.py
- FastAPI
- Graph Building and Analysis
- Multi-Python Version Testing
- Dependency Injection
- Local Password Authentication
- Python Testing
- pytest
- Smolink Codebase Walkthrough
- Smolink Backend Build Checklist
- Settings
- What You Must Do When Invoked
- Cache-Aside Redirect Pattern
- Local Compose Infrastructure
- Layered Modular Monolith
- Deterministic Testing
- Contract-First Testing
- test_email_service.py
- Free-Threaded Python Testing
- test_url_creation.py
- urls.py
- time
- dependencies/rate_limit.py
- sqlalchemy_ext_asyncio
- Async and Concurrency Testing
- Other Tools
- backend
- Graph Database Export
- AGENTS.md Integration
- Smolink — Engineering Context
- SQLModel
- Cluster-Only Refresh
- Frontend Serving
- Snowflake Base62 Short Codes
- extraction-spec.md
- Smolink Agent Guide
- FastAPI
- Testing Strategy
- Initial data model design
- Production authentication and authorization design
- Pytest Practices
- Part 1 — Project Foundation
- ENGINEERING_PLAYBOOK.md
- Part 2 — Backend Fundamentals
- Part 6 — Core Smolink Features
- Part 10 — DevOps & Deployment
- Path Operations and Routing
- graphify reference: extra exports and benchmark
- Repository Guidelines
- Reliability and Lifecycle Testing
- Sliding-window rate limiter design
- Agent skills and Graphify
- Part 3 — Data Layer
- Part 4 — Business Logic
- Part 5 — API Layer
- Part 7 — Performance & Scalability
- Part 8 — Frontend Architecture & Integration
- Part 9 — Quality Assurance & Testing
- Global Constraints
- graphify reference: query, path, explain
- Smolink Engineering Playbook
- Streaming
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native AGENTS.md integration
- fastapi/SKILL.md
- FastAPI Best Practices
- graphify reference: incremental update and cluster-only
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 100 edges
2. `User` - 69 edges
3. `SnowflakeGenerator` - 47 edges
4. `hash_password()` - 30 edges
5. `register_user()` - 24 edges
6. `Smolink Codebase Walkthrough` - 23 edges
7. `EmailVerificationToken` - 22 edges
8. `authenticate_user()` - 21 edges
9. `create_short_url()` - 21 edges
10. `Url` - 20 edges

## Surprising Connections (you probably didn't know these)
- `H. Production authentication and authorization — in progress` --references--> `get_optional_current_user()`  [INFERRED]
  docs/backend-build-checklist.md → backend/app/api/v1/dependencies/auth.py
- `Setup` --references--> `Settings`  [INFERRED]
  docs/development.md → backend/app/core/config.py
- `Troubleshooting` --references--> `Settings`  [INFERRED]
  docs/development.md → backend/app/core/config.py
- `Progress log` --references--> `get_session()`  [INFERRED]
  docs/backend-build-checklist.md → backend/app/db/session.py
- `D. Initial data model and migration — 120 minutes` --references--> `ClickEvent`  [INFERRED]
  docs/backend-build-checklist.md → backend/app/models/click_event.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Build Pipeline** — skills_skill_file_detection, skills_skill_structural_extraction, skills_skill_semantic_extraction, skills_skill_graph_building, skills_skill_community_labels, skills_skill_html_export [EXTRACTED 1.00]
- **Authentication Token Lifecycle** — docs_superpowers_specs_2026_08_01_authentication_authorization_design_local_password_auth, docs_superpowers_specs_2026_08_01_authentication_authorization_design_refresh_token_rotation, docs_superpowers_specs_2026_08_01_authentication_authorization_design_email_verification, docs_superpowers_specs_2026_08_01_authentication_authorization_design_google_oidc_flow [EXTRACTED 1.00]
- **Durable URL Data Model** — docs_superpowers_specs_2026_07_20_initial_data_model_design_user_model, docs_superpowers_specs_2026_07_20_initial_data_model_design_url_model, docs_superpowers_specs_2026_07_20_initial_data_model_design_click_event_model, docs_superpowers_specs_2026_07_20_initial_data_model_design_database_constraints [EXTRACTED 1.00]
- **Rate Limit Enforcement Flow** — docs_superpowers_specs_2026_07_29_sliding_window_rate_limiter_design_exact_sliding_window, docs_superpowers_specs_2026_07_29_sliding_window_rate_limiter_design_redis_sorted_set, docs_superpowers_specs_2026_07_29_sliding_window_rate_limiter_design_redis_outage_contract, docs_superpowers_plans_2026_07_29_sliding_window_rate_limiter_implementation_plan [EXTRACTED 1.00]

## Communities (79 total, 16 thin omitted)

### Community 0 - "auth_service.py"
Cohesion: 0.08
Nodes (75): app_schemas_auth, app_services_auth_service, app_utils_snowflake, forgot_password(), login(), logout(), me(), AsyncSession (+67 more)

### Community 1 - "get_settings"
Cohesion: 0.10
Nodes (59): create_url(), AsyncSession, JSONResponse, post, get_settings(), User, authenticate_user(), register_user() (+51 more)

### Community 2 - "test_models.py"
Cohesion: 0.07
Nodes (47): alembic, app_db, app_db_base, app_repositories_auth_repository, app_repositories_url_repository, asyncio, do_run_migrations(), run_async_migrations() (+39 more)

### Community 3 - "test_auth.py"
Cohesion: 0.08
Nodes (44): create_refresh_token(), client(), clear_auth_rate_limit(), override_get_redis_client(), create_pending_password_reset(), create_pending_verification(), create_verified_user(), datetime (+36 more)

### Community 4 - "test_security.py"
Cohesion: 0.10
Nodes (20): app_utils_oidc, app_utils_security, argon2, argon2_exceptions, create_pkce_verifier(), create_access_token(), decode_access_token(), UUID (+12 more)

### Community 5 - "test_pypi_security_audit.py"
Cohesion: 0.09
Nodes (31): _find_workspace_root(), _format_fix_versions(), _ignore_vuln_args(), Path, Security audit tests using pip-audit to detect known vulnerabilities. This test…, Run pip-audit to check for known security vulnerabilities. Detected…, Verify that pip-audit can run successfully (even if vulnerabilities are found).…, Walk up from ``start`` to the nearest ancestor containing ``uv.lock``. The… (+23 more)

### Community 6 - "FastAPI"
Cohesion: 0.22
Nodes (6): app_api_v1_endpoints_auth, app_api_v1_endpoints_urls, create_app(), A. Foundation cleanup — 20 minutes, FastAPI, fastapi_testclient

### Community 7 - "Graph Building and Analysis"
Cohesion: 0.11
Nodes (19): Folder Watching, URL Ingestion, Wiki Export, Cross-Repository Merge, Post-Commit Graph Hook, Concept Explanation, Graph Traversal, Path Query (+11 more)

### Community 8 - "Multi-Python Version Testing"
Cohesion: 0.07
Nodes (26): Basic Configuration, Built-in uv Backend, Caching, CI Patterns (GitHub Actions), Common Pitfalls, Dependency resolution across versions, Documentation Links, Interpreter discovery (+18 more)

### Community 9 - "Dependency Injection"
Cohesion: 0.22
Nodes (8): Yield Dependencies, No Ellipsis Defaults, No Pydantic RootModels, Dependency Injection, Class Dependencies, Dependencies with `yield` and `scope`, Dependency Injection, Annotated Declarations

### Community 10 - "Local Password Authentication"
Cohesion: 0.33
Nodes (7): Production Authentication and Authorization, Email Verification Lifecycle, Google OIDC Authorization-Code Flow, Local Password Authentication, Refresh Token Family Rotation, Optional Authentication, Session-Backed JWT Authentication

### Community 11 - "Python Testing"
Cohesion: 0.18
Nodes (10): Change-Specific Diagnostics, Common Mistakes, Invocation Notice, Overview, Python Testing, Quick Reference, References, Test Doubles (+2 more)

### Community 12 - "pytest"
Cohesion: 0.10
Nodes (23): app_schemas_url, app_utils_aliases, app_utils_base62, CreateUrlRequest, CreateUrlResponse, BaseModel, InvalidAliasError, normalize_alias() (+15 more)

### Community 13 - "Smolink Codebase Walkthrough"
Cohesion: 0.06
Nodes (35): Alembic migration environment, `backend/app/core/config.py`, `backend/app/db/base.py`, `backend/app/db/session.py`, `backend/app/main.py`, `backend/.env`, `backend/.env.example`, `backend/pyproject.toml` (+27 more)

### Community 14 - "Smolink Backend Build Checklist"
Cohesion: 0.08
Nodes (25): B. Local infrastructure — 60 minutes, C. Database foundation — 90 minutes, Current verified state, D. Initial data model and migration — 120 minutes, Day 1 — Foundation, persistence, and URL creation, Day 2 — Security, Redis behavior, and complete URL experience, E. Short-code utilities — 90 minutes, F. URL creation vertical slice — 150 minutes (+17 more)

### Community 15 - "Settings"
Cohesion: 0.18
Nodes (11): Settings, test_settings_reads_environment_variables(), BaseSettings, Local development, New migrations, Prerequisites, Setup, Tests (+3 more)

### Community 16 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native AGENTS.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 17 - "Cache-Aside Redirect Pattern"
Cohesion: 0.40
Nodes (5): Cache-Aside Redirect Pattern, Redirect Flow, Durable Database Constraints, PostgreSQL Source of Truth, Redis Cache and Ephemeral State

### Community 18 - "Local Compose Infrastructure"
Cohesion: 0.67
Nodes (3): Local Compose Infrastructure, PostgreSQL Compose Service, Redis Compose Service

### Community 19 - "Layered Modular Monolith"
Cohesion: 0.67
Nodes (3): Layered Backend Architecture, Layered Modular Monolith, Service Layer Transaction Coordination

### Community 21 - "Contract-First Testing"
Cohesion: 0.67
Nodes (3): Nox Multi-Python Test Matrix, Behavior-Oriented Tests, Contract-First Testing

### Community 22 - "test_email_service.py"
Cohesion: 0.11
Nodes (12): app_services_email_service, send_password_reset_email(), send_verification_email(), fake_email_settings(), fixture, MonkeyPatch, test_send_password_reset_email_uses_fragment_token(), test_send_verification_email_hides_provider_failure() (+4 more)

### Community 23 - "Free-Threaded Python Testing"
Cohesion: 0.09
Nodes (21): Background, C Extension Compatibility, CI Setup, Common Pitfalls, Concurrent Data Structures, Free-Threaded Python Testing, GitHub Actions, Installing Free-Threaded Python (+13 more)

### Community 24 - "test_url_creation.py"
Cohesion: 0.15
Nodes (17): client(), override_get_redis_client(), fixture, MonkeyPatch, TestClient, seed_verified_user(), test_authenticated_creation_uses_30_per_user_limit(), clear_limits() (+9 more)

### Community 25 - "urls.py"
Cohesion: 0.16
Nodes (15): app_core_config, app_db_session, app_repositories_user_repository, app_services_url_service, get_current_user(), get_optional_current_user(), AsyncSession, get_session() (+7 more)

### Community 26 - "time"
Cohesion: 0.17
Nodes (10): Redis, RateLimitResult, SlidingWindowRateLimiter, test_sliding_window_enforces_limit_prunes_and_keeps_keys_separate(), check(), dataclasses, math, threading (+2 more)

### Community 27 - "dependencies/rate_limit.py"
Cohesion: 0.24
Nodes (9): app_core_rate_limit, app_core_redis, limit_auth_write(), limit_url_creation(), Redis, get_redis_client(), Redis, redis_asyncio (+1 more)

### Community 28 - "sqlalchemy_ext_asyncio"
Cohesion: 0.44
Nodes (7): create_user(), get_user_by_email(), get_user_by_id(), AsyncSession, test_create_and_find_user_by_email(), check(), sqlalchemy_ext_asyncio

### Community 29 - "Async and Concurrency Testing"
Cohesion: 0.25
Nodes (7): Async and Concurrency Testing, Leak Diagnostics, Outcome, Practical Rules, Test Focus Areas, Validation Signals, When to Apply

### Community 30 - "Other Tools"
Cohesion: 0.25
Nodes (8): Asyncer, HTTPX, Other Tools, Ruff, SQLModel for SQL databases, ty, uv, Async and Sync Path Operations

### Community 34 - "Smolink — Engineering Context"
Cohesion: 0.08
Nodes (24): 10. All application APIs remain versioned under `/api/v1`, 11. Services coordinate multi-record transactions; handlers translate HTTP, 1. Layered modular monolith, not microservices (current), 2. Auth is optional, 3. PostgreSQL is the source of truth; Redis is cache-only for durable data, 4. Short code generation: Snowflake ID + Base62 encoding, 5. No dedicated alias-availability endpoint, 6. Route identifier convention (+16 more)

### Community 41 - "Smolink Agent Guide"
Cohesion: 0.22
Nodes (9): Collaboration and authorization, Decisions and completion, Development boundaries, Documentation maintenance, Documentation order, Mission, Skills and writing, Smolink Agent Guide (+1 more)

### Community 42 - "FastAPI"
Cohesion: 0.13
Nodes (15): Async vs Sync *path operations*, Do not use Ellipsis for *path operations* or Pydantic models, Do not use Pydantic RootModels, FastAPI, Including Routers, Other Libraries, Performance, Quick Reference (+7 more)

### Community 43 - "Testing Strategy"
Cohesion: 0.15
Nodes (12): Contract-First Rules, Coverage Expectations, Derived-pair invariants across composition boundaries, Determine Intent and Contracts, Determinism and Flake Control, Multi-Path and Derived-Field Patterns, Multiple write-sites for the same contract, Outcome (+4 more)

### Community 44 - "Initial data model design"
Cohesion: 0.15
Nodes (12): ClickEvent, Explicit deferrals, Indexes and relationships, Initial data model design, Migration and verification, Model layout, Purpose, Scope (+4 more)

### Community 45 - "Production authentication and authorization design"
Cohesion: 0.15
Nodes (12): API contract, Email and reset flow, Google OAuth2/OpenID Connect flow, Implementation status (2026-08-04), Modules and boundaries, Persistence model, Product decisions, Production authentication and authorization design (+4 more)

### Community 46 - "Pytest Practices"
Cohesion: 0.18
Nodes (10): Async and Reliability, Baseline Commands, Determinism, Fixtures, Mocking and Patching, Parametrization, Pytest Practices, Structure and Naming (+2 more)

### Community 47 - "Part 1 — Project Foundation"
Cohesion: 0.20
Nodes (10): Engineering Principles, Functional Requirements, High-Level Architecture, Non-Functional Requirements, Objectives, Part 1 — Project Foundation, Problem Statement & Target Users, Project Constraints (+2 more)

### Community 48 - "ENGINEERING_PLAYBOOK.md"
Cohesion: 0.35
Nodes (4): Graphify, Project skills, Technical writing, Parts 11–14 — Planned (content pending)

### Community 49 - "Part 2 — Backend Fundamentals"
Cohesion: 0.22
Nodes (9): 0. How the Internet Works, 10. REST API Design, 11. Request Lifecycle, 12. Folder Structure, 13. Layered Architecture (within each module), 14. Dependency Injection, 15. Configuration Management, 9. HTTP Fundamentals (+1 more)

### Community 50 - "Part 6 — Core Smolink Features"
Cohesion: 0.22
Nodes (9): 31. URL Shortening, 32. Snowflake IDs, 33. Base62 Encoding, 34. Custom Aliases, 35. Expiring Links, 36. Redirect Flow, 37. QR Code Generation, 38. Click Analytics (+1 more)

### Community 51 - "Part 10 — DevOps & Deployment"
Cohesion: 0.22
Nodes (9): 53. Git Workflow, 54. Docker, 55. Docker Compose, 56. Environment Variables, 57. NGINX Reverse Proxy, 58. HTTPS, Common Production Problems, Deployment Checklist (+1 more)

### Community 52 - "Path Operations and Routing"
Cohesion: 0.50
Nodes (3): Including Routers, Path Operations and Routing, Use one HTTP operation per function

### Community 53 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 54 - "Repository Guidelines"
Cohesion: 0.29
Nodes (7): Coding style and names, Commits and pull requests, Development commands, Project structure and modules, Repository Guidelines, Skills and Graphify, Testing rules

### Community 55 - "Reliability and Lifecycle Testing"
Cohesion: 0.29
Nodes (6): Lifecycle Scenarios to Test, Outcome, Reliability and Lifecycle Testing, Reliability Scenarios to Test, Review Gate, Test Layer Guidance

### Community 56 - "Sliding-window rate limiter design"
Cohesion: 0.29
Nodes (6): Algorithm, Decision, Interface and verification, Policies and failure behavior, Scope, Sliding-window rate limiter design

### Community 57 - "Agent skills and Graphify"
Cohesion: 0.33
Nodes (6): Agent skills and Graphify, Generated and historical material, Graphify, Query an existing graph, Refresh, Skills

### Community 58 - "Part 3 — Data Layer"
Cohesion: 0.33
Nodes (6): 16. Database Design, 17. SQLAlchemy Models, 18. Pydantic Schemas, 19. Repository Pattern, 20. Database Migrations (Alembic), Part 3 — Data Layer

### Community 59 - "Part 4 — Business Logic"
Cohesion: 0.33
Nodes (6): 21. Service Layer, 22. Utility Layer, 23. Validation Strategy — defense in depth, never just one layer, 24. Error Handling, 25. Logging, Part 4 — Business Logic

### Community 60 - "Part 5 — API Layer"
Cohesion: 0.33
Nodes (6): 26. Route Organization, 27. API Endpoints, 28. Authentication & Authorization, 29. File Uploads *(future)*, 30. API Versioning, Part 5 — API Layer

### Community 61 - "Part 7 — Performance & Scalability"
Cohesion: 0.33
Nodes (6): 39. Redis Caching — Cache-Aside Pattern, 40. Background Tasks, 41. Rate Limiting, 42. Async Programming, 43. Performance Optimization — measure before optimizing, Part 7 — Performance & Scalability

### Community 62 - "Part 8 — Frontend Architecture & Integration"
Cohesion: 0.33
Nodes (6): 44. Frontend Project Structure, 45. Frontend ↔ Backend Communication, 46. Authentication Flow, 47. Frontend Error Handling, 48. State Management, Part 8 — Frontend Architecture & Integration

### Community 63 - "Part 9 — Quality Assurance & Testing"
Cohesion: 0.33
Nodes (6): 49. Unit Testing, 50. Integration Testing, 51. API Testing, 52. Debugging Strategy, Part 9 — Quality Assurance & Testing, Testing Pyramid

### Community 64 - "Global Constraints"
Cohesion: 0.33
Nodes (5): Global Constraints, Sliding-window rate limiter Implementation Plan, Task 1: Sliding-window Redis primitive, Task 2: Guest-creation FastAPI dependency, Task 3: Redis outage contract and documentation

### Community 65 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 66 - "Smolink Engineering Playbook"
Cohesion: 0.67
Nodes (3): Documentation and agent tooling, Smolink Engineering Playbook, Table of Contents

### Community 67 - "Streaming"
Cohesion: 0.40
Nodes (4): Server-Sent Events (SSE), Stream bytes, Stream JSON Lines, Streaming

### Community 68 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 69 - "graphify reference: commit hook and native AGENTS.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native AGENTS.md integration, graphify reference: commit hook and native AGENTS.md integration

### Community 70 - "fastapi/SKILL.md"
Cohesion: 0.20
Nodes (6): Do not use Ellipsis, Do not use Pydantic RootModels, Pydantic, Responses, Return Type or Response Model, When to use `response_model`

### Community 72 - "FastAPI Best Practices"
Cohesion: 0.20
Nodes (10): Router-Level Configuration, Single Operation Functions, Response Model Selection, Byte Streaming, JSON Lines Streaming, Server-Sent Events, FastAPI Best Practices, Response Models (+2 more)

### Community 73 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

## Knowledge Gaps
- **358 isolated node(s):** `backend`, `graphify reference: extraction subagent prompt`, `Outcome`, `When to Apply`, `Test Focus Areas` (+353 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 476 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `get_settings` to `auth_service.py`, `test_models.py`, `test_auth.py`, `Smolink Backend Build Checklist`, `test_url_creation.py`, `urls.py`, `dependencies/rate_limit.py`, `sqlalchemy_ext_asyncio`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `Smolink Backend Build Checklist` connect `Smolink Backend Build Checklist` to `ENGINEERING_PLAYBOOK.md`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Why does `Technical writing` connect `test_models.py` to `Agent skills and Graphify`, `get_settings`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `User` (e.g. with `get_current_user()` and `get_optional_current_user()`) actually correct?**
  _`User` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SnowflakeGenerator` (e.g. with `issue_token_pair()` and `register_user()`) actually correct?**
  _`SnowflakeGenerator` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backend`, `graphify reference: extraction subagent prompt`, `Outcome` to the rest of the system?**
  _358 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `auth_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07626582278481013 - nodes in this community are weakly interconnected._