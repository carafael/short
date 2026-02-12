"""
Philosophy domain mode
"""

from typing import Dict, Any, List


class PhilosophyMode:
    """Specialized mode for philosophical discussions and analysis"""

    def __init__(self):
        self.name = "philosophy"
        self.description = "Philosophical reasoning, argument analysis, and ethical discussions"

        # Major philosophical branches
        self.branches = {
            "metaphysics": "Nature of reality, existence, causation, time, space",
            "epistemology": "Nature of knowledge, belief, justification, truth",
            "ethics": "Morality, right and wrong, virtue, duty, consequences",
            "logic": "Reasoning, argumentation, validity, soundness",
            "aesthetics": "Nature of beauty, art, taste, criticism",
            "political": "Justice, rights, liberty, authority, legitimacy",
            "philosophy_of_mind": "Consciousness, mental states, cognition",
            "philosophy_of_science": "Scientific method, theories, explanation"
        }

        # Logical fallacies
        self.fallacies = {
            "ad_hominem": "Attacking the person instead of the argument",
            "straw_man": "Misrepresenting an argument to make it easier to attack",
            "false_dichotomy": "Presenting only two options when more exist",
            "slippery_slope": "Claiming one thing will lead to extreme consequences",
            "appeal_to_authority": "Accepting claims based solely on authority",
            "appeal_to_emotion": "Manipulating emotions instead of using logic",
            "circular_reasoning": "Using the conclusion as a premise",
            "hasty_generalization": "Drawing conclusions from insufficient evidence",
            "red_herring": "Introducing irrelevant information to distract",
            "tu_quoque": "Dismissing criticism by pointing out hypocrisy"
        }

        # Ethical frameworks
        self.ethical_frameworks = {
            "consequentialism": {
                "description": "Actions judged by their consequences",
                "key_thinkers": ["Bentham", "Mill", "Singer"],
                "example": "Utilitarianism - maximize overall happiness"
            },
            "deontology": {
                "description": "Actions judged by adherence to rules/duties",
                "key_thinkers": ["Kant", "Ross"],
                "example": "Categorical imperative - act according to universal law"
            },
            "virtue_ethics": {
                "description": "Focus on character and virtues",
                "key_thinkers": ["Aristotle", "MacIntyre"],
                "example": "Cultivate virtues like courage, wisdom, justice"
            },
            "care_ethics": {
                "description": "Emphasis on relationships and caring",
                "key_thinkers": ["Gilligan", "Noddings"],
                "example": "Consider contextual relationships and responsibilities"
            }
        }

        # Argument structures
        self.argument_forms = {
            "modus_ponens": {
                "structure": ["If P then Q", "P", "Therefore Q"],
                "valid": True
            },
            "modus_tollens": {
                "structure": ["If P then Q", "Not Q", "Therefore not P"],
                "valid": True
            },
            "hypothetical_syllogism": {
                "structure": ["If P then Q", "If Q then R", "Therefore if P then R"],
                "valid": True
            },
            "disjunctive_syllogism": {
                "structure": ["P or Q", "Not P", "Therefore Q"],
                "valid": True
            },
            "affirming_consequent": {
                "structure": ["If P then Q", "Q", "Therefore P"],
                "valid": False,
                "note": "Common fallacy"
            },
            "denying_antecedent": {
                "structure": ["If P then Q", "Not P", "Therefore not Q"],
                "valid": False,
                "note": "Common fallacy"
            }
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for this domain"""
        return """You are now in Philosophy mode.

Focus on:
- Clear conceptual analysis
- Rigorous argumentation
- Identification of assumptions
- Exploration of implications
- Multiple perspectives
- Historical context
- Logical validity and soundness

Provide:
- Socratic questioning to deepen understanding
- Analysis of argument structure
- Identification of logical fallacies
- Discussion of different philosophical positions
- References to relevant thinkers and texts
- Exploration of thought experiments
- Clarification of key terms and concepts

Approach discussions with:
1. Intellectual humility
2. Charitable interpretation
3. Precision in language
4. Openness to counterarguments
5. Acknowledgment of complexity
"""

    def get_context_hints(self) -> List[str]:
        """Get contextual hints for this domain"""
        return [
            "Define key terms clearly",
            "Distinguish between valid and sound arguments",
            "Consider multiple philosophical perspectives",
            "Identify hidden assumptions",
            "Use thought experiments to test intuitions",
            "Provide charitable interpretations",
            "Acknowledge limitations and uncertainties",
            "Connect to relevant historical debates"
        ]

    def analyze_argument(self, premises: List[str], conclusion: str) -> Dict[str, Any]:
        """Provide basic argument analysis structure"""
        return {
            "premises": premises,
            "conclusion": conclusion,
            "questions_to_consider": [
                "Are the premises true?",
                "Does the conclusion follow from the premises?",
                "Are there hidden assumptions?",
                "What are potential counterarguments?",
                "What are the implications if the argument is sound?"
            ],
            "fallacies_to_check": list(self.fallacies.keys())
        }

    def get_fallacies(self) -> Dict[str, str]:
        """Get logical fallacies reference"""
        return self.fallacies

    def get_ethical_frameworks(self) -> Dict[str, Any]:
        """Get ethical frameworks reference"""
        return self.ethical_frameworks

    def get_argument_forms(self) -> Dict[str, Any]:
        """Get logical argument forms"""
        return self.argument_forms

    def get_socratic_questions(self, topic: str) -> List[str]:
        """Generate Socratic questions for deeper inquiry"""
        return [
            f"What do you mean by '{topic}'?",
            f"What assumptions are we making about {topic}?",
            f"What would be an example of {topic}?",
            f"What are the implications if we accept this view of {topic}?",
            f"How do we know this about {topic}?",
            f"What alternative perspectives exist on {topic}?",
            f"What would count as evidence against this view of {topic}?",
            f"How does this understanding of {topic} connect to broader questions?"
        ]

    def thought_experiments(self) -> Dict[str, Dict[str, str]]:
        """Classic philosophical thought experiments"""
        return {
            "trolley_problem": {
                "description": "Would you pull a lever to divert a trolley to kill one person instead of five?",
                "topics": "Ethics, consequentialism, moral duties"
            },
            "ship_of_theseus": {
                "description": "If all parts of a ship are replaced, is it still the same ship?",
                "topics": "Identity, persistence, change"
            },
            "brain_in_vat": {
                "description": "How do you know you're not a brain in a vat being fed false experiences?",
                "topics": "Skepticism, knowledge, reality"
            },
            "veil_of_ignorance": {
                "description": "What society would you design if you didn't know your position in it?",
                "topics": "Justice, fairness, social contract"
            },
            "chinese_room": {
                "description": "Can a system that manipulates symbols understand meaning?",
                "topics": "Consciousness, AI, understanding"
            },
            "experience_machine": {
                "description": "Would you plug into a machine providing perfect simulated experiences?",
                "topics": "Well-being, reality, value"
            }
        }
