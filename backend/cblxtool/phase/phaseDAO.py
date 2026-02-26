# phase/phaseDAO.py
from abc import ABC, abstractmethod

class PhaseDAO(ABC):
    @abstractmethod
    def get_all_phases(self):
        """Obtém todas as fases."""
        pass

    @abstractmethod
    def get_phase_by_id(self, phase_id):
        """Obtém uma fase pelo ID."""
        pass