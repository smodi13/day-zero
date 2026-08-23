import raw from "@/data/research.json";

/** The single source of truth for every value the site asserts.
 *  Nothing in this app may hard-code a research number. */
export const research = raw as unknown as Research;

export type EvidenceStatus =
  | "OBSERVED" | "OBSERVED_AS_CLAIM" | "INFERRED" | "UNKNOWN" | "NOT_FOUND";

export interface Lead {
  subject: string; builder: string; project: string; whyNow: string;
  artifact: string; technicalDepth: string; formationEvidence: string;
  arrayRelevance: string; whyMissed: string; strongestPositive: string;
  strongestNegative: string; technicalQuestion: string; commercialQuestion: string;
  mustVerify: string; signals: string[]; channels: string[];
  formationState: string; systemState: string; analystOverride: boolean;
}

export interface Dist {
  n: number; median: number; p25: number | null; p75: number | null;
  min: number | null; max: number | null;
}

export interface Research {
  generatedFrom: string;
  commits: Record<string, string>;
  hashes: { v1Frozen: string; v2Rules: string; experimentProtocol: string; experimentDataset: string };
  current3: Lead[];
  introQueue: { count: number; current3Emitted: boolean; contactedAnyone: boolean };
  sandlock: {
    recommendation: string; recommendationVocabulary: string[];
    financingWording: string; financingStatusCode: string; biggestRisk: string;
    construction: { human_contributors: number; top_contributions: number;
      weekly_commits_last_12: number[]; releases: string[];
      languages: Record<string, number>; architectures: string[] };
    attention: { stars: number; forks: number; open_issues: number; note: string };
    companyStatus: Record<string, unknown>;
    defensibility: { proven: string[]; potential: string[]; not_a_moat: string[] };
    guard: { passed: boolean; basis: string; caveat: string };
    agentsight: { established: string; not_established: string; sourcing_consequence: string };
    claims: { id: string; claim: string; status: EvidenceStatus; source?: string;
      verified_independently?: boolean; note?: string }[];
    competitors: Competitor[];
    sources: SourceRow[];
  };
  headroom: {
    verdict: string;
    dataset: { sampleCount: number; totalBytes: number;
      categories: Record<string, number>; tokenizers: string[];
      primaryTokenizer: string; baselines: string[]; primaryBaseline: string };
    claims: Record<string, { supported: boolean; value: number | null; threshold: string }>;
    supported: string[]; failed: string[];
    headline: Record<string, number | null>;
    categories: Record<string, { vsRaw: Dist; vsMinified: Dist; minifyOnlyVsRaw: Dist; retention: number }>;
    samples: HeadroomSample[];
    retention: number; errors: number;
    environment: Record<string, unknown>;
    supplementary: { id: string; hypothesis: string; method: string; conclusion: string }[];
    untested: string[];
    sourceClaims: { id: string; text: string; source: string }[];
  };
  methodology: {
    v1: { tally: Record<string, number>; hash: string; label: string };
    v2Exploratory: { tally: Record<string, number>; v1Tally: Record<string, number>;
      cases: Record<string, unknown>[]; label: string };
    unseen: { tally: Record<string, number>; cases: Record<string, unknown>[];
      label: string; cohortSize: number; eligible: number; freezeCommit: string;
      noStatistic: string };
    negativeControls: { v1: Record<string, number>; v2Regressions: number;
      v2Controls: Record<string, unknown>[] };
  };
  signals: {
    channels: Channel[];
    identity: { total_identities: number; states: Record<string, number>;
      mergeable_identities: number; mergeable_pct: number;
      x_linkable_count: number; x_linkable_pct: number;
      context: Record<string, unknown>; methods_excluded: string[] };
    domain: { with_a_project_domain_pct: number; domain_adds_distinct_pct: number;
      repositories_measured: number;
      interpretation: string; methods_excluded: string[] };
    attentionVsConstruction: { high: AvcRow[]; low: AvcRow[]; note: string };
  };
  scale: Record<string, number>;
}

export interface AvcRow {
  repo: string; stars: number; top_contributions: number; stars_per_commit: number | null;
}

export interface HeadroomSample {
  id: string; category: string; raw: number; minified: number; headroom: number;
  vsRaw: number | null; vsMinified: number | null; vsCompact: number | null;
  gzipVsRaw: number | null; retention: number;
}

export interface Competitor {
  name: string; isolation_boundary: string; kernel: string;
  root_required?: string | boolean; startup?: string; security_ceiling?: string;
  escape_requires?: string; filesystem?: string; sandlock_difference: string;
  source?: string;
}

export interface SourceRow {
  id: string; source: string; type: string; establishes: string;
}

export interface Channel {
  channel: string; evidence_records: number; raw_records: number;
  formation_signals: number; api_requests?: number; note?: string;
  technical_artifacts: number; unique_subjects: number;
}

export const DISCLAIMER =
  "DAY ZERO is an independent research project and is not affiliated with, sponsored by, " +
  "or endorsed by Array Ventures, Shruti Gandhi, Multikernel Technologies, Sandlock, " +
  "Headroom Labs, or any person or company referenced in the analysis. It is based " +
  "entirely on public information and is not investment advice.";
