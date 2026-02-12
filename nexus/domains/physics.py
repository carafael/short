"""
Physics Lab domain mode
"""

from typing import Dict, Any, List
import math


class PhysicsMode:
    """Specialized mode for physics lab work and calculations"""

    def __init__(self):
        self.name = "physics"
        self.description = "Physics lab calculations, experimental design, and data analysis"

        # Physical constants
        self.constants = {
            "c": {"value": 299792458, "unit": "m/s", "name": "Speed of light"},
            "h": {"value": 6.62607015e-34, "unit": "J·s", "name": "Planck constant"},
            "G": {"value": 6.67430e-11, "unit": "N·m²/kg²", "name": "Gravitational constant"},
            "k_B": {"value": 1.380649e-23, "unit": "J/K", "name": "Boltzmann constant"},
            "e": {"value": 1.602176634e-19, "unit": "C", "name": "Elementary charge"},
            "m_e": {"value": 9.1093837015e-31, "unit": "kg", "name": "Electron mass"},
            "m_p": {"value": 1.67262192369e-27, "unit": "kg", "name": "Proton mass"},
            "N_A": {"value": 6.02214076e23, "unit": "1/mol", "name": "Avogadro constant"},
            "R": {"value": 8.314462618, "unit": "J/(mol·K)", "name": "Gas constant"},
            "epsilon_0": {"value": 8.8541878128e-12, "unit": "F/m", "name": "Vacuum permittivity"},
            "mu_0": {"value": 1.25663706212e-6, "unit": "N/A²", "name": "Vacuum permeability"}
        }

        # Common formulas
        self.formulas = {
            "kinematics": [
                "v = v₀ + at",
                "x = x₀ + v₀t + ½at²",
                "v² = v₀² + 2a(x - x₀)"
            ],
            "dynamics": [
                "F = ma",
                "F = dp/dt",
                "W = F·d",
                "P = F·v"
            ],
            "energy": [
                "KE = ½mv²",
                "PE = mgh",
                "E = mc²",
                "U = ½kx²"
            ],
            "waves": [
                "v = fλ",
                "f = 1/T",
                "I = P/A",
                "β = 10log₁₀(I/I₀)"
            ],
            "electricity": [
                "V = IR",
                "P = IV = I²R = V²/R",
                "Q = CV",
                "E = ½CV²"
            ],
            "magnetism": [
                "F = qvB sin θ",
                "F = BIL sin θ",
                "Φ = BA cos θ",
                "ε = -dΦ/dt"
            ],
            "thermodynamics": [
                "PV = nRT",
                "ΔU = Q - W",
                "S = k_B ln Ω",
                "η = 1 - T_c/T_h"
            ],
            "quantum": [
                "E = hf",
                "λ = h/p",
                "ΔxΔp ≥ ℏ/2",
                "ψ(x,t) = Ae^(i(kx-ωt))"
            ]
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for this domain"""
        return """You are now in Physics Lab mode.

Focus on:
- Experimental design and methodology
- Data analysis and error propagation
- Unit conversions and dimensional analysis
- Lab safety and best practices
- Equipment calibration and troubleshooting
- Statistical analysis of measurements
- Graph plotting and interpretation

Provide:
- Step-by-step calculations with units
- Error analysis and uncertainty calculations
- LaTeX-formatted equations when helpful
- Experimental procedures and safety considerations
- Data visualization recommendations
- Literature references when appropriate

Always include:
1. Proper SI units
2. Significant figures
3. Uncertainty estimates
4. Clear methodology
"""

    def get_context_hints(self) -> List[str]:
        """Get contextual hints for this domain"""
        return [
            "Always specify units in calculations",
            "Consider measurement uncertainty",
            "Check order of magnitude for reasonableness",
            "Use appropriate significant figures",
            "Document experimental conditions",
            "Include control experiments",
            "Verify equipment calibration",
            "Follow safety protocols"
        ]

    def get_constants(self) -> Dict[str, Any]:
        """Get physical constants"""
        return self.constants

    def get_formulas(self, category: str = None) -> Dict[str, List[str]]:
        """Get physics formulas by category"""
        if category:
            return {category: self.formulas.get(category, [])}
        return self.formulas

    def unit_converter(self, value: float, from_unit: str, to_unit: str) -> str:
        """Convert between common physics units"""
        # Simple conversion factors (expand as needed)
        conversions = {
            ("m", "cm"): 100,
            ("m", "mm"): 1000,
            ("m", "km"): 0.001,
            ("kg", "g"): 1000,
            ("kg", "mg"): 1e6,
            ("J", "eV"): 6.242e18,
            ("eV", "J"): 1.602e-19,
            ("C", "K"): lambda x: x + 273.15,
            ("K", "C"): lambda x: x - 273.15,
            ("deg", "rad"): math.pi / 180,
            ("rad", "deg"): 180 / math.pi,
        }

        key = (from_unit, to_unit)
        if key in conversions:
            factor = conversions[key]
            if callable(factor):
                result = factor(value)
            else:
                result = value * factor
            return f"{value} {from_unit} = {result} {to_unit}"
        else:
            return f"Conversion from {from_unit} to {to_unit} not available"

    def uncertainty_propagation(self, operation: str, values: List[float], uncertainties: List[float]) -> Dict[str, float]:
        """Calculate propagated uncertainty for basic operations"""
        if operation == "add" or operation == "subtract":
            # For addition/subtraction: add uncertainties in quadrature
            total_uncertainty = math.sqrt(sum(u**2 for u in uncertainties))
            if operation == "add":
                result = sum(values)
            else:
                result = values[0] - sum(values[1:])
        elif operation == "multiply" or operation == "divide":
            # For multiplication/division: add relative uncertainties in quadrature
            relative_uncertainties = [u/v for u, v in zip(uncertainties, values)]
            total_relative = math.sqrt(sum(ru**2 for ru in relative_uncertainties))

            if operation == "multiply":
                result = math.prod(values)
            else:
                result = values[0] / math.prod(values[1:])

            total_uncertainty = abs(result * total_relative)
        else:
            return {"error": "Operation not supported"}

        return {
            "result": result,
            "uncertainty": total_uncertainty,
            "relative_uncertainty": total_uncertainty / result if result != 0 else 0
        }
