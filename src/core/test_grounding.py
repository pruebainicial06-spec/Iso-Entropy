import pytest
from .grounding import ground_inputs

def test_ground_inputs():
    # Test case 1: Low volatility, Low rigidity
    result = ground_inputs("Low (Stable)", "Low (Automated)", 6)
    assert result["I"] == 0.6
    assert result["K0"] == 3.0
    assert result["stock"] == 0.25
    assert result["liquidity"] == 0.9
    assert result["capital"] == 1.0

    # Test case 2: Medium volatility, Medium rigidity
    result = ground_inputs("Medium (Seasonal)", "Medium (Standard)", 12)
    assert result["I"] == 1.5
    assert result["K0"] == 1.5
    assert result["stock"] == 0.5
    assert result["liquidity"] == 0.6
    assert result["capital"] == 1.0

    # Test case 3: High volatility, High rigidity
    result = ground_inputs("High (Chaotic)", "High (Manual/Bureaucratic)", 3)
    assert result["I"] == 5.0
    assert result["K0"] == 0.8
    assert result["stock"] == 0.125
    assert result["liquidity"] == 0.3
    assert result["capital"] == 1.0

    # Test case 4: Invalid volatility
    result = ground_inputs("Invalid Volatility", "Low (Automated)", 6)
    assert result["I"] == 5.0  # Should default to 5.0
    assert result["K0"] == 3.0
    assert result["stock"] == 0.25
    assert result["liquidity"] == 0.9
    assert result["capital"] == 1.0

    # Test case 5: Invalid rigidity
    result = ground_inputs("Low (Stable)", "Invalid Rigidity", 6)
    assert result["I"] == 0.6
    assert result["K0"] == 0.8  # Should default to 0.8
    assert result["stock"] == 0.25
    assert result["liquidity"] == 0.9
    assert result["capital"] == 1.0
