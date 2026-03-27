"""Specification consistency tests — cross-document structural alignment.

Programmatically verifies that the specify-catalog.json, specify.md command,
agent specs, templates, and strategy skills are structurally aligned.

These are NOT runtime tests — they read files and check structural properties.
"""

import json
from pathlib import Path

import pytest

# Root of the repository (4 levels up from this test file)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "humaninloop"
BRAIN_ROOT = REPO_ROOT / "humaninloop_brain"

# Three copies of the catalog
CATALOG_PATHS = [
    PLUGIN_ROOT / "catalogs" / "specify-catalog.json",
    BRAIN_ROOT / "catalogs" / "specify-catalog.json",
    BRAIN_ROOT / "tests" / "fixtures" / "specify-catalog.json",
]

# Agent spec paths
SPECIFY_CMD = PLUGIN_ROOT / "commands" / "specify.md"
STATE_ANALYST = PLUGIN_ROOT / "agents" / "state-analyst.md"
REQUIREMENTS_ANALYST = PLUGIN_ROOT / "agents" / "requirements-analyst.md"
DEVILS_ADVOCATE = PLUGIN_ROOT / "agents" / "devils-advocate.md"

# Strategy skills
STRATEGY_CORE = PLUGIN_ROOT / "skills" / "strategy-core" / "SKILL.md"
STRATEGY_SPEC = PLUGIN_ROOT / "skills" / "strategy-specification" / "SKILL.md"

# Templates
TEMPLATE_DIR = PLUGIN_ROOT / "templates"


def _load_catalog(path: Path) -> dict:
    return json.loads(path.read_text())


def _catalog_node_ids(catalog: dict) -> set[str]:
    return {n["node_id"] for n in catalog["nodes"]}


def _catalog_node_types(catalog: dict) -> dict[str, str]:
    return {n["node_id"]: n["type"] for n in catalog["nodes"]}


def _catalog_node_agents(catalog: dict) -> dict[str, str | None]:
    return {n["node_id"]: n.get("agent") for n in catalog["nodes"]}


def _catalog_artifacts_produced(catalog: dict) -> set[str]:
    """All artifacts produced by any catalog node."""
    artifacts = set()
    for node in catalog["nodes"]:
        for a in node.get("contract", {}).get("produces", []):
            artifacts.add(a)
    return artifacts


def _catalog_artifacts_consumed(catalog: dict) -> set[str]:
    """All artifacts consumed by any catalog node."""
    artifacts = set()
    for node in catalog["nodes"]:
        for c in node.get("contract", {}).get("consumes", []):
            artifacts.add(c["artifact"])
    return artifacts


class TestThreeCatalogCopiesIdentical:
    """All 3 catalog JSON files must be byte-identical."""

    def test_all_three_exist(self):
        for path in CATALOG_PATHS:
            assert path.exists(), f"Missing catalog at {path}"

    def test_byte_identical(self):
        contents = [p.read_bytes() for p in CATALOG_PATHS]
        for i in range(1, len(contents)):
            assert contents[0] == contents[i], (
                f"Catalog at {CATALOG_PATHS[i]} differs from {CATALOG_PATHS[0]}"
            )

    def test_json_parseable(self):
        for path in CATALOG_PATHS:
            data = json.loads(path.read_text())
            assert "nodes" in data
            assert "edge_constraints" in data


class TestSpecifyCatalogConsistency:
    """specify.md routing table covers all catalog node types."""

    @pytest.fixture
    def catalog(self) -> dict:
        return _load_catalog(CATALOG_PATHS[0])

    @pytest.fixture
    def specify_text(self) -> str:
        return SPECIFY_CMD.read_text()

    def test_specify_cmd_exists(self):
        assert SPECIFY_CMD.exists()

    def test_catalog_referenced_in_specify(self, specify_text):
        """specify.md references the catalog path."""
        assert "specify-catalog.json" in specify_text

    def test_routing_table_covers_node_types(self, specify_text, catalog):
        """The routing table covers all 4 node types from the catalog."""
        node_types_in_catalog = {n["type"] for n in catalog["nodes"]}
        for node_type in node_types_in_catalog:
            assert node_type in specify_text, (
                f"Node type '{node_type}' from catalog not found in specify.md routing"
            )

    def test_strategy_skills_delegated_to_analyst(self, specify_text):
        """specify.md delegates strategy skill resolution to the Analyst via workflow identifier."""
        assert "workflow" in specify_text
        assert "Analyst" in specify_text or "analyst" in specify_text

    def test_advocate_verdicts_covered(self, specify_text, catalog):
        """All advocate verdict values from catalog are handled in specify.md."""
        advocate = next(n for n in catalog["nodes"] if n["node_id"] == "advocate-review")
        for verdict in advocate.get("verdict_values", []):
            assert verdict in specify_text, (
                f"Advocate verdict '{verdict}' not handled in specify.md"
            )


class TestStateAnalystAssemblyConsistency:
    """State Analyst spec aligns with catalog contracts, artifacts, and assembly patterns."""

    @pytest.fixture
    def catalog(self) -> dict:
        return _load_catalog(CATALOG_PATHS[0])

    @pytest.fixture
    def analyst_text(self) -> str:
        return STATE_ANALYST.read_text()

    def test_analyst_exists(self):
        assert STATE_ANALYST.exists()

    def test_dag_assembler_removed(self):
        """DAG Assembler agent file should not exist after merge."""
        dag_assembler = PLUGIN_ROOT / "agents" / "dag-assembler.md"
        assert not dag_assembler.exists(), (
            "dag-assembler.md should be deleted — functionality absorbed into State Analyst"
        )

    def test_four_actions_documented(self, analyst_text):
        """State Analyst documents its 4 combined actions."""
        assert "brief-and-assemble" in analyst_text
        assert "parse-and-advance" in analyst_text
        assert "update-and-advance" in analyst_text
        assert "re-brief" in analyst_text

    def test_artifact_path_convention_covers_catalog(self, analyst_text, catalog):
        """Artifact path convention table covers all catalog artifacts."""
        all_artifacts = _catalog_artifacts_produced(catalog) | _catalog_artifacts_consumed(catalog)
        system_artifacts = {"raw-input", "constitution.md"}
        non_system = all_artifacts - system_artifacts

        for artifact in non_system:
            assert artifact in analyst_text, (
                f"Artifact '{artifact}' from catalog not in State Analyst artifact path convention"
            )

    def test_key_node_ids_referenced(self, analyst_text, catalog):
        """Key node IDs from catalog appear in State Analyst prompt patterns."""
        for node_id in ["constitution-gate", "analyst-review", "advocate-review"]:
            assert node_id in analyst_text, (
                f"Key node '{node_id}' not referenced in State Analyst"
            )

    def test_report_parsing_patterns_for_agent_nodes(self, catalog, analyst_text):
        """Report parsing patterns exist in State Analyst for nodes that produce reports."""
        agent_nodes = [n for n in catalog["nodes"] if n.get("agent")]
        for node in agent_nodes:
            for artifact in node["contract"]["produces"]:
                if artifact.endswith(".md"):
                    assert artifact in analyst_text, (
                        f"No report parsing pattern for '{artifact}' "
                        f"produced by '{node['node_id']}' in State Analyst"
                    )

    def test_all_agent_nodes_have_prompt_pattern(self, catalog, analyst_text):
        """Every catalog node with an agent has a NL prompt pattern in State Analyst."""
        agent_nodes = [n for n in catalog["nodes"] if n.get("agent")]
        for node in agent_nodes:
            assert node["node_id"] in analyst_text, (
                f"Node '{node['node_id']}' (agent: {node['agent']}) has no "
                f"NL prompt pattern in State Analyst"
            )

    def test_skill_based_nodes_have_skill_reference(self, catalog, analyst_text):
        """Nodes with skill (no agent) have skill invocation in State Analyst."""
        skill_nodes = [
            n for n in catalog["nodes"]
            if n.get("skill") and not n.get("agent")
        ]
        for node in skill_nodes:
            assert node["skill"] in analyst_text, (
                f"Skill '{node['skill']}' for node '{node['node_id']}' "
                f"not referenced in State Analyst"
            )

    def test_constitution_gate_is_file_check(self, catalog, analyst_text):
        """constitution-gate (no agent) is handled as file-check in State Analyst."""
        const_gate = next(n for n in catalog["nodes"] if n["node_id"] == "constitution-gate")
        assert const_gate.get("agent") is None
        assert "file-check" in analyst_text
        assert "constitution-gate" in analyst_text


class TestStateAnalystCatalogConsistency:
    """State Analyst output fields constructible from catalog schema."""

    @pytest.fixture
    def catalog(self) -> dict:
        return _load_catalog(CATALOG_PATHS[0])

    @pytest.fixture
    def analyst_text(self) -> str:
        return STATE_ANALYST.read_text()

    def test_analyst_exists(self):
        assert STATE_ANALYST.exists()

    def test_viable_nodes_fields_from_catalog(self, analyst_text, catalog):
        """State Analyst output includes contract info that exists in catalog."""
        for field in ["id", "type", "agent", "contract"]:
            assert field in analyst_text

    def test_gap_classification_types(self, analyst_text):
        """State Analyst documents all gap types used in routing."""
        for gap_type in ["knowledge", "preference", "scope"]:
            assert gap_type in analyst_text

    def test_output_fields_documented(self, analyst_text):
        """All required output fields are documented."""
        required_fields = [
            "state_summary",
            "recommendations",
            "relevant_patterns",
            "pass_context",
            "outcome_trajectory",
            "alternatives",
        ]
        for field in required_fields:
            assert field in analyst_text, (
                f"Required output field '{field}' not documented in State Analyst"
            )

    def test_strategy_skills_referenced(self, analyst_text):
        """State Analyst references both strategy skills."""
        assert "strategy-core" in analyst_text
        assert "strategy-specification" in analyst_text

    def test_parse_and_advance_action_documented(self, analyst_text):
        """State Analyst documents parse-and-advance action."""
        assert "parse-and-advance" in analyst_text

    def test_hil_dag_record_referenced(self, analyst_text):
        """State Analyst references hil-dag record for atomic writes."""
        assert "record" in analyst_text

    def test_hil_dag_assemble_referenced(self, analyst_text):
        """State Analyst references hil-dag assemble for node assembly."""
        assert "assemble" in analyst_text

    def test_hil_dag_freeze_referenced(self, analyst_text):
        """State Analyst references hil-dag freeze for pass freezing."""
        assert "freeze" in analyst_text


class TestCatalogTemplateConsistency:
    """Template files exist for referenced artifacts and match report parsing."""

    @pytest.fixture
    def catalog(self) -> dict:
        return _load_catalog(CATALOG_PATHS[0])

    def test_spec_template_exists(self):
        assert (TEMPLATE_DIR / "spec-template.md").exists()

    def test_analyst_report_template_exists(self):
        assert (TEMPLATE_DIR / "analyst-report-template.md").exists()

    def test_advocate_report_template_exists(self):
        assert (TEMPLATE_DIR / "advocate-report-template.md").exists()

    def test_context_template_exists(self):
        assert (TEMPLATE_DIR / "context-template.md").exists()

    def test_analyst_template_has_expected_sections(self):
        """Analyst report template has sections referenced in State Analyst parsing patterns."""
        template = (TEMPLATE_DIR / "analyst-report-template.md").read_text()
        assert "What I Created" in template or "Created" in template
        assert "Summary" in template or "summary" in template.lower()

    def test_advocate_template_has_verdict_section(self):
        """Advocate report template has a verdict section for parsing."""
        template = (TEMPLATE_DIR / "advocate-report-template.md").read_text()
        assert "Verdict" in template or "verdict" in template.lower() or "Status" in template


class TestCrossAgentRoutingCoverage:
    """Every catalog (type, agent) combination has routing in specify.md."""

    @pytest.fixture
    def catalog(self) -> dict:
        return _load_catalog(CATALOG_PATHS[0])

    @pytest.fixture
    def specify_text(self) -> str:
        return SPECIFY_CMD.read_text()

    @pytest.fixture
    def analyst_text(self) -> str:
        return STATE_ANALYST.read_text()

    def test_dispatch_modes_in_routing_table(self, catalog, specify_text):
        """dispatch_mode routing covers all 4 modes in specify.md."""
        for mode in ["agent", "skill", "supervisor-owned", "auto-resolved"]:
            assert mode in specify_text, (
                f"dispatch_mode '{mode}' not in specify.md routing table"
            )

    def test_decision_node_uses_ask_user(self, specify_text):
        """Decision node type routes to AskUserQuestion in specify.md."""
        assert "AskUserQuestion" in specify_text
        assert "decision" in specify_text.lower()

    def test_milestone_node_verifies_artifacts(self, specify_text):
        """Milestone node type verifies required artifacts in specify.md."""
        assert "milestone" in specify_text.lower()

    def test_two_outbound_verbs(self, specify_text):
        """specify.md uses two outbound verbs (not three)."""
        assert "Two Outbound Verbs" in specify_text
        assert "Three Outbound Verbs" not in specify_text
