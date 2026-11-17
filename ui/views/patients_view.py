# ui/views/patients_view.py
# Reexporta HistoriaClinicaView como PatientsView para retrocompatibilidad completa
from ui.views.historia_clinica_view import HistoriaClinicaView

class PatientsView(HistoriaClinicaView):
    """
    Vista de Historias Clínicas y Expedientes de Pacientes.
    Mantiene compatibilidad con el nombre PatientsView usado en la navegación.
    """
    pass
