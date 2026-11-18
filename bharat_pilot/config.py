"""
Configuration and Profile Management for BharatPilot.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


def load_env_file():
    """Load environment variables from standard paths."""
    paths = [
        Path.cwd() / ".env",
        Path.home() / ".config" / "bharat-pilot" / ".env",
        Path.home() / ".hermes" / ".env",
    ]
    for p in paths:
        if p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k and k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass


load_env_file()


@dataclass
class UserProfile:
    """Default passenger & citizen profile for 1-click auto-fill."""
    full_name: str = "Shubhransh Gupta"
    age: int = 28
    gender: str = "Male"
    email: str = "shubhransh@example.com"
    phone: str = "+91 98765 43210"
    pan_number: str = "ABCDE1234F"
    uan_number: str = "101234567890"
    meal_preference: str = "Veg"
    seat_preference: str = "Window"
    berth_preference: str = "Lower"


@dataclass
class BharatConfig:
    """Global configuration for BharatPilot."""
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    profile: UserProfile = field(default_factory=UserProfile)
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "bharat_outputs")
    web_host: str = "127.0.0.1"
    web_port: int = 8501

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
