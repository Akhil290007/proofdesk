"""proofdesk: a claim-to-proof register for creators who fact-check before they publish."""

from .register import Claim, Register, STATUSES, ValidationIssue

__all__ = ["Claim", "Register", "STATUSES", "ValidationIssue"]
__version__ = "0.1.0"
