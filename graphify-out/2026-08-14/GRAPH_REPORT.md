# Graph Report - /home/debrato/Projects/smolink  (2026-08-14)

## Corpus Check
- 97 files · ~57,220 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 380 nodes · 670 edges · 41 communities (33 shown, 8 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 171 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

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

## God Nodes (most connected - your core abstractions)
1. `SnowflakeGenerator` - 22 edges
2. `User` - 19 edges
3. `register_user()` - 16 edges
4. `issue_token_pair()` - 16 edges
5. `get_settings()` - 15 edges
6. `rotate_refresh_token()` - 13 edges
7. `create_short_url()` - 11 edges
8. `InvalidRefreshJwtError` - 10 edges
9. `create_verified_user()` - 10 edges
10. `register()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Exact Sliding-Window Log` --semantically_similar_to--> `Strict Redis Rate Limiting`  [INFERRED] [semantically similar]
  docs/superpowers/specs/2026-07-29-sliding-window-rate-limiter-design.md → README.md
- `Layered Backend Architecture` --semantically_similar_to--> `Layered Modular Monolith`  [INFERRED] [semantically similar]
  docs/ENGINEERING_PLAYBOOK.md → README.md
- `test_token_identifier_hash_is_deterministic_and_keyed()` --calls--> `hash_token_identifier()`  [INFERRED]
  backend/tests/test_auth_service.py → backend/app/utils/security.py
- `Local Password Authentication` --implements--> `Optional Authentication`  [EXTRACTED]
  docs/superpowers/specs/2026-08-01-authentication-authorization-design.md → README.md
- `get_current_user()` --calls--> `decode_access_token()`  [INFERRED]
  backend/app/api/v1/dependencies/auth.py → backend/app/utils/security.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FastAPI API Conventions** — skills_skill_annotated, skills_skill_response_models, skills_skill_router_configuration, skills_skill_dependency_injection, skills_skill_streaming [EXTRACTED 1.00]
- **Graphify Build Pipeline** — skills_skill_file_detection, skills_skill_structural_extraction, skills_skill_semantic_extraction, skills_skill_graph_building, skills_skill_community_labels, skills_skill_html_export [EXTRACTED 1.00]
- **Async Reliability Testing** — skills_skill_python_testing, references_async_and_concurrency_testing_async_concurrency_testing, references_async_and_concurrency_testing_leak_diagnostics [EXTRACTED 1.00]
- **Authentication Token Lifecycle** — specs_2026_08_01_authentication_authorization_design_local_password_auth, specs_2026_08_01_authentication_authorization_design_refresh_token_rotation, specs_2026_08_01_authentication_authorization_design_email_verification, specs_2026_08_01_authentication_authorization_design_google_oidc_flow [EXTRACTED 1.00]
- **Durable URL Data Model** — specs_2026_07_20_initial_data_model_design_user_model, specs_2026_07_20_initial_data_model_design_url_model, specs_2026_07_20_initial_data_model_design_click_event_model, specs_2026_07_20_initial_data_model_design_database_constraints [EXTRACTED 1.00]
- **Rate Limit Enforcement Flow** — specs_2026_07_29_sliding_window_rate_limiter_design_exact_sliding_window, specs_2026_07_29_sliding_window_rate_limiter_design_redis_sorted_set, specs_2026_07_29_sliding_window_rate_limiter_design_redis_outage_contract, plans_2026_07_29_sliding_window_rate_limiter_implementation_plan [EXTRACTED 1.00]

## Communities (41 total, 8 thin omitted)

### Community 0 - "Auth API and Sessions"
Cohesion: 0.10
Nodes (45): AsyncSession, BaseModel, get_settings(), get_session(), get_current_user(), EmailVerificationToken, login(), logout() (+37 more)

### Community 1 - "Auth Repository Tests"
Cohesion: 0.07
Nodes (25): test_email_verification_token_repository_creates_and_locks_record(), test_refresh_token_repository_creates_and_looks_up_record(), test_revoke_refresh_token_family_revokes_only_that_family(), test_authenticate_user_locks_account_after_five_failed_attempts(), test_authenticate_user_rejects_currently_locked_account(), test_authenticate_user_rejects_invalid_credentials(), test_authenticate_user_rejects_unverified_password_account(), test_authenticate_user_resets_failure_state_after_successful_login() (+17 more)

### Community 2 - "Database Models"
Cohesion: 0.08
Nodes (25): datetime, Base, DeclarativeBase, AuthIdentity, ClickEvent, OAuthAuthorizationRequest, Url, create_url() (+17 more)

### Community 3 - "Auth Endpoint Tests"
Cohesion: 0.12
Nodes (36): MonkeyPatch, TestClient, client(), create_pending_verification(), create_verified_user(), suppress_verification_email(), test_forgot_password_always_returns_202(), test_login_rejects_unverified_password_account() (+28 more)

### Community 4 - "Authentication Service"
Cohesion: 0.19
Nodes (20): Exception, User, create_user(), get_user_by_email(), AccountLockedError, authenticate_user(), EmailTakenError, EmailUnverifiedError (+12 more)

### Community 5 - "Dependency Security Audits"
Cohesion: 0.12
Nodes (24): Path, _find_workspace_root(), _format_fix_versions(), _ignore_vuln_args(), Security audit tests using pip-audit to detect known vulnerabilities.  This test, Run pip-audit to check for known security vulnerabilities.      Detected vulnera, Verify that pip-audit can run successfully (even if vulnerabilities are found)., Walk up from ``start`` to the nearest ancestor containing ``uv.lock``.      The (+16 more)

### Community 6 - "App and Rate Limiting"
Cohesion: 0.13
Nodes (9): create_app(), RateLimitResult, SlidingWindowRateLimiter, get_redis_client(), limit_auth_write(), limit_guest_creation(), FastAPI, Redis (+1 more)

### Community 7 - "Graphify Tooling"
Cohesion: 0.11
Nodes (19): Folder Watching, URL Ingestion, Wiki Export, Cross-Repository Merge, Post-Commit Graph Hook, Concept Explanation, Graph Traversal, Path Query (+11 more)

### Community 8 - "Security Utilities Tests"
Cohesion: 0.19
Nodes (17): test_refresh_rejects_expired_token(), test_refresh_rejects_token_without_a_persisted_record(), test_access_token_contains_only_required_claims(), test_access_token_rejects_wrong_issuer_or_audience(), test_generate_opaque_token_returns_unique_nonempty_values(), test_normalize_email_strips_and_lowercases(), test_password_hash_is_argon2id_and_verifiable(), test_refresh_decoder_rejects_access_token() (+9 more)

### Community 9 - "FastAPI Design Guidance"
Cohesion: 0.13
Nodes (16): Class Dependencies, Yield Dependencies, Router-Level Configuration, Single Operation Functions, No Ellipsis Defaults, No Pydantic RootModels, Response Model Selection, Byte Streaming (+8 more)

### Community 10 - "Authentication Design"
Cohesion: 0.33
Nodes (7): Production Authentication and Authorization, Optional Authentication, Session-Backed JWT Authentication, Email Verification Lifecycle, Google OIDC Authorization-Code Flow, Local Password Authentication, Refresh Token Family Rotation

### Community 11 - "Python Testing Guidance"
Cohesion: 0.29
Nodes (7): Async and Concurrency Testing, Leak Diagnostics, Asyncer, Async and Sync Path Operations, Python Testing, Regression Testing, Test Doubles

### Community 12 - "Alembic Async Migrations"
Cohesion: 0.40
Nodes (4): do_run_migrations(), run_async_migrations(), run_migrations_online(), Connection

### Community 13 - "Sliding Window Limiting"
Cohesion: 0.40
Nodes (6): Sliding-Window Rate Limiting, Rate Limiter Implementation Plan, Strict Redis Rate Limiting, Exact Sliding-Window Log, Protected-Write Redis Outage Contract, Redis Sorted-Set Limiter State

### Community 14 - "Email Verification Delivery"
Cohesion: 0.40
Nodes (4): EmailDeliveryError, send_verification_email(), test_send_verification_email_hides_provider_failure(), test_send_verification_email_uses_fragment_token_and_idempotency()

### Community 15 - "Application Configuration"
Cohesion: 0.40
Nodes (3): BaseSettings, Settings, test_settings_reads_environment_variables()

### Community 16 - "URL and Analytics Design"
Cohesion: 0.40
Nodes (5): Guest URL Creation, Synchronous Click Analytics, Click Event Data Model, URL Data Model, User Data Model

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
Cohesion: 0.67
Nodes (3): Free-Threaded Python Testing, Deterministic Testing, Reliability and Lifecycle Contracts

### Community 21 - "Cross Version Testing"
Cohesion: 0.67
Nodes (3): Nox Multi-Python Test Matrix, Behavior-Oriented Tests, Contract-First Testing

## Knowledge Gaps
- **38 isolated node(s):** `backend`, `Frontend Serving`, `Yield Dependencies`, `Class Dependencies`, `JSON Lines Streaming` (+33 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `create_short_url()` connect `Database Models` to `Auth API and Sessions`, `Authentication Service`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `Auth API and Sessions` to `Auth Endpoint Tests`, `Authentication Service`, `App and Rate Limiting`, `Security Utilities Tests`, `Email Verification Delivery`, `Application Configuration`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `SnowflakeGenerator` connect `Authentication Service` to `Auth API and Sessions`, `Database Models`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 13 inferred relationships involving `SnowflakeGenerator` (e.g. with `AccountLockedError` and `EmailTakenError`) actually correct?**
  _`SnowflakeGenerator` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `User` (e.g. with `Base` and `AccountLockedError`) actually correct?**
  _`User` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Security audit tests using pip-audit to detect known vulnerabilities.  This test`, `Walk up from ``start`` to the nearest ancestor containing ``uv.lock``.      The`, `Return True when ``uv audit`` can run for this project (uv installed and a lockf` to the rest of the system?**
  _60 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Auth API and Sessions` be split into smaller, more focused modules?**
  _Cohesion score 0.09551020408163265 - nodes in this community are weakly interconnected._