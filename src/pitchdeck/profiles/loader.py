"""YAML-based VC profile loader with Pydantic validation."""

from pathlib import Path
from typing import Optional

from ruamel.yaml import YAML

from pitchdeck.models import ProfileNotFoundError, VCProfile

PROFILES_DIR = Path(__file__).parent.parent.parent.parent / "profiles"


def load_vc_profile(
    name: str, profiles_dir: Optional[Path] = None
) -> VCProfile:
    """Load a VC profile from YAML config.

    Searches for {name}.yaml in the profiles directory.
    """
    search_dir = profiles_dir or PROFILES_DIR
    profile_path = search_dir / f"{name}.yaml"
    if not profile_path.exists():
        available = [p.stem for p in search_dir.glob("*.yaml")]
        raise ProfileNotFoundError(
            f"Profile '{name}' not found. Available: {', '.join(available)}"
        )
    yaml = YAML()
    with open(profile_path) as f:
        raw = yaml.load(f)
    return VCProfile(**raw)


def list_profiles(profiles_dir: Optional[Path] = None) -> list[str]:
    """List available VC profile names."""
    search_dir = profiles_dir or PROFILES_DIR
    return sorted(p.stem for p in search_dir.glob("*.yaml"))
