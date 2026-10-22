# AI Usage

## AI tool

AI assistant using Copilot SDK in VS Code.

## Important prompt summary

- Build a small full-stack Service Desk ticket application with a REST API, a working frontend, and Docker Compose for local use.
- Validate server-generated ticket IDs, trimmed titles of 1–80 characters, allowed priorities and statuses, malformed JSON, missing tickets, and persistence across container restarts.
- Include a project README with the selected tools, commands, API base, project structure, and named volume, plus this AI usage record.

## Review and verification

- Reviewed the generated design against the requested scope: no authentication, uploads, delete action, timestamps, seed data, dashboard, or cloud deployment.
- Kept database persistence on the backend in SQLite and mounted the data directory as a Docker named volume.
- Inspected API input validation and response behavior, including strict string validation, title trimming, server-owned IDs, the fixed `open` create status, JSON validation errors, and 404 handling.
- Built and started both containers with Docker Compose. Verified health, the initially empty ticket list, create and status-update responses, and the Nginx-proxied frontend.
- Rejected 11 invalid API payloads with JSON errors without changing the ticket count; also verified a missing ticket returns JSON 404.
- Changed a ticket status in the browser and confirmed the filter showed only matching tickets.
- Ran `docker compose down` followed by `docker compose up -d`; both tickets and their changed status remained intact in the named volume.
