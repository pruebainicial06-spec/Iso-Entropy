# fsm.py
from enum import Enum, auto
from typing import Optional


class AgentPhase(Enum):
    ORIENT = auto()
    VALIDATE = auto()
    STRESS = auto()
    CONCLUDE = auto()


class IsoEntropyFSM:
    def __init__(self):
        self.phase: AgentPhase = AgentPhase.ORIENT
        self.stable_hits: int = 0

    def update(self, collapse_rate: Optional[float]):
        if collapse_rate is None:
            return

        if self.phase == AgentPhase.ORIENT:
            if collapse_rate < 0.05:
                self.phase = AgentPhase.VALIDATE
                self.stable_hits = 1
            else:
                self.phase = AgentPhase.ORIENT

        elif self.phase == AgentPhase.VALIDATE:
            if collapse_rate < 0.05:
                self.stable_hits += 1
                if self.stable_hits >= 2:
                    self.phase = AgentPhase.STRESS
            else:
                self.phase = AgentPhase.ORIENT
                self.stable_hits = 0

        elif self.phase == AgentPhase.STRESS:
            self.phase = AgentPhase.CONCLUDE

    def allow_simulation(self) -> bool:
        return self.phase != AgentPhase.CONCLUDE

    def phase_reasoning(self) -> str:
        return {
            AgentPhase.ORIENT:
                "Diagnosticar si el sistema puede entrar en una región estable.",
            AgentPhase.VALIDATE:
                "Confirmar que la estabilidad observada no es estadística.",
            AgentPhase.STRESS:
                "Detectar fragilidad estructural bajo estrés controlado.",
            AgentPhase.CONCLUDE:
                "La ganancia informacional adicional es marginal."
        }[self.phase]

    def phase_name(self) -> str:
        return self.phase.name
