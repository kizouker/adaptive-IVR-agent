"""Content schemas: caller checklists (#143) + target-seed vocab (#40).

Validates the JSON SHAPE and grounding of the two content files:
data/role-phrasebooks.json (per-persona checklists with short rule hints)
and schemas/public-authority-ivr-target-seeds.json (AF menu vocabulary /
parlour seed). Seeds stay target-model only, never observations.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHRASEBOOKS = ROOT / "data" / "role-phrasebooks.json"
SEEDS = ROOT / "schemas" / "public-authority-ivr-target-seeds.json"

MIN_ROLES = 8
MIN_CHECKLIST_ITEMS = 3
MAX_RULE_HINT_LEN = 200  # 'why' is a short rule hint, not an essay

CHECKLIST_KEYS = {"say", "why", "source_url"}

# Robot-named words from the call transcripts (see phrasebook "sources"),
# not from the AF website taxonomy, so absent from the seed utterances.
TRANSCRIPT_WORDS = {"automatisk växel"}


def load_books():
    return json.loads(PHRASEBOOKS.read_text(encoding="utf-8"))


def load_seeds():
    return json.loads(SEEDS.read_text(encoding="utf-8"))


def seed_nodes(authority):
    """All tree nodes of one authority, depth-first."""
    out = []

    def walk(nodes):
        for node in nodes:
            out.append(node)
            walk(node.get("children", []))

    walk(authority["tree"])
    return out


# --- phrasebooks: checklist presence per persona (#143) ---


def test_phrasebooks_top_level_schema():
    raw = load_books()
    assert raw["schema_version"] == "1.0"
    assert raw["description"].strip()
    assert raw["sources"] and all(s.strip() for s in raw["sources"])
    assert raw["updated_at"].strip()
    # Ticket #143 requires the not-legal-advice note next to the sources.
    assert "not legal advice" in raw["disclaimer"].lower()
    assert "ej juridisk rådgivning" in raw["disclaimer"]
    assert len(raw["roles"]) >= MIN_ROLES
    ids = [role["id"] for role in raw["roles"]]
    assert len(set(ids)) == len(ids)


def test_every_persona_has_checklist_with_rule_hints():
    raw = load_books()
    for role in raw["roles"]:
        for key in ("id", "label", "description", "errand", "errand_en",
                    "goal", "af_sections", "vocabulary", "checklist"):
            assert role[key], f"{role['id']}: empty {key}"
        assert len(role["checklist"]) >= MIN_CHECKLIST_ITEMS
        seen = set()
        for item in role["checklist"]:
            assert set(item) == CHECKLIST_KEYS, role["id"]
            assert item["say"].strip(), role["id"]
            assert item["why"].strip(), role["id"]
            assert len(item["why"]) <= MAX_RULE_HINT_LEN, role["id"]
            assert item["say"] not in seen, f"{role['id']}: dup say"
            seen.add(item["say"])
            url = item["source_url"]
            assert url == "UNVERIFIED" or url.startswith("https://"), role["id"]
            # Convention: UNVERIFIED source must say so in the hint, and
            # only then.
            assert (url == "UNVERIFIED") == item["why"].startswith("UNVERIFIED")


def test_persona_sections_and_words_grounded_in_seed():
    books, seeds = load_books(), load_seeds()
    node_ids = {n["id"] for a in seeds["authorities"] for n in seed_nodes(a)}
    utterances = {u.lower() for a in seeds["authorities"]
                  for n in seed_nodes(a)
                  for u in n.get("candidate_utterances", [])}
    for role in books["roles"]:
        for section in role["af_sections"]:
            assert section in node_ids, f"{role['id']}: {section}"
        for word in role["vocabulary"]:
            assert word.lower() in utterances or word in TRANSCRIPT_WORDS, (
                f"{role['id']}: {word!r} grounded nowhere")


# --- target seeds: AF menu vocabulary (#40 acceptance) ---


def test_seed_top_level_schema_and_evidence_policy():
    raw = load_seeds()
    assert raw["schema_version"] == "1.0"
    assert raw["model"] == "target_seed"
    policy = raw["evidence_policy"]
    assert policy["target_seed_is_observation"] is False
    assert policy["observed_model_location"].strip()
    assert policy["status_values"] == ["publicly_documented",
                                       "website_taxonomy",
                                       "candidate_only"]
    assert "test call" in policy["rule"]
    assert raw["sources"] and raw["authorities"]


def test_seed_sources_have_ids_urls_titles():
    raw = load_seeds()
    ids = [s["id"] for s in raw["sources"]]
    assert len(set(ids)) == len(ids)
    for source in raw["sources"]:
        assert source["id"].strip()
        assert source["url"].startswith("https://")
        assert source["title"].strip()


def test_seed_authorities_have_phone_facts_and_trees():
    raw = load_seeds()
    known = {s["id"] for s in raw["sources"]}
    allowed = set(raw["evidence_policy"]["status_values"])
    seen_ids = set()
    for authority in raw["authorities"]:
        for key in ("id", "name", "scope", "phone_facts", "sources", "tree"):
            assert authority[key], authority.get("id")
        facts = authority["phone_facts"]
        assert facts["status"] in allowed
        assert facts["summary"].strip()
        for source_id in authority["sources"]:
            assert source_id in known, authority["id"]
        for node in seed_nodes(authority):
            assert node["id"] and node["label"] and node["kind"]
            assert node["id"] not in seen_ids, node["id"]
            seen_ids.add(node["id"])
            assert node["status"] in allowed, node["id"]
            for source_id in node["source_ids"]:
                assert source_id in known, node["id"]
            for utterance in node.get("candidate_utterances", []):
                assert utterance.strip(), node["id"]


def test_af_section_quotes_phone_facts():
    raw = load_seeds()
    af = next(a for a in raw["authorities"]
              if a["id"] == "arbetsformedlingen")
    assert "När du ringer oss" in af["phone_facts"]["summary"]
    assert af["phone_facts"]["status"] == "publicly_documented"
    af_ids = {n["id"] for n in seed_nodes(af)}
    assert {"af.unemployed", "af.support", "af.personal_case"} <= af_ids
