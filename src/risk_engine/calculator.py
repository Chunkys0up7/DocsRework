"""
Risk Score Calculator with ML-based ranking
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCalculator:
    """Calculate and rank risks with ML-based enhancements"""

    # Risk level thresholds
    THRESHOLDS = {
        RiskLevel.CRITICAL: 17,
        RiskLevel.HIGH: 10,
        RiskLevel.MEDIUM: 5,
        RiskLevel.LOW: 1,
    }

    @staticmethod
    def calculate_inherent_risk(likelihood: int, impact: int) -> Tuple[float, RiskLevel]:
        """
        Calculate inherent risk score

        Args:
            likelihood: Likelihood score (1-5)
            impact: Impact score (1-5)

        Returns:
            Tuple of (risk_score, risk_level)
        """
        if not (1 <= likelihood <= 5 and 1 <= impact <= 5):
            raise ValueError("Likelihood and impact must be between 1 and 5")

        score = likelihood * impact

        # Determine risk level
        if score >= RiskCalculator.THRESHOLDS[RiskLevel.CRITICAL]:
            level = RiskLevel.CRITICAL
        elif score >= RiskCalculator.THRESHOLDS[RiskLevel.HIGH]:
            level = RiskLevel.HIGH
        elif score >= RiskCalculator.THRESHOLDS[RiskLevel.MEDIUM]:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return score, level

    @staticmethod
    def calculate_residual_risk(
        inherent_score: float,
        controls: List[Dict[str, Any]]
    ) -> Tuple[float, RiskLevel]:
        """
        Calculate residual risk after applying controls

        Args:
            inherent_score: Inherent risk score
            controls: List of controls with effectiveness ratings

        Returns:
            Tuple of (residual_score, risk_level)
        """
        if not controls:
            return inherent_score, RiskCalculator._get_risk_level(inherent_score)

        # Calculate weighted average control effectiveness
        total_effectiveness = sum(c.get("effectiveness", 0) for c in controls)
        avg_effectiveness = total_effectiveness / len(controls) if controls else 0

        # Apply diminishing returns for multiple controls
        # Using logarithmic scale to avoid over-mitigation
        import math
        mitigation_factor = 1 - (avg_effectiveness / 100) * (1 - math.exp(-len(controls) / 3))

        residual_score = inherent_score * mitigation_factor

        level = RiskCalculator._get_risk_level(residual_score)

        return round(residual_score, 2), level

    @staticmethod
    def _get_risk_level(score: float) -> RiskLevel:
        """Determine risk level from score"""
        if score >= RiskCalculator.THRESHOLDS[RiskLevel.CRITICAL]:
            return RiskLevel.CRITICAL
        elif score >= RiskCalculator.THRESHOLDS[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        elif score >= RiskCalculator.THRESHOLDS[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    @staticmethod
    def calculate_control_adequacy(
        risk_score: float,
        risk_level: RiskLevel,
        controls: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess if controls are adequate for the risk level

        Args:
            risk_score: Risk score
            risk_level: Risk level
            controls: List of controls

        Returns:
            Dictionary with adequacy assessment
        """
        if not controls:
            return {
                "adequate": False,
                "reason": "No controls defined",
                "recommended_effectiveness": 80,
                "current_effectiveness": 0
            }

        avg_effectiveness = sum(c.get("effectiveness", 0) for c in controls) / len(controls)

        # Define minimum effectiveness by risk level
        min_effectiveness = {
            RiskLevel.CRITICAL: 90,
            RiskLevel.HIGH: 80,
            RiskLevel.MEDIUM: 70,
            RiskLevel.LOW: 60,
        }

        required = min_effectiveness[risk_level]
        adequate = avg_effectiveness >= required

        return {
            "adequate": adequate,
            "current_effectiveness": round(avg_effectiveness, 2),
            "required_effectiveness": required,
            "gap": max(0, required - avg_effectiveness),
            "control_count": len(controls),
            "recommendation": RiskCalculator._get_control_recommendation(
                risk_level, avg_effectiveness, len(controls)
            )
        }

    @staticmethod
    def _get_control_recommendation(
        risk_level: RiskLevel,
        effectiveness: float,
        control_count: int
    ) -> str:
        """Generate recommendation for control improvements"""
        if risk_level == RiskLevel.CRITICAL and effectiveness < 90:
            return "Critical risk requires additional high-effectiveness controls"
        elif risk_level == RiskLevel.HIGH and effectiveness < 80:
            return "High risk needs stronger controls or additional preventive measures"
        elif control_count < 2 and risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return "Consider implementing multiple controls for defense in depth"
        elif effectiveness >= 95:
            return "Controls are adequate, maintain regular testing"
        else:
            return "Controls meet minimum requirements, consider optimization"

    @staticmethod
    def aggregate_workflow_risk(
        component_risks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate risk scores from workflow components

        Args:
            component_risks: List of risk dictionaries from components

        Returns:
            Aggregated risk assessment
        """
        if not component_risks:
            return {
                "total_score": 0,
                "max_score": 0,
                "avg_score": 0,
                "risk_level": RiskLevel.LOW,
                "risk_count": 0
            }

        scores = [r.get("residual_score", r.get("inherent_score", 0)) for r in component_risks]

        total_score = sum(scores)
        max_score = max(scores)
        avg_score = total_score / len(scores)

        # Use maximum risk level for workflow classification
        level = RiskCalculator._get_risk_level(max_score)

        return {
            "total_score": round(total_score, 2),
            "max_score": round(max_score, 2),
            "avg_score": round(avg_score, 2),
            "risk_level": level.value,
            "risk_count": len(component_risks),
            "critical_risks": sum(1 for s in scores if s >= 17),
            "high_risks": sum(1 for s in scores if 10 <= s < 17),
            "medium_risks": sum(1 for s in scores if 5 <= s < 10),
            "low_risks": sum(1 for s in scores if s < 5)
        }

    @staticmethod
    def rank_risks(risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank risks by priority considering multiple factors

        Args:
            risks: List of risk dictionaries

        Returns:
            Sorted list of risks with priority scores
        """
        for risk in risks:
            # Calculate priority score considering:
            # - Residual risk score (50%)
            # - Control adequacy (30%)
            # - Time since last review (20%)

            residual_score = risk.get("residual_score", risk.get("inherent_score", 0))

            # Control adequacy factor
            controls = risk.get("controls", [])
            adequacy = RiskCalculator.calculate_control_adequacy(
                residual_score,
                RiskCalculator._get_risk_level(residual_score),
                controls
            )
            control_factor = 0 if adequacy["adequate"] else adequacy["gap"] / 100

            # Time since review factor (simplified)
            last_reviewed = risk.get("reviewSchedule", {}).get("lastReviewed")
            time_factor = 0.5 if not last_reviewed else 0  # Simplified

            # Combined priority score
            priority_score = (
                residual_score * 0.5 +
                control_factor * 30 +
                time_factor * 20
            )

            risk["priority_score"] = round(priority_score, 2)
            risk["rank_factors"] = {
                "residual_risk": residual_score,
                "control_gap": control_factor,
                "review_overdue": time_factor
            }

        # Sort by priority score descending
        return sorted(risks, key=lambda r: r["priority_score"], reverse=True)


def calculate_risk_trends(
    historical_scores: List[Tuple[datetime, float]]
) -> Dict[str, Any]:
    """
    Analyze risk trends over time (ML-ready)

    Args:
        historical_scores: List of (timestamp, score) tuples

    Returns:
        Trend analysis
    """
    if len(historical_scores) < 2:
        return {
            "trend": "insufficient_data",
            "direction": "stable",
            "change_rate": 0
        }

    # Sort by timestamp
    sorted_scores = sorted(historical_scores, key=lambda x: x[0])

    # Calculate simple linear trend
    scores = [s[1] for s in sorted_scores]
    n = len(scores)

    # Simple moving average trend
    recent_avg = sum(scores[-3:]) / min(3, n)
    older_avg = sum(scores[:3]) / min(3, n)

    change = recent_avg - older_avg
    change_rate = (change / older_avg * 100) if older_avg > 0 else 0

    if change > 1:
        direction = "increasing"
    elif change < -1:
        direction = "decreasing"
    else:
        direction = "stable"

    return {
        "trend": direction,
        "direction": direction,
        "change_rate": round(change_rate, 2),
        "recent_average": round(recent_avg, 2),
        "historical_average": round(older_avg, 2),
        "data_points": n
    }
