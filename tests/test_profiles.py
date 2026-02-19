"""Tests for VC profile loading."""

import pytest
from ruamel.yaml import YAML

from pitchdeck.models import ProfileNotFoundError
from pitchdeck.profiles.loader import list_profiles, load_vc_profile


class TestLoadVCProfile:
    def test_load_valid_profile(self, sample_vc_yaml):
        profile = load_vc_profile("testvc", profiles_dir=sample_vc_yaml)
        assert profile.name == "Test VC"
        assert profile.fund_name == "Fund I"
        assert "seed" in profile.stage_focus

    def test_profile_not_found(self, tmp_path):
        with pytest.raises(ProfileNotFoundError, match="not found"):
            load_vc_profile("nonexistent", profiles_dir=tmp_path)

    def test_available_profiles_in_error(self, sample_vc_yaml):
        with pytest.raises(ProfileNotFoundError, match="testvc"):
            load_vc_profile("missing", profiles_dir=sample_vc_yaml)

    def test_pydantic_validation_on_load(self, sample_vc_yaml):
        profile = load_vc_profile("testvc", profiles_dir=sample_vc_yaml)
        assert profile.deck_preferences.preferred_slide_count == 15
        assert "cover" in profile.deck_preferences.must_include_slides

    def test_load_earlybird_profile(self):
        """Integration test: load the actual earlybird profile."""
        from pathlib import Path

        profiles_dir = (
            Path(__file__).parent.parent / "profiles"
        )
        profile = load_vc_profile("earlybird", profiles_dir=profiles_dir)
        assert profile.name == "Earlybird Capital"
        assert len(profile.thesis_points) == 7
        assert len(profile.deck_preferences.must_include_slides) == 15


class TestListProfiles:
    def test_list_profiles(self, sample_vc_yaml):
        profiles = list_profiles(profiles_dir=sample_vc_yaml)
        assert profiles == ["testvc"]

    def test_list_empty_dir(self, tmp_path):
        profiles = list_profiles(profiles_dir=tmp_path)
        assert profiles == []

    def test_list_multiple_profiles(self, tmp_path):
        yaml = YAML()
        for name in ["alpha", "beta", "charlie"]:
            data = {
                "name": name,
                "fund_name": "Fund",
                "stage_focus": ["seed"],
                "sector_focus": ["ai"],
                "geo_focus": ["EU"],
                "thesis_points": ["test"],
            }
            with open(tmp_path / f"{name}.yaml", "w") as f:
                yaml.dump(data, f)
        profiles = list_profiles(profiles_dir=tmp_path)
        assert profiles == ["alpha", "beta", "charlie"]
