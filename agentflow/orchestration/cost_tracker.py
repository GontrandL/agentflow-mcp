"""
Cost Tracker for Waterfall Escalation System

Tracks costs across FREE, Mid-Tier, and Premium tiers with detailed metrics.
"""

from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TierUsage:
    """Usage statistics for a single tier"""
    tier: str
    tokens: int = 0
    cost: float = 0.0
    calls: int = 0
    success_rate: float = 0.0


@dataclass
class CostSummary:
    """Complete cost summary across all tiers"""
    total_cost: float
    total_tokens: int
    total_calls: int
    tier_breakdown: Dict[str, TierUsage]
    timestamp: datetime = field(default_factory=datetime.now)


class CostTracker:
    """
    Tracks and analyzes costs across the waterfall escalation tiers.

    Tier costs:
    - FREE: $0 (Qwen3 Coder, DeepSeek R1)
    - Mid: $0.14/M tokens (DeepSeek V3)
    - Premium: $3/M tokens (Claude Sonnet 4)
    """

    def __init__(self):
        """Initialize cost tracker with tier pricing"""
        self.costs_per_1m = {
            "free": 0.0,
            "mid": 0.14,
            "premium": 3.0
        }

        self.tier_usage: Dict[str, TierUsage] = {
            "free": TierUsage(tier="free"),
            "mid": TierUsage(tier="mid"),
            "premium": TierUsage(tier="premium")
        }

        self.total_cost = 0.0
        self.total_tokens = 0
        self.total_calls = 0

    def track(self, tier: str, tokens: int, success: bool = True) -> float:
        """
        Track usage for a specific tier

        Args:
            tier: Tier name ("free", "mid", "premium")
            tokens: Number of tokens used
            success: Whether the call succeeded

        Returns:
            Cost for this specific call
        """
        if tier not in self.costs_per_1m:
            raise ValueError(f"Unknown tier: {tier}. Must be free, mid, or premium")

        # Calculate cost
        cost_per_1k = self.costs_per_1m[tier] / 1000
        cost = (tokens / 1000) * cost_per_1k

        # Update tier usage
        usage = self.tier_usage[tier]
        usage.tokens += tokens
        usage.cost += cost
        usage.calls += 1

        # Update success rate
        if usage.calls > 0:
            successful_calls = int(usage.success_rate * (usage.calls - 1))
            if success:
                successful_calls += 1
            usage.success_rate = successful_calls / usage.calls

        # Update totals
        self.total_cost += cost
        self.total_tokens += tokens
        self.total_calls += 1

        return cost

    def get_tier_summary(self, tier: str) -> TierUsage:
        """Get usage summary for a specific tier"""
        if tier not in self.tier_usage:
            raise ValueError(f"Unknown tier: {tier}")
        return self.tier_usage[tier]

    def get_summary(self) -> CostSummary:
        """Get complete cost summary"""
        return CostSummary(
            total_cost=self.total_cost,
            total_tokens=self.total_tokens,
            total_calls=self.total_calls,
            tier_breakdown=self.tier_usage.copy()
        )

    def reset(self):
        """Reset all tracking data"""
        for tier in self.tier_usage.values():
            tier.tokens = 0
            tier.cost = 0.0
            tier.calls = 0
            tier.success_rate = 0.0

        self.total_cost = 0.0
        self.total_tokens = 0
        self.total_calls = 0

    def get_savings_vs_direct(self, direct_tier: str = "premium") -> Dict:
        """
        Calculate savings compared to using a direct tier for all calls

        Args:
            direct_tier: Tier to compare against (usually "premium")

        Returns:
            Dictionary with savings analysis
        """
        # Calculate what it would have cost using direct tier
        direct_cost_per_1k = self.costs_per_1m[direct_tier] / 1000
        direct_total_cost = (self.total_tokens / 1000) * direct_cost_per_1k

        # Calculate savings
        savings_amount = direct_total_cost - self.total_cost
        savings_percent = (savings_amount / direct_total_cost * 100) if direct_total_cost > 0 else 0

        return {
            "waterfall_cost": self.total_cost,
            "direct_cost": direct_total_cost,
            "savings_amount": savings_amount,
            "savings_percent": savings_percent,
            "total_tokens": self.total_tokens,
            "total_calls": self.total_calls
        }

    def print_summary(self):
        """Print formatted cost summary"""
        summary = self.get_summary()
        savings = self.get_savings_vs_direct()

        print("\n" + "="*60)
        print("WATERFALL COST SUMMARY")
        print("="*60)
        print(f"\nTotal Cost: ${summary.total_cost:.4f}")
        print(f"Total Tokens: {summary.total_tokens:,}")
        print(f"Total Calls: {summary.total_calls}")

        print("\nTier Breakdown:")
        print("-" * 60)
        for tier, usage in summary.tier_breakdown.items():
            if usage.calls > 0:
                print(f"\n{tier.upper()} Tier:")
                print(f"  Calls: {usage.calls}")
                print(f"  Tokens: {usage.tokens:,}")
                print(f"  Cost: ${usage.cost:.4f}")
                print(f"  Success Rate: {usage.success_rate * 100:.1f}%")

        print("\nSavings Analysis:")
        print("-" * 60)
        print(f"Waterfall Cost: ${savings['waterfall_cost']:.4f}")
        print(f"Direct Premium Cost: ${savings['direct_cost']:.4f}")
        print(f"Savings: ${savings['savings_amount']:.4f} ({savings['savings_percent']:.1f}%)")
        print("="*60 + "\n")


if __name__ == "__main__":
    # Example usage
    tracker = CostTracker()

    # Simulate some usage
    tracker.track("free", 50000, success=True)   # FREE tier attempt
    tracker.track("free", 30000, success=False)  # FREE tier retry
    tracker.track("mid", 40000, success=True)    # Escalated to mid
    tracker.track("premium", 60000, success=True) # Escalated to premium

    # Print summary
    tracker.print_summary()
