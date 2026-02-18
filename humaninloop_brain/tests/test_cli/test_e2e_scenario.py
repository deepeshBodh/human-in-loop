"""End-to-end walkthrough: Scenario 1 (skip enrichment) through CLI.

Walks through a complete /specify workflow pass where enrichment is skipped
because the user provided detailed input. Demonstrates DAG flexibility.
"""

import json
from pathlib import Path

from humaninloop_brain.cli.main import main

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
CATALOG = str(FIXTURES_DIR / "specify-catalog.json")


class TestScenario1SkipEnrichment:
    """Full Scenario 1: constitution-gate -> analyst -> advocate."""

    def test_full_walkthrough(self, tmp_path, capsys):
        dag_path = str(tmp_path / "dag.json")

        # Step 1: Create pass
        code = main(["create", "specify-feature-auth", "--pass", "1", "--output", dag_path])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "success"

        # Step 2: Validate catalog
        code = main(["catalog-validate", CATALOG])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

        # Step 3: Assemble constitution-gate (skip enrichment — detailed input)
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"] == "constitution-gate"

        # Step 4: Assemble analyst-review
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"] == "analyst-review"

        # Step 5: Update analyst status to completed
        code = main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

        # Step 6: Assemble advocate-review (gate)
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"] == "advocate-review"
        # Should have inferred edges from analyst produces -> advocate consumes
        assert out["edges_inferred"] > 0

        # Step 7: Topological sort
        code = main(["sort", dag_path])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        order = out["order"]
        # Constitution gate and analyst before advocate
        assert order.index("advocate-review") > order.index("analyst-review")

        # Step 8: Validate the assembled DAG
        code = main(["validate", dag_path, "--catalog", CATALOG])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

        # Step 9: Freeze the pass
        code = main([
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "advocate-verdict-ready",
            "--rationale", "Advocate approved specification",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True

        # Step 10: Verify frozen pass validates
        code = main(["validate", dag_path, "--catalog", CATALOG])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

        # Verify the final DAG structure
        dag_data = json.loads(Path(dag_path).read_text())
        assert dag_data["outcome"] == "completed"
        assert len(dag_data["nodes"]) == 3
        node_ids = {n["id"] for n in dag_data["nodes"]}
        assert node_ids == {"constitution-gate", "analyst-review", "advocate-review"}
        assert "input-enrichment" not in node_ids  # Enrichment was skipped
