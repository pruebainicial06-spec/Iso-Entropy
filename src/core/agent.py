# agent.py - ISO-ENTROPY Autonomous Auditor (google-genai)
import os
import time
import json
import hashlib
import math
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# ✓ CORRECT IMPORT (google-genai)
from google import genai

from .physics import run_simulation, calculate_collapse_threshold
from .grounding import ground_inputs
from .constraints import apply_hard_rules, HardConstraintViolation
from .fsm import IsoEntropyFSM, AgentPhase
from .prompt_templates import build_prompt_for_phase
from .telemetry import build_llm_signal

load_dotenv()


# ============================================================================
# RATE LIMITER - Respects 5 RPM
# ============================================================================

class RateLimiter:
    """Handles 5 RPM rate limit for Gemini."""
    
    def __init__(self, max_rpm: int = 5):
        self.max_rpm = max_rpm
        self.min_interval = 60.0 / max_rpm  # 12 seconds
        self.request_timestamps = []
        self.total_requests = 0
    
    def wait_if_needed(self, verbose: bool = True) -> float:
        """Waits if necessary to respect 5 RPM."""
        now = time.time()
        
        # Clean up old timestamps (outside 60-second window)
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if now - ts < 60.0
        ]
        
        # If there are 5 requests in the window, wait
        if len(self.request_timestamps) >= self.max_rpm:
            oldest = self.request_timestamps[0]
            wait_time = 60.0 - (now - oldest) + 0.5
            if verbose:
                print(f"⏳ Rate limit (5 RPM): waiting {wait_time:.1f}s")
            time.sleep(wait_time)
            now = time.time()
        
        # Ensure minimum interval
        if self.request_timestamps:
            last = self.request_timestamps[-1]
            elapsed = now - last
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                if verbose:
                    print(f"⏳ Minimum interval: waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                now = time.time()
        
        # Register request
        self.request_timestamps.append(now)
        self.total_requests += 1
        
        return now


# ============================================================================
# MAIN AUTONOMOUS AUDITOR
# ============================================================================

class IsoEntropyAgent:
    """
    Autonomous Auditor with complete FSM.
    - FSM: ORIENT → VALIDATE → STRESS → CONCLUDE
    - Smart loops adjusting K
    - Monte Carlo simulation (500 runs)
    - Function calling to Gemini
    - Rate limit respected
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        mock_mode: bool = False,
        verbose: bool = True,
        max_iterations: int = 10
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.mock_mode = mock_mode or os.getenv("ISO_MOCK_MODE", "false").lower() == "true"
        self.verbose = verbose
        self.max_iterations = max_iterations
        
        if not self.mock_mode and not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not found")
        
        if not self.mock_mode:
            # ✓ CORRECT INITIALIZATION (google-genai)
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None
        
        # Agent state
        self.fsm = IsoEntropyFSM()
        self.experiment_log: List[Dict[str, Any]] = []
        self.rate_limiter = RateLimiter(max_rpm=5)
        self.cache = {}
    
    def _log(self, message: str):
        if self.verbose:
            print(message)
    
    def _get_cache_key(self, user_input: str, volatility: str, rigidity: str) -> str:
        """Cache key."""
        key = f"{user_input}|{volatility}|{rigidity}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def _calculate_wilson_upper_bound(self, collapses: int, runs: int) -> float:
        """Calculates Wilson score interval upper bound (95%)."""
        if runs == 0:
            return 1.0
        
        z = 1.96  # 95% confidence
        phat = collapses / runs
        denom = 1 + (z**2 / runs)
        centre = phat + (z**2 / (2 * runs))
        adj = z * math.sqrt((phat * (1 - phat) / runs) + (z**2 / (4 * runs**2)))
        upper = (centre + adj) / denom
        
        return min(1.0, upper)
    
    # ========================================================================
    # STEP 1: GROUND INPUTS (Local Calculation)
    # ========================================================================
    
    def _ground_inputs_and_validate(
        self,
        user_input: str,
        volatility: str,
        rigidity: str,
        buffer: int
    ) -> Dict[str, float]:
        """Calculates parameters locally and applies hard rules."""
        
        self._log("\n" + "="*70)
        self._log("🚀 ISO-ENTROPY AUTONOMOUS AUDIT")
        self._log("="*70)
        
        # 1. Ground inputs
        params = ground_inputs(volatility, rigidity, buffer)
        self._log(f"📊 Initial parameters: I={params['I']:.2f}, K={params['K0']:.2f}")
        
        # 2. Calculate theta_max
        theta_max = calculate_collapse_threshold(
            params['stock'],
            params['capital'],
            params['liquidity']
        )
        params['theta_max'] = theta_max
        self._log(f"📊 Collapse threshold: θ_max={theta_max:.2f}")
        
        # 3. Apply hard rules
        try:
            apply_hard_rules(
                volatility=volatility,
                rigidity=rigidity,
                buffer_months=buffer,
                params=params
            )
            self._log("✅ Hard rules applied")
        except HardConstraintViolation as e:
            self._log(f"🚫 Constraint violation: {e}")
            raise
        
        return params
    
    # ========================================================================
    # STEP 2: MAIN LOOP WITH FSM
    # ========================================================================
    
    def audit_system(
        self,
        user_input: str,
        volatility: str,
        rigidity: str,
        buffer: int
    ) -> str:
        """
        Complete audit with FSM and loops.
        """
        
        # Check cache
        cache_key = self._get_cache_key(user_input, volatility, rigidity)
        if cache_key in self.cache:
            self._log("✅ Report retrieved from cache")
            return self.cache[cache_key]
        
        # Ground inputs
        physical_params = self._ground_inputs_and_validate(
            user_input, volatility, rigidity, buffer
        )
        
        I = physical_params['I']
        K_base = physical_params['K0']
        stock = physical_params['stock']
        liquidity = physical_params['liquidity']
        capital = physical_params['capital']
        theta_max = physical_params['theta_max']
        
        # Mock mode
        if self.mock_mode:
            self._log("🎭 MOCK MODE")
            report = self._generate_mock_report(
                user_input, I, K_base, theta_max, stock, liquidity, capital
            )
            self.cache[cache_key] = report
            return report
        
        # ====================================================================
        # MAIN LOOP: ORIENT → VALIDATE → STRESS → CONCLUDE
        # ====================================================================
        
        current_K = K_base
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            self._log(f"\n📍 Iteration {iteration}/{self.max_iterations} - Phase: {self.fsm.phase_name()}")
            
            # 1. Run simulation
            self._log(f"🔬 Simulating: I={I:.2f}, K={current_K:.2f}, θ_max={theta_max:.2f}")
            
            sim_result = run_simulation(I, current_K, theta_max, runs=500)
            collapse_rate = sim_result['collapse_rate']
            collapses = sim_result.get('total_collapses', int(collapse_rate * 500))
            ub95 = self._calculate_wilson_upper_bound(collapses, 500)
            
            self._log(f"📊 Result: Collapse={collapse_rate:.1%}, UB95={ub95:.1%}")
            
            # 2. Log experiment
            self.experiment_log.append({
                'cycle': iteration,
                'phase': self.fsm.phase_name(),
                'hypothesis': {'I': I, 'K': current_K},
                'result': {
                    'collapse_rate': collapse_rate,
                    'upper_ci95': ub95,
                    'total_collapses': collapses,
                    'runs': 500,
                    'trajectory': sim_result.get('trajectory', [])
                }
            })
            
            # 3. Update FSM
            self.fsm.update(collapse_rate, ub95)
            self._log(f"🔄 FSM updated → {self.fsm.phase_name()}")
            
            # 4. Phase-based decision
            if self.fsm.phase == AgentPhase.CONCLUDE:
                self._log("✅ Moving to CONCLUDE - Generating final report")
                break
            
            elif self.fsm.phase == AgentPhase.ORIENT:
                # Adjust K to find stability
                if collapse_rate < 0.05:
                    self._log("✅ Stability found in ORIENT")
                    current_K = current_K  # Maintain K
                else:
                    # Increase K
                    delta_k = 0.2 if collapse_rate > 0.5 else 0.1
                    current_K = min(current_K + delta_k, 10.0)
                    self._log(f"📈 Increasing K to {current_K:.2f}")
            
            elif self.fsm.phase == AgentPhase.VALIDATE:
                # Confirm reproducibility
                self._log("✓ In VALIDATE phase")
            
            elif self.fsm.phase == AgentPhase.STRESS:
                # Keep K constant
                self._log("⚠️ In STRESS phase (K constant)")
        
        # ====================================================================
        # GENERATE FINAL REPORT WITH GEMINI
        # ====================================================================
        
        self._log("\n📝 Generating final report with Gemini...")
        
        # Build master prompt with experiment history
        llm_signal = build_llm_signal(self.experiment_log)
        prompt = build_prompt_for_phase(
            phase=AgentPhase.CONCLUDE,  # Force executive report format
            phase_reasoning=self.fsm.phase_reasoning(),
            system_description=user_input,
            llm_signal=llm_signal
        )
        
        # Add final instructions
        final_prompt = f"""{prompt}

HISTORY OF EXPERIMENTS PERFORMED:
{json.dumps(self.experiment_log, indent=2)}

FINAL SYSTEM PARAMETERS:
- External Entropy (I): {I:.2f} bits
- Optimal Capacity (K): {current_K:.2f} bits
- I/K Ratio: {I/current_K:.2f}
- Collapse Threshold: {theta_max:.2f} bits
- Stock Buffer: {stock:.2f} months
- Liquidity: {liquidity:.2f}

GENERATE A COMPLETE EXECUTIVE REPORT IN MARKDOWN FORMAT WITH THE FOLLOWING EXACT STRUCTURE:

### Forensic Audit Report: [System Name]

**To the attention of the CEO:**

[Brief introduction on the purpose of the audit]

---

### 1. Diagnosis of Informational Insolvency
[Detailed analysis of the I/K ratio and its meaning in business terms]

### 2. Critical Failure Point
[Description of the collapse threshold and identified vulnerabilities]

### 3. Survival Horizon
[Temporal estimation of stability under current conditions]

### 4. Concrete Mitigation Actions
[Numbered list of 3 specific and actionable actions]

---

**Final Verdict:** [Executive conclusion]

---

IMPORTANT: Use a professional tone, explain technical terms in business language, and ensure the report is complete and actionable.
"""
        
        # Make Gemini call
        self.rate_limiter.wait_if_needed()

        try:
            model = "gemini-3-pro-preview" if self.fsm.phase == AgentPhase.CONCLUDE else "gemini-3-flash-preview"
            response = self.client.models.generate_content(
                model=model,
                contents=final_prompt
            )
            
            report = f"""# 🎯 Forensic Audit - ISO-ENTROPY

## 📊 Execution Context
- **Analyzed System:** {volatility} volatility, {rigidity} rigidity, {buffer} months buffer
- **Experiments Performed:** {len(self.experiment_log)}
- **Final Parameters:** I={I:.2f}, K={current_K:.2f}, θ_max={theta_max:.2f}
- **Final Phase:** {self.fsm.phase_name()}

---

{response.text}

---

## 📈 Experiment History

| Cycle | Phase | K (bits) | Collapse (%) | UB95 (%) |
|-------|------|----------|-------------|----------|
"""
            
            for exp in self.experiment_log:
                k = exp['hypothesis']['K']
                collapse = exp['result']['collapse_rate']
                ub = exp['result']['upper_ci95']
                phase = exp['phase']
                report += f"| {exp['cycle']} | {phase} | {k:.2f} | {collapse:.1%} | {ub:.1%} |\n"
            
            report += f"""
---
*Generated by Iso-Entropy Agent v2.3*
*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            # Cache result
            self.cache[cache_key] = report
            
            self._log("✅ Audit completed successfully")
            return report
        
        except Exception as e:
            error_str = str(e)
            self._log(f"❌ Gemini Error: {error_str[:100]}")
            
            # Fallback to mock if quota exhausted
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                self._log("💾 Quota exhausted. Generating mock report...")
                report = self._generate_mock_report(
                    user_input, I, current_K, theta_max, stock, liquidity, capital
                )
                self.cache[cache_key] = report
                return report
            else:
                raise
    
    # ========================================================================
    # MOCK REPORT GENERATOR
    # ========================================================================
    
    def _generate_mock_report(
        self,
        user_input: str,
        I: float,
        K: float,
        theta_max: float,
        stock: float,
        liquidity: float,
        capital: float
    ) -> str:
        """Generates a mock report when the API is unavailable."""
        
        ratio = I / K if K > 0 else float('inf')
        
        if ratio > 5:
            status = "🔴 CRITICAL"
            diagnosis = f"System in informational collapse. I/K = {ratio:.2f}"
            horizon = "7-14 days"
        elif ratio > 2:
            status = "🟠 MARGINAL"
            diagnosis = f"Fragile system. I/K = {ratio:.2f}"
            horizon = "30-60 days"
        else:
            status = "🟢 STABLE"
            diagnosis = f"Robust system. I/K = {ratio:.2f}"
            horizon = "6+ months"
        
        return f"""# 🎯 Forensic Audit - ISO-ENTROPY

**Status: {status}**

## 📋 Executive Summary
System under analysis with parameters: I={I:.2f} bits (Entropy), K={K:.2f} bits (Capacity).

## 🔍 Diagnosis of Informational Insolvency

**I/K Ratio: {ratio:.2f}**

{diagnosis}

## ⚠️ Structural Critical Failure Point

The system collapses when entropy debt ≥ {theta_max:.2f} bits.

Limiting factors:
- External Entropy (I): {I:.2f} bits
- Response Capacity (K): {K:.2f} bits
- Available Buffer (Stock): {stock:.2f} months
- Liquidity: {liquidity:.2f}

## ⏱️ Survival Horizon

**{horizon}** without corrective intervention.

## 🛡️ Strategic Mitigation

### Action 1: Increase Capacity (K)
- Automate manual processes
- Timeline: 4-6 weeks
- Investment: $50K-150K
- Impact: Reduce I/K by 20-30%

### Action 2: Reduce Volatility (I)
- Diversify revenue/services
- Timeline: 2-3 months
- Investment: $100K-300K
- Impact: Stabilize market by 15-25%

### Action 3: Strengthen Buffer
- Emergency credit line
- Timeline: Immediate (2-3 weeks)
- Investment: Low (0% if not used)
- Impact: +60% survival horizon

---
*Generated in Mock Mode*
*{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""