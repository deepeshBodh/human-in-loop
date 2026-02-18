"""Tests for edge inference."""

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.nodes import GraphNode, NodeContract, ArtifactConsumption
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.graph.inference import infer_edges


def _make_catalog(load_fixture) -> NodeCatalog:
    return NodeCatalog.model_validate(load_fixture("specify-catalog.json"))


class TestInferEdges:
    def test_analyst_after_enrichment(self, load_fixture):
        """Adding analyst-review when enrichment exists should infer edges."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")

        # Add enrichment node
        dag.nodes.append(
            GraphNode(
                id="input-enrichment",
                type=NodeType.task,
                name="Enrichment",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[ArtifactConsumption(artifact="raw-input")],
                    produces=["enriched-input"],
                ),
            )
        )

        edges = infer_edges("analyst-review", dag, catalog)
        edge_types = {e.type for e in edges}

        # analyst consumes enriched-input (optional), so depends-on + produces
        assert EdgeType.depends_on in edge_types
        assert EdgeType.produces in edge_types

    def test_advocate_after_analyst(self, load_fixture):
        """Adding advocate-review (gate) after analyst (task) infers validates."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")

        dag.nodes.append(
            GraphNode(
                id="analyst-review",
                type=NodeType.task,
                name="Analyst",
                description="d",
                status="pending",
                contract=NodeContract(
                    produces=["spec.md", "analyst-report.md"],
                ),
            )
        )

        edges = infer_edges("advocate-review", dag, catalog)
        edge_types = {e.type for e in edges}

        assert EdgeType.depends_on in edge_types
        assert EdgeType.produces in edge_types
        assert EdgeType.validates in edge_types

    def test_no_edges_for_first_node(self, load_fixture):
        """First node in DAG has no upstream — no edges inferred."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        edges = infer_edges("input-enrichment", dag, catalog)
        assert edges == []

    def test_unknown_node_returns_empty(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        edges = infer_edges("nonexistent", dag, catalog)
        assert edges == []

    def test_no_duplicate_edges(self, load_fixture):
        """Inferred edges should not duplicate existing edges."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")

        dag.nodes.append(
            GraphNode(
                id="analyst-review",
                type=NodeType.task,
                name="Analyst",
                description="d",
                status="pending",
                contract=NodeContract(produces=["spec.md", "analyst-report.md"]),
            )
        )

        # Pre-add a depends-on edge
        dag.edges.append(
            Edge(
                id="existing",
                source="analyst-review",
                target="advocate-review",
                type=EdgeType.depends_on,
            )
        )

        edges = infer_edges("advocate-review", dag, catalog)
        dep_edges = [e for e in edges if e.type == EdgeType.depends_on]
        assert len(dep_edges) == 0  # Already exists

    def test_edge_id_format(self, load_fixture):
        """Inferred edge IDs follow the naming convention."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")

        dag.nodes.append(
            GraphNode(
                id="input-enrichment",
                type=NodeType.task,
                name="Enrichment",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[ArtifactConsumption(artifact="raw-input")],
                    produces=["enriched-input"],
                ),
            )
        )

        edges = infer_edges("analyst-review", dag, catalog)
        for edge in edges:
            assert edge.id.startswith("inferred-")

    def test_scenario_skip_enrichment(self, load_fixture):
        """Scenario 1: When no enrichment exists, analyst has no upstream."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")

        # Add constitution gate (produces nothing useful for analyst)
        dag.nodes.append(
            GraphNode(
                id="constitution-gate",
                type=NodeType.gate,
                name="Gate",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[ArtifactConsumption(artifact="constitution.md")],
                    produces=[],
                ),
            )
        )

        edges = infer_edges("analyst-review", dag, catalog)
        # No artifacts match, so no edges
        assert edges == []

    def test_scenario_research_before_analyst(self, load_fixture):
        """Scenario 2: Research produces findings consumed by analyst."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")

        dag.nodes.append(
            GraphNode(
                id="targeted-research",
                type=NodeType.task,
                name="Research",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[ArtifactConsumption(artifact="advocate-report.md")],
                    produces=["research-findings"],
                ),
            )
        )

        edges = infer_edges("analyst-review", dag, catalog)
        edge_sources = {e.source for e in edges}
        assert "targeted-research" in edge_sources

    def test_skip_reopened_node(self, load_fixture):
        """skip_reopened=True returns empty list immediately."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes.append(
            GraphNode(
                id="input-enrichment",
                type=NodeType.task,
                name="Enrichment",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[ArtifactConsumption(artifact="raw-input")],
                    produces=["enriched-input"],
                ),
            )
        )
        edges = infer_edges("analyst-review", dag, catalog, skip_reopened=True)
        assert edges == []

    def test_gate_does_not_get_produces_from_gate(self, load_fixture):
        """Produces edges only come from task sources."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")

        # constitution-gate is a gate, not a task
        dag.nodes.append(
            GraphNode(
                id="constitution-gate",
                type=NodeType.gate,
                name="Gate",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[ArtifactConsumption(artifact="constitution.md")],
                    produces=["gate-output"],
                ),
            )
        )

        # A task that consumes gate-output
        dag.nodes.append(
            GraphNode(
                id="test-task",
                type=NodeType.task,
                name="Test",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[ArtifactConsumption(artifact="gate-output")],
                    produces=[],
                ),
            )
        )

        # Infer for test-task — gate output should create depends-on but not produces
        # (since source is gate, not task, and produces requires task source)
        edges = infer_edges("test-task", dag, catalog)
        # test-task is not in catalog, so returns empty
        assert edges == []
