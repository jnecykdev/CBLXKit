#phase/CBLphaseDAO.py
from .phaseDAO import PhaseDAO
from .models.phase import Phase

class CBLPhaseDAO(PhaseDAO):
    
    @staticmethod
    def get_all_phases():
        try:
            return Phase.objects.all()
        except Exception as e:
                raise Exception(f"Erro ao buscar as fases: {str(e)}")


    @staticmethod
    def get_phase_by_id(phase_id):
        try:
            return Phase.objects.get(pk=phase_id)
        except Phase.DoesNotExist:
            return None
        except Exception as e:
                raise Exception(f"Erro ao buscar fase pelo ID: {str(e)}")
