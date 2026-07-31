# Sliding-window rate limiter design

**Status:** approved design; implementation plan pending review  
**Date:** 2026-07-29

## Decision

Replace the previously planned Redis fixed-window counter with an exact
sliding-window log for abuse-sensitive writes. Fixed windows permit a burst at
their boundary; Smolink needs fair enforcement for authentication and public
URL creation.

## Algorithm

Each limit scope has one Redis sorted-set key. Its members are unique request
tokens and their scores are Unix timestamps in milliseconds. One Lua script
atomically removes members outside the window, counts those remaining, rejects
when the count is at the limit, otherwise records the request and sets expiry.
The Python wrapper derives a positive `retry_after` from the oldest score.

## Policies and failure behavior

- `rate:auth:{ip}` — 5 requests per IP per rolling 60 seconds.
- `rate:create:guest:{ip}` — 10 requests per IP per rolling 60 seconds.
- `rate:create:user:{user_id}` — 30 requests per user per rolling 60 seconds.

`GET /health` and `GET /{short_code}` are un-limited. Redis errors on
protected writes return `503`; redirect-cache failures remain a separate
Postgres-fallback concern. Keys are ephemeral enforcement data, never durable
application data.

## Interface and verification

`SlidingWindowRateLimiter.check(key, limit, window_seconds)` returns `allowed`,
`count`, and `retry_after`. Local Redis tests prove pruning, separate keys, and
rejection. Endpoint tests then prove `429` with `Retry-After` and a simulated
Redis outage proves `503`.

## Scope

This does not add proxy-aware IP extraction, an admin dashboard, workers,
Kafka, or frontend controls.
