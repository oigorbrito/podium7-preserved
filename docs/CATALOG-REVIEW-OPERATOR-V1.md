# Podium 7 Catalog Review Operator V1

Status: **internal/private operator contract; merge pending executable repository CI**.

## Purpose

Provide a minimal operator surface for the durable Catalog Identity review queue without changing resolver policy or bypassing evidence-backed review semantics.

Canonical invocation:

```text
python -m podium7 review list --database <path> [--limit N]
python -m podium7 review show <review_id> --database <path>
python -m podium7 review match <review_id> <vehicle_id> --database <path> --actor <id> --reason <text>
python -m podium7 review create <review_id> --database <path> --actor <id> --reason <text>
```

`scripts/resolve_catalog_review.py` is retained only as a compatibility wrapper. It translates its legacy argument shape into the canonical `python -m podium7 review ...` surface and contains no independent database-opening or resolution logic.

## Database safety boundary

The operator requires an **existing** SQLite file that already contains the supported Podium evidence, Catalog V2, and durable catalog-review schemas.

Before normal opening, the canonical operator resolves the supplied filesystem path and performs a read-only SQLite preflight on that canonical target. The same resolved path is then used for the normal CatalogStore open, so a symlink/relative alias is not validated through one pathname and reopened through another. The preflight verifies:

- the V1 persistence `PRAGMA user_version` is exactly supported;
- the required evidence/catalog/review tables and indexes exist;
- the `catalog` schema component version is exactly supported;
- the `catalog_review` schema component version is exactly supported.

Missing files, `:memory:`, empty files, unrelated SQLite databases, catalog databases without the review component, and unsupported schema versions fail closed. The preflight must not initialize or upgrade those files.

The compatibility script inherits the same preflight; it must never recreate the historical behavior where a missing/default database could be initialized merely by invoking the review operator.

## Read operations

`list` returns only open review tasks, bounded by the existing queue limit contract. It intentionally keeps output compact and does not expand source/candidate context.

`show` returns one review task plus:

- the retained raw-evidence and source context;
- canonical catalog identities for the task's candidate IDs.

Candidate IDs stored on the durable task remain historical audit references. If a candidate has since been merged, `show` resolves it through catalog redirects when presenting the candidate entity.

## Mutation operations

`match` and `create` delegate to the existing catalog review domain functions. They do not implement an alternate resolver or persistence path.

Both require explicit `actor` and `reason` values. The domain layer remains responsible for candidate validation, redirects, idempotency, atomic candidate-fact persistence, evidence-backed creation, and durable resolution metadata.

- `match` may resolve only to a current canonical target derived from a candidate already attached to the review task.
- `create` creates the review identity through the existing evidence-backed catalog creation gate.
- conflicting second resolutions fail closed.

## Output and errors

Successful canonical commands emit JSON with `status: "PASS"` and exit code `0`.

Runtime/preflight/domain failures emit JSON with `status: "FAIL"` and exit code `1`. Argument-shape errors remain owned by `argparse`.

No authentication system is introduced by this local/internal CLI. `actor` is durable audit attribution, not proof of external identity or authorization.

## Boundaries

This V1 operator does not:

- change Catalog Identity resolver semantics;
- weaken `REVIEW` decisions;
- infer missing identity fields;
- introduce a network service or UI;
- change the Catalog JSON Contract V2;
- change software licensing or public-release status;
- create or upgrade a database implicitly.
