# Raw collection caches — intentionally not published

This directory holds the raw API responses DAY ZERO collects during a run. Some of
those caches are **excluded from the public repository**, and this file explains
which and why.

## What is excluded

| Path | Why |
| --- | --- |
| `github_users.json` | Bulk third-party profile records — display names, self-reported locations, bios, company and personal website/contact fields, follower counts. |
| `github_orgs.json` | Organisation records carrying name, location and website fields. |

Both were removed from the entire public Git history before first publication; see
`research/prepublication_privacy_audit.md`.

## Why

1. **Third-party privacy.** These records describe real people who did not publish
   them *to this project*. Reading a public profile once to answer a research
   question is not the same act as redistributing hundreds of them as a downloadable
   file, and the project's data-ethics rules
   (`research/data_ethics.md`) forbid the second.
2. **Bulk redistribution serves no one.** Nothing in the public analysis needs the
   raw cache. Every conclusion is carried by the aggregate outputs in `outputs/`,
   which contain no personal fields.
3. **API-derived data goes stale.** Profile fields change. A cache frozen at one
   moment is a poor artifact to hand someone as if it were durable ground truth.

## What *is* public

Everything needed to understand, audit and re-run the method:

- **The collection code** — `src/dayzero/collect.py` and its adapters, so the
  retrieval logic is fully inspectable.
- **The schemas and config** — including the frozen rule manifests.
- **The canonical aggregate outputs** — `outputs/**`, which are privacy-filtered by
  construction and are what every published figure is computed from.
- **The tests**, including a full-history privacy test that fails if a raw cache is
  ever reintroduced.
- The remaining collection caches in this directory that carry no personal fields:
  repository metadata, contributor login/commit counts, releases, and arXiv records.

## Regenerating them

`python -m dayzero.collect` rebuilds the caches from the GitHub and arXiv APIs. The
result will not be byte-identical to the original run — upstream data changes — so
hashes recorded in the frozen manifests will not reproduce. That is a limitation of
any API-sourced corpus, and it is stated rather than papered over.

The excluded paths are listed in `.gitignore`, so a fresh run cannot accidentally
stage them again.
