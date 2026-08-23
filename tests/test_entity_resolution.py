"""Conservative entity resolution, including the Phase 1 collision fixtures."""
from dayzero.resolve import (MERGED, POSSIBLE_MATCH, REJECTED, decide_merge,
                             identity_confidence, project_collision)


def test_agency_collision_does_not_merge():
    """Array's portfolio company 'Agency' vs AgentOps 'Agency' — Array did not back
    the latter. Merging would produce a false statement about who backed whom."""
    r = project_collision("Agency", "Agency", "getagency.example", "agentops.ai")
    assert r.collides is True


def test_eventual_collision_survives_identical_round_size():
    """Two 'Eventual' companies, both with a $7.5M seed. Name + round size is the
    most tempting merge key available, and it is forbidden."""
    r = project_collision("Eventual", "Eventual", "", "", "7.5M", "7.5M")
    assert r.collides is True
    assert "NOT merge evidence" in r.basis


def test_same_name_same_domain_is_the_same_entity():
    r = project_collision("Daft", "Daft", "daft.ai", "https://daft.ai")
    assert r.collides is False


def test_name_similarity_never_merges():
    d = decide_merge(a_profile_url="https://github.com/vivekchand",
                     b_profile_url="https://x.com/vivek_chand",
                     name_similarity=True)
    assert d.status == POSSIBLE_MATCH
    assert d.rule is None


def test_explicit_cross_link_merges():
    d = decide_merge(a_profile_url="https://github.com/a",
                     b_profile_url="https://example.com/me",
                     a_self_links=["https://example.com/me"])
    assert d.status == MERGED and d.rule == "self_published_link"


def test_no_evidence_rejects():
    d = decide_merge(a_profile_url="https://github.com/a", b_profile_url="https://x.com/b")
    assert d.status == REJECTED


def test_artifact_cross_reference_merges():
    d = decide_merge(a_profile_url="a", b_profile_url="b", artifact_cross_reference=True)
    assert d.status == MERGED


def test_identity_confidence_low_without_a_name():
    assert identity_confidence(has_real_name=False, has_self_published_site=False,
                               has_org_membership=False, cross_channel_links=0) == "low"


def test_identity_confidence_high_requires_a_name():
    assert identity_confidence(has_real_name=True, has_self_published_site=True,
                               has_org_membership=False, cross_channel_links=1) == "high"
    assert identity_confidence(has_real_name=False, has_self_published_site=True,
                               has_org_membership=True, cross_channel_links=2) != "high"


def test_bots_are_never_people(conn):
    n = conn.execute("SELECT COUNT(*) FROM identities WHERE handle LIKE '%[bot]'").fetchone()[0]
    assert n == 0


def test_paper_link_requires_exact_author_overlap():
    from dayzero.adapters.arxiv import author_overlaps
    assert author_overlaps(["Cong Wang"], ["Cong Wang"]) == ["cong wang"]
    assert author_overlaps(["Cong Wang"], ["Wang"]) == []
    assert author_overlaps(["Yusheng Zheng"], ["云微"]) == []
