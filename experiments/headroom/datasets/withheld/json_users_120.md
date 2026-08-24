# Withheld benchmark sample — `json_users_120`

This sample is part of the pre-registered EXP-1 corpus but is **not distributed in
the public repository**. Only its metadata appears here.

| Property | Value |
| --- | --- |
| Sample ID | `json_users_120` |
| Category | `structured_json` |
| Format | `json_pretty` |
| Size | 40,563 bytes |
| Records | 120 |
| Probe tokens | 2 (values withheld) |
| Original SHA-256 | `5c2716f2e53f44a74523f6aa4f6ab231229153522e8bb0bb91ebcade1dacbbda` |
| Provenance | GitHub REST API profile responses, collected in Phase 2 |
| Original path | `experiments/headroom/datasets/samples/json_users_120.txt` |

## Why it is withheld

The sample is a slice of a raw GitHub user-profile cache. Those records carry
per-person fields — display names, self-reported locations, bios and personal
website/contact fields — and several of the contact fields contained live email
addresses. Every field was public on GitHub at collection time, but redistributing
120 such profiles as a bulk file in a public repository is a different act from
reading them once for research, and it is the kind of redistribution this project's
own data-ethics rules prohibit. The file was therefore removed from **all** public
Git history before the repository was first published.

## What this does and does not affect

- **The original result is unchanged.** EXP-1 ran on all 35 samples
  (1,573,042 bytes) and its verdict, distributions and per-sample measurements
  stand exactly as recorded. Nothing was recomputed to make the public repository
  look tidier.
- **The manifest still lists this sample.** `datasets/manifest.json` is the frozen,
  pre-registered dataset description and its `manifest_sha256` is published as part
  of the protocol. Editing it to erase a sample would invalidate the
  pre-registration, so it was left byte-identical.
- **Byte-exact re-execution of the original run is not possible from the public
  repository alone**, because this input is absent. See
  `research/headroom_public_subset_sensitivity.md` for a 34-sample recomputation
  and `experiments/headroom/README.md` for the reproducibility taxonomy.

## Does withholding it change the findings?

No. Re-running the pre-registered analysis over the 34 distributable samples moves
the structured-JSON medians by −0.28 pp (vs raw) and −1.36 pp (vs minified), leaves
the coding and agent results at 0.00%, leaves probe retention at 1.0000 and zero
transformation errors, and returns the same verdict — `PARTIALLY_REPRODUCED` — with
the same three claims supported and the same two not. Full detail in
`research/headroom_public_subset_sensitivity.md`.

## Reconstructing it

The sample was produced by `experiments/headroom/build_datasets.py`, which slices
the first 120 logins (sorted) from a `data/collected/github_users.json` cache built
by `src/dayzero/collect.py`. Anyone with GitHub API access can regenerate an
equivalent cache, but it will not be byte-identical to the original — profile
fields change over time — so the original SHA-256 above will not reproduce.
