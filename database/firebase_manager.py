import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

class FirebaseManager:
    """
    Gestor de base de datos Firestore.
    Usa firebase-admin (SDK Admin) para operaciones CRUD.
    
    Estructura de colecciones Firestore equivalente al schema SQL anterior:
    
    /usuarios/{uid}              → datos del usuario (nombre, rol, email, activo)
    /pacientes/{id}              → datos personales del paciente
    /psicologos/{id}             → perfil profesional del psicólogo
    /citas/{id}                  → citas programadas
    /sesiones_clinicas/{id}      → notas de sesión terapéutica
    /diagnosticos_catalogo/{id}  → catálogo DSM-5 / CIE-11
    /facturas/{id}               → control de pagos
    /documentos/{id}             → referencias a archivos (Firebase Storage)
    """

    _instance = None

    def __new__(cls):
        """Singleton — solo una instancia del FirebaseManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._db = None
        service_account_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "firebase_service_account.json"
        )

        if os.path.exists(service_account_path):
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                print("[DEBUG] Firestore inicializado correctamente.")
            except Exception as e:
                print(f"[WARN] No se pudo inicializar Firestore Admin: {e}")
        else:
            print("[WARN] firebase_service_account.json no encontrado. Firestore Admin no disponible.")

        self._initialized = True

    def is_configured(self):
        return self._db is not None

    # ── Usuarios ───────────────────────────────────────────────
    def crear_usuario(self, uid, nombre_completo, email, rol="recepcionista"):
        """Crear documento de usuario en Firestore al registrarse."""
        if not self.is_configured():
            return False
        try:
            self._db.collection("usuarios").document(uid).set({
                "nombre_completo": nombre_completo,
                "email": email,
                "rol": rol,
                "activo": True,
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP,
            })
            return True
        except Exception as e:
            print(f"[ERROR] crear_usuario: {e}")
            return False

    def obtener_usuario(self, uid):
        """Obtener datos de un usuario por su UID."""
        if not self.is_configured():
            return None
        try:
            doc = self._db.collection("usuarios").document(uid).get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"[ERROR] obtener_usuario: {e}")
            return None

    # ── Pacientes ──────────────────────────────────────────────
    def crear_paciente(self, datos: dict):
        """Crear un nuevo paciente en la colección /pacientes."""
        if not self.is_configured():
            return None
        try:
            datos["fecha_registro"] = firestore.SERVER_TIMESTAMP
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            datos["activo"] = True
            ref = self._db.collection("pacientes").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_paciente: {e}")
            return None

    def obtener_pacientes(self, solo_activos=True):
        """Listar todos los pacientes."""
        if not self.is_configured():
            return []
        try:
            query = self._db.collection("pacientes")
            if solo_activos:
                query = query.where("activo", "==", True)
            return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]
        except Exception as e:
            print(f"[ERROR] obtener_pacientes: {e}")
            return []

    # ── Citas ──────────────────────────────────────────────────
    def crear_cita(self, datos: dict):
        """Crear una cita en la colección /citas."""
        if not self.is_configured():
            return None
        try:
            datos["estado"] = datos.get("estado", "programada")
            datos["created_at"] = firestore.SERVER_TIMESTAMP
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("citas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_cita: {e}")
            return None

    def obtener_citas(self):
        """Listar todas las citas."""
        if not self.is_configured():
            return []
        try:
            docs = self._db.collection("citas").stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            print(f"[ERROR] obtener_citas: {e}")
            return []

    def obtener_citas_por_psicologo(self, psicologo_id):
        """Listar citas de un psicólogo específico."""
        if not self.is_configured():
            return []
        try:
            docs = (
                self._db.collection("citas")
                .where("psicologo_id", "==", psicologo_id)
                .stream()
            )
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            print(f"[ERROR] obtener_citas_por_psicologo: {e}")
            return []

    def actualizar_cita(self, cita_id, datos: dict):
        if not self.is_configured(): return False
        try:
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            self._db.collection("citas").document(cita_id).update(datos)
            return True
        except Exception as e:
            print(f"[ERROR] actualizar_cita: {e}")
            return False

    def eliminar_cita(self, cita_id):
        if not self.is_configured(): return False
        try:
            self._db.collection("citas").document(cita_id).delete()
            return True
        except Exception as e:
            print(f"[ERROR] eliminar_cita: {e}")
            return False

    # ── Sesiones Clínicas ──────────────────────────────────────
    def crear_sesion(self, datos: dict):
        if not self.is_configured(): return None
        try:
            datos["fecha"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("sesiones_clinicas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_sesion: {e}")
            return None

    def obtener_sesiones_por_paciente(self, paciente_id):
        if not self.is_configured(): return []
        try:
            docs = self._db.collection("sesiones_clinicas").where("paciente_id", "==", paciente_id).stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            print(f"[ERROR] obtener_sesiones_por_paciente: {e}")
            return []

    def actualizar_sesion(self, sesion_id, datos: dict):
        if not self.is_configured(): return False
        try:
            self._db.collection("sesiones_clinicas").document(sesion_id).update(datos)
            return True
        except Exception as e:
            print(f"[ERROR] actualizar_sesion: {e}")
            return False

    def eliminar_sesion(self, sesion_id):
        if not self.is_configured(): return False
        try:
            self._db.collection("sesiones_clinicas").document(sesion_id).delete()
            return True
        except Exception as e:
            print(f"[ERROR] eliminar_sesion: {e}")
            return False

    # ── Facturación ────────────────────────────────────────────
    def crear_factura(self, datos: dict):
        if not self.is_configured(): return None
        try:
            datos["fecha_emision"] = firestore.SERVER_TIMESTAMP
            datos["estado"] = datos.get("estado", "pendiente")
            ref = self._db.collection("facturas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_factura: {e}")
            return None

    def obtener_facturas(self):
        if not self.is_configured(): return []
        try:
            docs = self._db.collection("facturas").stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            print(f"[ERROR] obtener_facturas: {e}")
            return []

    def actualizar_factura(self, factura_id, datos: dict):
        if not self.is_configured(): return False
        try:
            self._db.collection("facturas").document(factura_id).update(datos)
            return True
        except Exception as e:
            print(f"[ERROR] actualizar_factura: {e}")
            return False

    # ── Recetas ────────────────────────────────────────────────
    def crear_receta(self, datos: dict):
        if not self.is_configured(): return None
        try:
            datos["fecha_emision"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("recetas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_receta: {e}")
            return None

    def obtener_recetas_por_paciente(self, paciente_id):
        if not self.is_configured(): return []
        try:
            docs = self._db.collection("recetas").where("paciente_id", "==", paciente_id).stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            print(f"[ERROR] obtener_recetas_por_paciente: {e}")
            return []

    def obtener_todas_recetas(self):
        if not self.is_configured(): return []
        try:
            docs = self._db.collection("recetas").order_by("fecha_emision", direction=firestore.Query.DESCENDING).stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception:
            try:
                docs = self._db.collection("recetas").stream()
                return [doc.to_dict() | {"id": doc.id} for doc in docs]
            except Exception as e:
                print(f"[ERROR] obtener_todas_recetas: {e}")
                return []

    def actualizar_receta(self, receta_id: str, datos: dict):
        if not self.is_configured(): return False
        try:
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            self._db.collection("recetas").document(receta_id).update(datos)
            return True
        except Exception as e:
            print(f"[ERROR] actualizar_receta: {e}")
            return False

    def eliminar_receta(self, receta_id):
        if not self.is_configured(): return False
        try:
            self._db.collection("recetas").document(receta_id).delete()
            return True
        except Exception as e:
            print(f"[ERROR] eliminar_receta: {e}")
            return False

    # ── Fármacos ──────────────────────────────────────────────
    def crear_farmaco(self, datos: dict):
        if not self.is_configured(): return None
        try:
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("farmacos").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_farmaco: {e}")
            return None

    def obtener_farmacos(self):
        if not self.is_configured(): return []
        try:
            docs = self._db.collection("farmacos").stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            print(f"[ERROR] obtener_farmacos: {e}")
            return []

    def actualizar_farmaco(self, farmaco_id: str, datos: dict):
        if not self.is_configured(): return False
        try:
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            self._db.collection("farmacos").document(farmaco_id).update(datos)
            return True
        except Exception as e:
            print(f"[ERROR] actualizar_farmaco: {e}")
            return False

    def eliminar_farmaco(self, farmaco_id: str):
        if not self.is_configured(): return False
        try:
            self._db.collection("farmacos").document(farmaco_id).delete()
            return True
        except Exception as e:
            print(f"[ERROR] eliminar_farmaco: {e}")
            return False

    # ── Historias Clínicas ────────────────────────────────────
    def crear_historia_clinica(self, datos: dict):
        """Crear una historia clínica completa en Firestore."""
        if not self.is_configured(): return None
        try:
            datos["created_at"] = firestore.SERVER_TIMESTAMP
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("historias_clinicas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_historia_clinica: {e}")
            return None

    def obtener_historias_clinicas(self):
        """Listar todas las historias clínicas."""
        if not self.is_configured(): return []
        try:
            docs = self._db.collection("historias_clinicas").stream()
            return [doc.to_dict() | {"id": doc.id} for doc in docs]
        except Exception as e:
            print(f"[ERROR] obtener_historias_clinicas: {e}")
            return []

    def obtener_historia_por_paciente(self, paciente_id):
        """Obtener la historia clínica asociada a un paciente."""
        if not self.is_configured(): return None
        try:
            docs = self._db.collection("historias_clinicas").where("paciente_id", "==", paciente_id).limit(1).stream()
            results = [doc.to_dict() | {"id": doc.id} for doc in docs]
            return results[0] if results else None
        except Exception as e:
            print(f"[ERROR] obtener_historia_por_paciente: {e}")
            return None

    def actualizar_historia_clinica(self, historia_id, datos: dict):
        """Actualizar datos de una historia clínica existente."""
        if not self.is_configured(): return False
        try:
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            self._db.collection("historias_clinicas").document(historia_id).update(datos)
            return True
        except Exception as e:
            print(f"[ERROR] actualizar_historia_clinica: {e}")
            return False

    def eliminar_historia_clinica(self, historia_id):
        """Eliminar una historia clínica."""
        if not self.is_configured(): return False
        try:
            self._db.collection("historias_clinicas").document(historia_id).delete()
            return True
        except Exception as e:
            print(f"[ERROR] eliminar_historia_clinica: {e}")
            return False
