# READ-IT! — Project Guide for Developers and AI Assistants

## 1. Project purpose

**READ-IT!** is a private, self-hosted messaging platform. It is intended to run on the owner's own server, with messaging initially focused on the owner and later on approved friends. It is not intended to be a public, open-registration messaging service.

Repository: https://github.com/null-patch/READ-IT

This document is an orientation and handoff guide. The checked-in repository is the source of truth; inspect the current code before making changes. Some status notes below come from earlier project work and must be re-verified against the current checkout.

## 2. Known technology stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy ORM
- UUID identifiers
- JWT-based authentication and a `current_user` authentication dependency
- WebSockets for real-time messaging

Confirm exact dependency versions and commands from the repository's dependency files and configuration. Do not assume a package manager or deployment layout without checking.

## 3. Architecture and data model

The known backend structure uses an `app` Python package. The following modules were supplied or discussed:

| Module | Responsibility |
|---|---|
| `app/database/database.py` | Builds the SQLAlchemy engine from `app.core.config.settings.DATABASE_URL`, creates `SessionLocal`, declares the shared ORM `Base`, and provides the `get_db()` dependency. |
| `app/models/message.py` (uploaded as `message(2).py`) | SQLAlchemy `Message` model mapped to `messages`. |
| `app/models/conversation.py` (uploaded as `conversation(2).py`) | SQLAlchemy `Conversation` model mapped to `conversations`. |
| `app/models/conversation_member.py` (uploaded as `conversation_member(2).py`) | Membership association model mapped to `conversation_members`. |

The uploaded filenames may not match the repository's actual paths. Verify paths and imports in the checkout before editing.

### `Message` model — fields observed

- `id`: PostgreSQL UUID primary key, generated with `uuid.uuid4`
- `conversation_id`: required UUID foreign key to `conversations.id`, with `ON DELETE CASCADE`
- `sender_id`: nullable UUID foreign key to `users.id`, with `ON DELETE SET NULL`
- `message_type`: required `String(20)`, default `"text"`
- `content`: nullable text
- `edited`: non-null Boolean, default `False`
- `deleted`: non-null Boolean, default `False`
- `created_at`: timezone-aware datetime with database-side `func.now()` default

### `Conversation` model — fields observed

- `id`: PostgreSQL UUID primary key, generated with `uuid.uuid4`
- `type`: required `String(20)`
- `title`: nullable `String(255)`
- `created_by`: nullable UUID; the supplied model did not show a foreign-key constraint for this field
- `created_at`: timezone-aware datetime with database-side `func.now()` default

### `ConversationMember` model — fields observed

- `conversation_id`: UUID foreign key to `conversations.id`, `ON DELETE CASCADE`, part of a composite primary key
- `user_id`: UUID foreign key to `users.id`, `ON DELETE CASCADE`, part of a composite primary key
- `joined_at`: timezone-aware datetime with database-side `func.now()` default

### Database session setup observed

`database.py` reads `settings.DATABASE_URL`, calls `create_engine(..., pool_pre_ping=True, future=True)`, creates a `sessionmaker` with `autocommit=False` and `autoflush=False`, and defines `get_db()` as a generator that yields a session and closes it in `finally`.

Do not change schema semantics or delete behavior casually. Check migrations, deployed schema, relationships, indexes, and existing API contracts before changing ORM models.

## 4. Project progress and known areas to audit

Earlier project context indicated that Milestones 1–5 were structurally implemented but needed an audit. These are historical notes, not proof that the current checkout still has the same state.

- **Milestones 1–5:** audit existing implementation and validate it before adding major features.
- **Milestone 6 — calls/WebRTC:** not started in the last recorded project status. Do not begin this milestone until startup, backend APIs, database behavior, authorization, and WebSocket behavior have been validated.
- **Milestone 7 — AI Friend:** not started in the last recorded project status.
- **Message-read API issue:** a previous startup blocker involved using a SQLAlchemy ORM model named `MessageRead` as a FastAPI response model (`list[MessageRead]`). The intended fix was to define a Pydantic response schema such as `MessageReadResponse` in `schemas/message_read.py`, configure `from_attributes=True`, and use that schema in the relevant API response declarations. Re-check the current code and error before applying this fix; do not blindly duplicate an existing schema.
- **Friend API/service consistency:** an earlier audit identified a possible mismatch where `api/friend.py` imported `app.services.friend.FriendService`, while `services/friend_service.py` appeared to expose differently named functions. Verify the actual files and imports.
- **WebSocket modules:** an earlier audit noted possible overlap between `app/api/ws.py` and `app/api/websocket.py`. Determine which router/module is active and consolidate only if justified by the actual code and tests.

## 5. Non-negotiable implementation rules

Any AI assistant or developer working on this repository should follow these rules:

1. **Inspect before editing.** Read the relevant implementation, callers, schemas, tests, configuration, and migrations before changing code.
2. **Use the repository as the source of truth.** Do not invent missing modules, routes, settings, database tables, or business rules.
3. **Fix issues incrementally.** Address one startup/runtime issue at a time, then rerun the relevant checks.
4. **Preserve architecture and compatibility.** Keep existing naming, API paths, response shapes, authentication flow, formatting, and working functionality unless a change is necessary and explicitly explained.
5. **No silent architecture changes.** Explain the reason and impact of any proposed structural change before applying it.
6. **No placeholder implementations.** Do not leave TODO-only functions, fake success responses, stubbed security checks, or incomplete code presented as finished.
7. **Do not skip required imports or files.** Trace model registration, router registration, schema imports, configuration, and migration dependencies.
8. **Authorization is mandatory.** Verify that a user is authenticated and is authorized to access the requested conversation/message. Being authenticated alone must not grant access to another user's private conversations.
9. **Persist before broadcasting.** For real-time messaging, commit/persist the message successfully before broadcasting it to WebSocket clients.
10. **Friends-only access.** Preserve the private/friends-only product model; do not introduce public access or unrestricted discovery without an explicit requirement.
11. **Database correctness matters.** Check foreign keys, `ON DELETE` behavior, uniqueness, indexes, migrations, transaction boundaries, and ORM/Pydantic compatibility.
12. **Validate before advancing milestones.** Do not start WebRTC/calls work until the existing backend and WebSockets have been checked and validated.
13. **Report uncertainty honestly.** Distinguish verified facts from assumptions and historical notes. Do not claim tests passed unless they were actually run.

## 6. Recommended work order

Start from the current checkout and follow this sequence:

1. **Inventory the repository:** inspect the tree, dependency/lock files, environment example, README/docs, tests, Alembic configuration and migrations, and application entry point.
2. **Check configuration safely:** identify required environment variables from the settings code. Never print or commit secrets, tokens, passwords, or production database URLs.
3. **Run compile/import checks:** use the project's actual virtual environment and documented commands. Record the exact first error and fix that before proceeding.
4. **Start the application:** use the repository's documented Uvicorn/FastAPI entry point and confirm startup succeeds.
5. **Verify database schema:** compare SQLAlchemy models and migrations with the actual expected PostgreSQL schema. Confirm all models are imported/registered before metadata or migrations are used.
6. **Audit APIs and Pydantic schemas:** check response models, UUID serialization, request validation, status codes, error handling, and consistency between routes and services.
7. **Audit access control:** test conversation membership checks, message-read permissions, friend restrictions, and attempts to access other users' IDs.
8. **Audit WebSockets:** check authentication, connection lifecycle, membership authorization, disconnect cleanup, duplicate routers, and persist-before-broadcast behavior.
9. **Run tests and static checks:** use the commands and tools defined by the repository. Add focused regression tests for each fix.
10. **Only then plan the next milestone.** Do not implement calls or AI-friend functionality while core behavior remains unvalidated.

## 7. Security and operational expectations

- Keep secrets in environment variables or the project's intended secret-management mechanism.
- Do not commit `.env` files, credentials, JWT secrets, private keys, database dumps, or real user messages.
- Validate and authorize every object ID supplied by a client.
- Avoid leaking internal exception details or secrets in API responses and logs.
- Use parameterized ORM/query APIs; do not build SQL from untrusted input.
- Use explicit transaction/commit behavior and handle rollback on failures where appropriate.
- Apply schema changes through the repository's migration system when one exists; do not rely on manual production-only database edits.
- Treat message deletion/editing and read-state behavior as API and data-contract decisions, not just column changes.

## 8. Useful first commands

Run commands from the repository root, adapting paths to the actual checkout and virtual environment:

```bash
git status --short
find . -maxdepth 3 -type f | sort
```

If the project uses a local virtual environment, activate it according to the repository's instructions before running Python commands. Then inspect its dependency files and documented test/lint commands.

A compile check may be useful once the environment is active:

```bash
python -m compileall -q .
```

This only checks Python compilation; it does **not** prove imports resolve, the application starts, the database schema is correct, or the APIs are secure.

Use the repository's actual documented startup command rather than assuming an entry-point module. Do not run destructive migrations or database-reset commands against a real database without a verified backup and explicit authorization.

## 9. How an AI assistant should report work

For each task, report:

- **Observed problem:** the exact error or behavior and where it occurs.
- **Root cause:** evidence from the code, not a guess.
- **Files changed:** every file modified and why.
- **Fix:** what changed and any API/database compatibility impact.
- **Validation:** exact commands run and their real outcomes; clearly label checks not run.
- **Next step:** the single most useful next action.

Prefer small, reviewable patches. Do not rewrite entire modules when a focused change is sufficient. If essential information is missing, state the assumption or ask one targeted question instead of fabricating project details.

## 10. Current task handoff

The latest recorded technical focus was resolving and validating the message-read API and its Pydantic response schema. Begin by inspecting the current `MessageRead` model, related schema files, API route, service/repository code, and tests. Reproduce the current error, make the smallest compatible correction, then validate application startup and the affected endpoint before moving to other issues.

---

**Maintenance note:** Update this README when architecture, milestone status, setup commands, or API/database contracts are verified to have changed. Mark unverified progress as unverified rather than treating historical notes as current facts.
