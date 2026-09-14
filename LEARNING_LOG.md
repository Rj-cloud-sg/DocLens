Primary key — uniquely identifies each row; must be stable (never changes, never reused). We used SERIAL, which auto-generates incrementing integers via a hidden sequence object (nextval()).

Foreign key — a column whose value must match an existing primary key in another table; the database enforces this (referential integrity), rejecting inserts that violate it.

Unique vs. Not Null — two separate constraints. NOT NULL = can't be empty. UNIQUE = no duplicate values across rows. A primary key doesn't automatically prevent duplicate emails — that's why email needed its own UNIQUE constraint.

Index — an additional data structure that speeds up row lookup. Learned that PRIMARY KEY and UNIQUE constraints automatically create indexes behind the scenes (saw this directly in \d users output).

Transaction — groups multiple operations into one atomic unit; all-or-nothing (commit or rollback).

Principle of least privilege — give every user/process only the access it actually needs. Applied this by creating doclens_user (scoped only to the doclens database) instead of connecting as the postgres superuser — contains the "blast radius" of bugs or leaked credentials.

Virtual environments — isolated, project-specific copies of Python + installed packages, so different projects can have different dependency versions without conflicting. Analogous reasoning to the least-privilege/isolation principle, just at the Python-package layer instead of the database layer.

.gitignore — excludes files from git tracking; used for things that are large, regenerable, and machine-specific (venv folders) or sensitive (.env with secrets/credentials).

Decorators (@app.get(...)) — Python syntax that registers a plain function to run when a specific URL + HTTP method is hit; connects your code to FastAPI's routing system.

Health check endpoints — small, no-business-logic endpoints real systems use so load balancers/monitoring tools can check if a server is alive.

SQLAlchemy engine vs. connection — create_engine() doesn't open a live connection immediately; it's a manager/factory that knows how to connect. The actual network connection happens at engine.connect().

Context managers (with ... as ...) — guarantees cleanup (like closing a DB connection) happens automatically, even if an error occurs mid-block — prevents connection leaks.

Connection strings — postgresql://user:password@host:port/database — a pattern used across nearly all database tools, not just SQLAlchemy.

ORM (Object-Relational Mapper) — translates between Python classes/objects and database tables/rows; SQLAlchemy generates real SQL underneath every operation
VARCHAR / String(255) — same concept in SQL and Python; a variable-length text field with a max length

SQLAlchemy Column, primary_key=True — triggers auto-increment behavior on integer primary keys, same underlying mechanism as SERIAL
__tablename__ — the explicit bridge between Python class naming conventions and SQL table naming conventions

Sessions (sessionmaker, session.add(), session.commit()) — add() stages a change in memory; commit() executes it as a real transaction against the database. Ties directly to the transaction concept — staging multiple changes before committing lets you group them into one atomic unit.

Stories (problem → solution → alternatives → why)

Story 1 — Git initialized in the wrong location
Problem: ran git init in home directory instead of a project folder, which would have tracked unrelated files across the whole system.
Diagnosis: noticed Initialized empty Git repository in /home/allow-bad-names/.git/ — wrong path.
Fix: removed .git, created a dedicated project folder, reinitialized there, then had to merge divergent histories (--allow-unrelated-histories --no-rebase) since GitHub already had a commit from the first (wrong) push, and set upstream tracking properly.
Lesson: always confirm your working directory before running git init; diagnose git state with git status/git log --oneline --all rather than guessing.

Story 2 — Postgres schema permission error
Problem: CREATE TABLE failed with "permission denied for schema public" even after granting database-level privileges.
Why: Postgres 18+ separates database-level grants from schema-level grants; GRANT ALL PRIVILEGES ON DATABASE doesn't include the public schema.
Fix: GRANT ALL ON SCHEMA public TO doclens_user.
Lesson: privilege systems can have more granular layers than expected; read error messages precisely rather than assuming the obvious grant covers everything.

Story 3 — VS Code/WSL connection failure
Problem: VS Code couldn't open the project folder — first "unable to resolve resource," then a WebSocket 1006 error.
Diagnosis: verified the filesystem itself was fine (from a plain terminal) before assuming the project was broken — isolated the failure to VS Code's remote connection specifically, not the files.
Fix: confirmed WSL status from an actual Windows terminal (wsl --status), then wsl --shutdown to reset the WSL backend, closed VS Code fully, reopened via code . from inside WSL.
Lesson: isolate which layer of the system is actually failing (filesystem vs. app vs. remote connection vs. OS-level virtualization) before attempting fixes — a great "how I approach debugging" story.

Story 4 — Why doclens_user instead of postgres superuser
Problem/tradeoff: the app needs to connect to Postgres somehow.
Alternatives: connect as the existing postgres superuser (simpler, no extra setup) vs. create a dedicated limited user.
Decision: created doclens_user, scoped only to the doclens database.
Why: least privilege — contains the damage of a bug or leaked credentials to just this one database, rather than every database on the machine.

Story 5 — Why FastAPI BackgroundTasks instead of Celery/Redis (concept locked in, not yet built — worth pre-logging the reasoning now since we've discussed it multiple times)
Alternatives: Celery + Redis (durable, scales across processes, survives restarts) vs. FastAPI's built-in BackgroundTasks (simple, no extra infrastructure, but jobs are lost on restart, tied to a single process).
Decision: BackgroundTasks for MVP.
Why: the project's expected scale doesn't justify the added infrastructure complexity; explicitly an intentional tradeoff, with a clear upgrade path if reliability/scale needs increased.

Story 7 — psql showed 0 rows, Python showed 1 row: apparent contradiction, actually just command order
Problem: checked psql and saw an empty table right after also seeing a successful Python insert — looked contradictory at first glance.
Diagnosis: realized the psql check happened before the Python insert script ran, not after — a command-ordering mistake, not a real bug.
Lesson: before assuming a discrepancy is a bug, check the actual sequence of what ran when — this is a basic but real debugging habit.

New tradeoff (already discussed, worth logging formally now)

Raw SQL first, then ORM — deliberately learned raw SQL and created the first table by hand before introducing SQLAlchemy, so the ORM would be understood as a translation layer rather than an opaque abstraction.