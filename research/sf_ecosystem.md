# DAY ZERO — SF Ecosystem Module (design)

## 1. Why this module exists

Array's AI Analyst posting asks for someone to *"attend in-person events, hackathons, and
community gatherings in San Francisco to build and maintain a live founder pipeline."*
The role is explicitly in-person.

This is not a gap in an automated system — it is the part of the system that a competitor
building a pure scraper cannot replicate. Some of the strongest Pool A evidence
(a hackathon team that stays together, a demo that is better than its README, a researcher
who is visibly restless) has **no online artifact at all**, and much of what does exist
online (Devpost) is closed to automated collection by policy (`data_sources.md` §3).

So the correct design is: **the programmatic channels handle everything they can, so that
human hours go where only a human can go.**

## 2. What the module tracks

Public, forward-looking information only:

- Hackathons (independent, corporate-hosted, and university)
- Technical meetups and user groups
- Research talks and seminars (university and lab-hosted)
- Demo days (accelerators, communities)
- Builder nights and open-source community events
- University events (Berkeley, Stanford, and SF-based programs)

## 3. Event record schema

```yaml
event_id:
name:
date:                    # ISO 8601
location:                # venue/neighborhood — public event location only
official_url:
organizer:
theme:                   # mapped to Array's named themes where applicable
why_relevant:            # one sentence tied to a cited Array theme, not a vibe
sourcing_objective:      # the specific question this attendance answers
builder_profile_sought:  # what kind of construction evidence to look for
attendance:              # ALWAYS defaults to null. Never inferred. Human-entered only.
post_event_notes:        # human-entered, optional
followups:               # links to person/artifact records created from the event
```

**`attendance` is never populated by the system.** DAY ZERO does not, and must not,
represent the operator as having attended anything. A record with `attendance: null` means
exactly that — an event was identified, nothing more.

## 4. The rule that makes hackathon signals worth anything

From `negative_controls.md` NC-8:

> A hackathon signal (S-07 / F-05) may enter the graph immediately, but it cannot
> contribute to a Weekly 3 record until a BUILD signal is observed **≥90 days after the
> event.**

The signal of interest is never the demo and never the win. It is **whether the thing was
still being built three months later.** Hackathon weekends produce impressive artifacts
almost by construction; persistence is the rare part.

This rule is also what converts an in-person event into a *durable* data asset: a name
noted at a demo night in August becomes a checkable GitHub query in November.

## 5. Sourcing objectives by event type

| Event type | What to look for | What to ignore |
| --- | --- | --- |
| Hackathon | Teams that formed *before* the event; projects that solve the builder's own problem; anyone who wrote the hard part rather than the demo | Prize winners as such; polish |
| Research talk | Who asks the sharp question; whose implementation exists; PhD students shipping tools alongside papers | Speaker prestige |
| Meetup / user group | Maintainers of things other attendees already depend on | Attendance counts |
| Demo day | Nothing — by demo day the company is legible and the round is usually done | Everything |
| Builder night / OSS meetup | People with a repo they've maintained for a year and no company | Pitch quality |

Demo days are listed as low-value on purpose: a demo day is the *end* of DAY ZERO's window,
not the beginning.

## 6. Privacy constraints specific to in-person research

- Record only what a person says publicly, in a public setting, about their public work.
- Do not record who attended with whom, or any social observation.
- Do not photograph or record attendees.
- Do not record a person's presence at an event as evidence about their employment status.
- If someone shares something in confidence, it is not a data point.

These follow from `data_ethics.md` §1–2 and are restated here because in-person research is
where they are easiest to violate accidentally.

## 7. Phase 1 status

**Designed, not populated.** No event has been researched, no event has been attended, and
no attendance has been recorded. Populating this module requires a live calendar sweep
each cycle, which is Phase 2 work.
