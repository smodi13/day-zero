# Negative Controls — Results

**Rules hash:** `ad0b7ae00630f7948e7c4444440af7c20fed61169370e46e076cd8f575a3566c`

> The control set is curated. This measures design failure modes, not statistical specificity.

| Result | Count |
| --- | --- |
| CORRECTLY_REJECTED | 3 |
| COVERED_BY_UNIT_TEST | 5 |
| REJECTED_FOR_A_DIFFERENT_REASON | 4 |

| ID | Control | Subject | Expected reason | State | Actual reason | Result |
| --- | --- | --- | --- | --- | --- | --- |
| NC-1 | Viral repo, near-zero construction | 0xSero/turboquant | INSUFFICIENT_TECHNICAL_DEPTH | DROP | ABANDONED | REJECTED_FOR_A_DIFFERENT_REASON |
| NC-2 | Thin wrapper as infrastructure | class:wrapper | WRAPPER_ONLY | N/A | - | COVERED_BY_UNIT_TEST |
| NC-3 | Abandoned project with formation shell | zerobootdev/zeroboot | ABANDONED | DROP | ABANDONED | CORRECTLY_REJECTED |
| NC-3b | Abandoned well-specified artifact | dipampaul17/KVSplit | ABANDONED | DROP | ABANDONED | CORRECTLY_REJECTED |
| NC-4 | Precise claim, no license, dead | scrya-com/rotorquant | ABANDONED | DROP | ABANDONED | CORRECTLY_REJECTED |
| NC-5 | Frontier-lab engineer, strong artifact, zero formation | RyanCodrai/turbovec | NO_FORMATION_EVIDENCE | WATCH | IDENTITY_UNRESOLVED | REJECTED_FOR_A_DIFFERENT_REASON |
| NC-6 | Established org resurfaced as new | thunder-id/thunderid | ALREADY_ESTABLISHED | WATCH | IDENTITY_UNRESOLVED | REJECTED_FOR_A_DIFFERENT_REASON |
| NC-7 | Research with no formation | FutureMLS-Lab/OSCAR | NO_FORMATION_EVIDENCE | WATCH | IDENTITY_UNRESOLVED | REJECTED_FOR_A_DIFFERENT_REASON |
| NC-8 | Hackathon demo that stopped | class:hackathon_stopped | ABANDONED | N/A | - | COVERED_BY_UNIT_TEST |
| NC-9 | Large following, weak artifact | class:curation_repo | INSUFFICIENT_TECHNICAL_DEPTH | N/A | - | COVERED_BY_UNIT_TEST |
| NC-10 | Excellent but out of thesis | class:out_of_thesis | OUTSIDE_THESIS | N/A | - | COVERED_BY_UNIT_TEST |
| NC-11 | Name-collision false positive | collision:Agency\|Eventual | IDENTITY_UNRESOLVED | N/A | - | COVERED_BY_UNIT_TEST |
