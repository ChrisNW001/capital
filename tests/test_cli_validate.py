"""Tests for the validate CLI command."""

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from pitchdeck.cli import app

runner = CliRunner()


class TestValidateCLIFileHandling:
    def test_file_not_found_exits_1(self):
        result = runner.invoke(
            app, ["validate", "nonexistent.json", "--skip-llm"]
        )
        assert result.exit_code == 1
        assert "File not found" in result.output

    def test_invalid_json_schema_exits_1(self, tmp_path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text('{"company_name": "X"}')
        result = runner.invoke(
            app, ["validate", str(bad_json), "--skip-llm"]
        )
        assert result.exit_code == 1
        assert "Invalid deck JSON schema" in result.output

    def test_corrupted_file_exits_1(self, tmp_path):
        bad_file = tmp_path / "corrupt.json"
        bad_file.write_text("not json at all {{{")
        result = runner.invoke(
            app, ["validate", str(bad_file), "--skip-llm"]
        )
        assert result.exit_code == 1
        assert "FAIL" in result.output


class TestValidateCLIApiKey:
    def test_missing_api_key_without_skip_llm_exits_1(
        self, sample_deck_json
    ):
        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(
                app, ["validate", str(sample_deck_json)]
            )
        assert result.exit_code == 1
        assert "ANTHROPIC_API_KEY" in result.output


class TestValidateCLIRuleBased:
    def test_skip_llm_succeeds(self, sample_deck_json, tmp_path):
        report_path = tmp_path / "report.md"
        result = runner.invoke(app, [
            "validate", str(sample_deck_json),
            "--skip-llm",
            "--output", str(report_path),
        ])
        assert result.exit_code == 0
        assert "Overall Score" in result.output
        assert report_path.exists()

    def test_skip_llm_prints_pass_or_fail(self, sample_deck_json, tmp_path):
        result = runner.invoke(app, [
            "validate", str(sample_deck_json),
            "--skip-llm",
            "--output", str(tmp_path / "report.md"),
        ])
        assert result.exit_code == 0
        assert "PASS" in result.output or "FAIL" in result.output

    def test_custom_threshold(self, sample_deck_json, tmp_path):
        result = runner.invoke(app, [
            "validate", str(sample_deck_json),
            "--skip-llm",
            "--threshold", "95",
            "--output", str(tmp_path / "report.md"),
        ])
        assert result.exit_code == 0
        # A 95 threshold on a synthetic deck should produce FAIL
        assert "FAIL" in result.output

    def test_vc_checks_shown(self, sample_deck_json, tmp_path):
        result = runner.invoke(app, [
            "validate", str(sample_deck_json),
            "--skip-llm",
            "--output", str(tmp_path / "report.md"),
        ])
        assert result.exit_code == 0
        assert "VC Checks" in result.output

    def test_improvements_shown(self, sample_deck_json, tmp_path):
        result = runner.invoke(app, [
            "validate", str(sample_deck_json),
            "--skip-llm",
            "--output", str(tmp_path / "report.md"),
        ])
        assert result.exit_code == 0
        assert "Top Improvements" in result.output

    def test_report_saved_message(self, sample_deck_json, tmp_path):
        report_path = tmp_path / "report.md"
        result = runner.invoke(app, [
            "validate", str(sample_deck_json),
            "--skip-llm",
            "--output", str(report_path),
        ])
        assert result.exit_code == 0
        assert "Report saved to" in result.output


class TestValidateCLIProfileErrors:
    def test_unknown_profile_exits_1(self, sample_deck_json):
        result = runner.invoke(app, [
            "validate", str(sample_deck_json),
            "--vc", "nonexistent-vc-profile",
            "--skip-llm",
        ])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestValidateCLISaveErrors:
    def test_report_save_failure_exits_1(self, sample_deck_json, tmp_path):
        """When save_validation_report raises OSError, command exits non-zero."""
        with patch(
            "pitchdeck.output.save_validation_report",
            side_effect=OSError("Permission denied"),
        ):
            result = runner.invoke(app, [
                "validate", str(sample_deck_json),
                "--skip-llm",
                "--output", str(tmp_path / "report.md"),
            ])
        assert result.exit_code == 1
        assert "Failed to save report" in result.output


class TestGenerateCLISaveErrors:
    def test_save_markdown_failure_exits_1(self, tmp_path):
        """When save_markdown raises OSError, generate command exits non-zero."""
        mock_deck = MagicMock()
        mock_deck.slides = []
        mock_deck.gaps_identified = []
        mock_deck.model_dump_json.return_value = "{}"

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("pitchdeck.parsers.extract_document", return_value="text"):
                with patch("pitchdeck.profiles.load_vc_profile") as mock_profile:
                    mock_profile.return_value = MagicMock(
                        name="VC", thesis_points=["x"],
                    )
                    with patch("pitchdeck.engine.narrative.generate_deck", return_value=mock_deck):
                        with patch(
                            "pitchdeck.output.save_markdown",
                            side_effect=OSError("Disk full"),
                        ):
                            input_file = tmp_path / "doc.pdf"
                            input_file.write_text("dummy")
                            result = runner.invoke(app, [
                                "generate", str(input_file),
                                "--output", str(tmp_path / "deck.md"),
                                "--skip-gaps",
                            ])
        assert result.exit_code == 1
        assert "Failed to save deck" in result.output

    def test_save_json_failure_exits_1(self, tmp_path):
        """When model_dump_json raises OSError, generate command exits non-zero."""
        mock_deck = MagicMock()
        mock_deck.slides = []
        mock_deck.gaps_identified = []
        mock_deck.model_dump_json.side_effect = OSError("Disk full")

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch("pitchdeck.parsers.extract_document", return_value="text"):
                with patch("pitchdeck.profiles.load_vc_profile") as mock_profile:
                    mock_profile.return_value = MagicMock(
                        name="VC", thesis_points=["x"],
                    )
                    with patch("pitchdeck.engine.narrative.generate_deck", return_value=mock_deck):
                        with patch("pitchdeck.output.save_markdown"):
                            input_file = tmp_path / "doc.pdf"
                            input_file.write_text("dummy")
                            result = runner.invoke(app, [
                                "generate", str(input_file),
                                "--output", str(tmp_path / "deck.md"),
                                "--skip-gaps",
                            ])
        assert result.exit_code == 1
        assert "Failed to save JSON" in result.output
