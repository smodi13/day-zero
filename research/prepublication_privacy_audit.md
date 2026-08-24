# Pre-publication privacy audit and history rewrite

**Before this repository was first made public, its Git history was privacy-scrubbed.**
This document records what was found, what was removed, and what that did and did not
change. It is published rather than quietly performed, because a project whose central
claim is *freeze the rules and publish the failures* cannot make an exception for its
own mistakes.

## What was found

A full-history audit — every reachable Git object, not just `HEAD` — was run as the
final gate before publication. It found that raw research caches, committed during
Phase 2 and Phase 3, contained bulk third-party profile data:

| Path | Content |
| --- | --- |
| `data/collected/github_users.json` | 267 GitHub profile records: display names (223), self-reported locations (150), bios (149), company fields (114), personal website/contact fields (114), follower counts (267). Four of the contact fields held live email addresses. |
| `data/collected/github_orgs.json` | 66 organisation records carrying name, location and website fields. |
| `experiments/headroom/datasets/samples/json_users_120.txt` | A 120-record slice of the same user cache, used as one benchmark input. |

Every field had been public on GitHub when collected. That is not the point. The
project's own data-ethics rules (`research/data_ethics.md`) and its public privacy
statement both say it does not redistribute personal contact information or bulk
person data, and shipping these files in a public repository would have made that
statement false in the same commit that published it. Reading a public profile once
for research and redistributing 267 of them as a downloadable file are different acts.

The audit also found personal filesystem paths (`/Users/<name>/…`) in a research
document.

Two things the audit deliberately did **not** treat as violations:

- **Named research subjects.** Builders, maintainers and companies discussed in
  Current 3, the Sandlock diligence and the historical case studies are intentional,
  professional research subjects, analysed from their public technical artifacts.
  Naming them is the work, not a leak.
- **Non-personal contact addresses.** The author's own GitHub `noreply` address
  (present in commit metadata by construction), Anthropic's `noreply` co-author
  trailer, a `user@github.com` documentation example inside a quoted README, and a
  venture firm's published deal-flow address cited as `OBSERVED` evidence all remain.
  None is a private individual's contact information.

## What was done

The original working repository remains **private and unmodified**. A separate
publication clone was made, and the rewrite was performed only inside that clone
using `git filter-repo`, before any public repository or remote existed. Specifically:

1. The three paths above were removed from **every** reachable commit and blob.
2. Personal filesystem paths were replaced with a neutral form (`~/day-zero`).
3. The scrub was verified by rescanning all 363 reachable objects: zero occurrences
   of the removed paths, zero occurrences of any of the four personal addresses, zero
   `/Users/<name>` paths.
4. A full-history privacy test (`tests/test_public_history_privacy.py`) was added so
   this cannot silently regress.

## What changed as a result — and what did not

**Commit object IDs changed.** Rewriting history necessarily rehashes every commit
from the first affected one onward. All twelve commits therefore have new IDs in the
public repository.

**Commit ordering did not change.** The sequence that carries the methodological
argument is intact and still verifiable with `git log`:

```
Phase 1 → v1 rules frozen → v1 result → experiment protocol frozen
       → v2 rules frozen → reproduction + diligence run
       → unseen cohort frozen → unseen validation → frontend → visual polish
```

Every freeze-before-result boundary survives. A rule set or cohort is still committed
*before* the outcome it governs exists, and that is still checkable from the public
history alone.

**Public hash references were updated** to the post-scrub equivalents wherever the
project points at a commit — the methodology page, the canonical
`cohort_freeze_commit` pointer, the phase reports and the generated frontend export.
Stale hashes that resolve to nothing would have been worse than useless.

**One category was deliberately left byte-identical:** `experiments/headroom/`. The
benchmark corpus, its `manifest.json` and the recorded results are pre-registered
artifacts whose SHA-256 hashes are published as part of the protocol. Several
benchmark samples are snapshots of the repository's own `git log` taken at experiment
time, so they quote pre-scrub commit IDs. Editing them to look consistent would have
falsified a pre-registered input and broken `manifest_sha256`. They are left as the
historical record they are, and this paragraph is the explanation.

**No research rule, threshold, decision or result was changed.** Not the Current 3,
not the Sandlock recommendation, not the v1 / v2 / unseen tallies, not the Headroom
measurements or verdict, not the negative controls, not any evidence classification.
The rewrite removed data; it did not touch findings. `research/phase4_report.md` and
the canonical outputs record the same numbers they did before.

The one substantive consequence for a reader is that the Headroom run can no longer
be re-executed byte-for-byte from the public repository, because one of its 35 inputs
is withheld. That is disclosed at
`experiments/headroom/datasets/withheld/json_users_120.md`, and a 34-sample
sensitivity check (`research/headroom_public_subset_sensitivity.md`) reports that
withholding it changes no verdict, no claim outcome and no headline figure by more
than 1.4 percentage points.

## Timing

The rewrite happened **before** first publication. No version of this repository
containing the removed files was ever pushed, hosted, shared or made public. The
exposure window was zero; what is described here is a gate that held, not an incident
that occurred.
