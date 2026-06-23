"""Core engine for local, peer-to-peer bid comparison."""

from .config import EnterpriseConfig
from .pipeline import compare_bidder_files

__all__ = ["EnterpriseConfig", "compare_bidder_files"]
