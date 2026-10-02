"""
TECH-NDS-01 — NDS Worker
Technical Department Employee
Version: 1.1.0
Status: Ready
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from memory.memory_engine import MemoryEngine


class TechNDS01:
    """
    NDS Worker — Technical Department Employee.

    Focus:
    - Market Structure
    - Liquidity
    - NDS concepts
    - Multi-timeframe analysis (H1 → M15 → M5 → M1)
    - Final decision framing always on M1

    Communication:
    - Only with TECH-MANAGER
    """

    IDENTITY = {
        "agent_id": "TECH-NDS-01",
        "name": "NDS Worker",
        "agent_type": "Employee",
        "department": "Technical",
        "role": "NDS Analysis",
        "version": "1.1.0",
        "status": "READY"
    }

    RESPONSIBILITIES = [
        "Analyze market structure using NDS concepts",
        "Identify liquidity zones and pools",
        "Perform multi-timeframe analysis (H1 to M1)",
        "Produce final analysis on M1",
        "Generate structured report with confidence and evidence",
        "Submit report only to Technical Department Manager"
    ]

    RESTRICTIONS = [
        "Cannot communicate with other employees",
        "Cannot communicate with Assistant",
        "Cannot execute trades",
        "Cannot modify knowledge or architecture",
        "Cannot create autonomous missions"
    ]

    TIMEFRAMES = ["H1", "M15", "M5", "M1"]

    def __init__(self):
        self.identity = self.IDENTITY.copy()
        self.memory_engine = MemoryEngine(agent_id=self.identity["agent_id"])

    def _extract_context(self, mission_input: Dict[str, Any]) -> Dict[str, Any]:
        raw = mission_input.get("input", mission_input)
        return {
            "symbol": raw.get("symbol", "UNKNOWN"),
            "timeframe": raw.get("timeframe", "M1"),
            "context": raw.get("context", ""),
            "chart_data": raw.get("chart_data"),
            "price": raw.get("price"),
            "bid": raw.get("bid"),
            "ask": raw.get("ask"),
            "session": raw.get("session"),
            "direction_hint": raw.get("direction_hint"),
        }

    def _analyze_market_structure(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structural NDS market-structure assessment.
        Without live OHLC, returns disciplined placeholder with clear confidence penalty.
        """
        has_chart = bool(ctx.get("chart_data"))

        structure = {
            "trend_state": "UNDEFINED",
            "structure_type": "RANGE_OR_UNKNOWN",
            "bos": None,          # Break of Structure
            "choch": None,        # Change of Character
            "internal_structure": "UNKNOWN",
            "swing_high": None,
            "swing_low": None,
            "notes": []
        }

        if not has_chart:
            structure["notes"].append("No OHLC/chart_data provided — structure cannot be confirmed.")
            structure["notes"].append("NDS requires confirmed swing points before bias lock.")
        else:
            structure["notes"].append("Chart data detected — full structure engine pending price-model integration.")

        return structure

    def _analyze_liquidity(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        liquidity = {
            "buy_side_liquidity": [],
            "sell_side_liquidity": [],
            "equal_highs": False,
            "equal_lows": False,
            "liquidity_grab_risk": "UNKNOWN",
            "notes": []
        }

        if not ctx.get("chart_data"):
            liquidity["notes"].append("Liquidity map unavailable without swing highs/lows from chart.")
            liquidity["liquidity_grab_risk"] = "HIGH_UNCERTAINTY"
        else:
            liquidity["notes"].append("Liquidity mapping ready for OHLC integration.")

        return liquidity

    def _multi_timeframe_summary(self, ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        frames = []
        for tf in self.TIMEFRAMES:
            frames.append({
                "timeframe": tf,
                "bias": "NEUTRAL",
                "structure": "UNCONFIRMED",
                "confidence": 0.0 if not ctx.get("chart_data") else 0.2,
                "role": "CONTEXT" if tf != "M1" else "EXECUTION"
            })
        return frames

    def _derive_bias(self, structure: Dict[str, Any], liquidity: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conservative bias engine.
        No chart => forced NEUTRAL / NO_TRADE posture.
        """
        if not ctx.get("chart_data"):
            return {
                "bias": "NEUTRAL",
                "setup": "NO_SETUP",
                "entry_model": None,
                "invalidation": None,
                "reason": "Missing chart_data. NDS bias cannot be validated."
            }

        return {
            "bias": "NEUTRAL",
            "setup": "DATA_PRESENT_BUT_MODEL_NOT_FULLY_WIRED",
            "entry_model": "M1_CONFIRMATION_REQUIRED",
            "invalidation": None,
            "reason": "Chart data present; advanced NDS pattern engine not fully connected yet."
        }

    def _score_confidence(self, ctx: Dict[str, Any], structure: Dict[str, Any], bias_info: Dict[str, Any]) -> float:
        score = 0.0

        if ctx.get("symbol") and ctx["symbol"] != "UNKNOWN":
            score += 0.1
        if ctx.get("chart_data"):
            score += 0.4
        if structure.get("trend_state") not in ["UNDEFINED", None]:
            score += 0.2
        if bias_info.get("bias") in ["BULLISH", "BEARISH"]:
            score += 0.2
        if bias_info.get("setup") not in [None, "NO_SETUP"]:
            score += 0.1

        return round(min(score, 1.0), 2)

    def analyze(self, mission_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute independent NDS analysis."""
        self.memory_engine.add_working(
            content=mission_input,
            meta={"type": "mission_input"}
        )

        ctx = self._extract_context(mission_input)
        structure = self._analyze_market_structure(ctx)
        liquidity = self._analyze_liquidity(ctx)
        mtf = self._multi_timeframe_summary(ctx)
        bias_info = self._derive_bias(structure, liquidity, ctx)
        confidence = self._score_confidence(ctx, structure, bias_info)

        evidence = []
        if ctx.get("symbol"):
            evidence.append(f"Symbol context: {ctx['symbol']}")
        if ctx.get("chart_data"):
            evidence.append("Chart data provided in mission input")
        else:
            evidence.append("No chart_data in mission input")
        evidence.append("Final execution timeframe locked to M1 per NDS rule")

        limitations = []
        if not ctx.get("chart_data"):
            limitations.append("No live/OHLC chart data connected")
            limitations.append("Cannot confirm BOS/CHoCH or liquidity pools")
        limitations.append("Advanced pattern recognition model not fully integrated")

        result = {
            "agent_id": self.identity["agent_id"],
            "version": self.identity["version"],
            "mission_id": mission_input.get("mission_id"),
            "output_type": "Analysis",
            "symbol": ctx["symbol"],
            "analysis": {
                "method": "NDS",
                "timeframes_used": self.TIMEFRAMES,
                "final_timeframe": "M1",
                "market_structure": structure,
                "liquidity": liquidity,
                "multi_timeframe": mtf,
                "bias": bias_info["bias"],
                "setup": bias_info["setup"],
                "entry_model": bias_info.get("entry_model"),
                "invalidation": bias_info.get("invalidation"),
                "key_levels": [],
                "summary": bias_info["reason"]
            },
            "confidence": confidence,
            "evidence": evidence,
            "limitations": limitations,
            "status": "COMPLETED",
            "timestamp": datetime.utcnow().isoformat()
        }

        self.memory_engine.add_mission_history(
            mission_id=mission_input.get("mission_id", "UNKNOWN"),
            result=result
        )

        # Store neutral experience trail
        self.memory_engine.add_experience(
            content={
                "symbol": ctx["symbol"],
                "bias": bias_info["bias"],
                "confidence": confidence,
                "had_chart_data": bool(ctx.get("chart_data"))
            },
            mission_id=mission_input.get("mission_id", "UNKNOWN"),
            confidence=confidence
        )

        return result

    def generate_report(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate formal report for TECH-MANAGER only."""
        analysis = analysis_result.get("analysis", {})

        report = {
            "report_id": f"REPORT-{self.identity['agent_id']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "mission_id": analysis_result.get("mission_id"),
            "agent_id": self.identity["agent_id"],
            "department": "Technical",
            "symbol": analysis_result.get("symbol"),
            "analysis": analysis,
            "confidence": analysis_result.get("confidence", 0.0),
            "evidence": analysis_result.get("evidence", []),
            "limitations": analysis_result.get("limitations", []),
            "risk": {
                "level": "HIGH" if analysis_result.get("confidence", 0) < 0.4 else "MEDIUM",
                "notes": analysis_result.get("limitations", [])
            },
            "recommendation": {
                "action": "NO_TRADE" if analysis.get("bias") == "NEUTRAL" else "WAIT_CONFIRMATION",
                "bias": analysis.get("bias"),
                "setup": analysis.get("setup")
            },
            "validation": "PENDING",
            "status": analysis_result.get("status"),
            "timestamp": datetime.utcnow().isoformat()
        }
        return report

    def submit_to_manager(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Submit report only to Technical Manager."""
        return {
            "from": self.identity["agent_id"],
            "to": "TECH-MANAGER",
            "type": "REPORT",
            "payload": report,
            "timestamp": datetime.utcnow().isoformat()
        }
