import os
import firebase_admin
from firebase_admin import credentials, firestore
from core.app_paths import app_dir, load_app_env

load_app_env()

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
        self._current_user_id = None
        service_account_path = os.path.join(app_dir(), "firebase_service_account.json")

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

    def set_current_user_id(self, uid: str):
        """Fija el UID del usuario médico actualmente autenticado para aislar sus datos."""
        self._current_user_id = uid or ""
        print(f"[DEBUG] FirebaseManager: usuario activo fijado a '{self._current_user_id}'")

    def get_current_user_id(self) -> str:
        """Retorna el UID del usuario médico en sesión."""
        if not self._current_user_id:
            try:
                from core.auth_manager import AuthManager
                auth = AuthManager()
                self._current_user_id = auth.get_uid()
            except Exception:
                pass
        return self._current_user_id or ""

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
        """Crear un nuevo paciente en la colección /pacientes vinculado al usuario médico."""
        if not self.is_configured():
            return None
        try:
            if not datos.get("user_id"):
                datos["user_id"] = self.get_current_user_id()
            datos["fecha_registro"] = firestore.SERVER_TIMESTAMP
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            datos["activo"] = True
            ref = self._db.collection("pacientes").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_paciente: {e}")
            return None

    def obtener_pacientes(self, solo_activos=True, user_id=None):
        """Listar todos los pacientes pertenecientes al usuario actual."""
        if not self.is_configured():
            return []
        try:
            uid = user_id or self.get_current_user_id()
            query = self._db.collection("pacientes")
            if uid:
                query = query.where("user_id", "==", uid)
            docs = query.stream()
            results = []
            for doc in docs:
                d = doc.to_dict() | {"id": doc.id}
                if solo_activos and d.get("activo") is False:
                    continue
                results.append(d)
            return results
        except Exception as e:
            print(f"[ERROR] obtener_pacientes: {e}")
            return []

    # ── Citas ──────────────────────────────────────────────────
    def crear_cita(self, datos: dict):
        """Crear una cita vinculada al usuario médico."""
        if not self.is_configured():
            return None
        try:
            if not datos.get("user_id"):
                datos["user_id"] = self.get_current_user_id()
            datos["estado"] = datos.get("estado", "programada")
            datos["created_at"] = firestore.SERVER_TIMESTAMP
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("citas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_cita: {e}")
            return None

    def obtener_citas(self, user_id=None):
        """Listar citas del usuario actual."""
        if not self.is_configured():
            return []
        try:
            uid = user_id or self.get_current_user_id()
            query = self._db.collection("citas")
            if uid:
                query = query.where("user_id", "==", uid)
            docs = query.stream()
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
            if not datos.get("user_id"):
                datos["user_id"] = self.get_current_user_id()
            datos["fecha_registro"] = firestore.SERVER_TIMESTAMP
            # Se registra en 'sesiones' (usada en views)
            ref = self._db.collection("sesiones").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_sesion: {e}")
            return None

    def obtener_sesiones(self, user_id=None):
        """Obtiene las sesiones clínicas del médico actual."""
        if not self.is_configured(): return []
        try:
            uid = user_id or self.get_current_user_id()
            query = self._db.collection("sesiones")
            if uid:
                query = query.where("user_id", "==", uid)
            docs = query.stream()
            res = [doc.to_dict() | {"id": doc.id} for doc in docs]
            if not res:
                # Búsqueda de retrocompatibilidad en 'sesiones_clinicas'
                q2 = self._db.collection("sesiones_clinicas")
                if uid:
                    q2 = q2.where("user_id", "==", uid)
                res = [doc.to_dict() | {"id": doc.id} for doc in q2.stream()]
            return res
        except Exception as e:
            print(f"[ERROR] obtener_sesiones: {e}")
            return []

    def obtener_sesiones_por_paciente(self, paciente_id):
        if not self.is_configured(): return []
        try:
            docs = self._db.collection("sesiones").where("paciente_id", "==", paciente_id).stream()
            res = [doc.to_dict() | {"id": doc.id} for doc in docs]
            if not res:
                docs2 = self._db.collection("sesiones_clinicas").where("paciente_id", "==", paciente_id).stream()
                res = [doc.to_dict() | {"id": doc.id} for doc in docs2]
            return res
        except Exception as e:
            print(f"[ERROR] obtener_sesiones_por_paciente: {e}")
            return []

    def actualizar_sesion(self, sesion_id, datos: dict):
        if not self.is_configured(): return False
        try:
            self._db.collection("sesiones").document(sesion_id).update(datos)
            return True
        except Exception:
            try:
                self._db.collection("sesiones_clinicas").document(sesion_id).update(datos)
                return True
            except Exception as e:
                print(f"[ERROR] actualizar_sesion: {e}")
                return False

    def eliminar_sesion(self, sesion_id):
        if not self.is_configured(): return False
        try:
            self._db.collection("sesiones").document(sesion_id).delete()
            return True
        except Exception:
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
            if not datos.get("user_id"):
                datos["user_id"] = self.get_current_user_id()
            datos["fecha_emision"] = firestore.SERVER_TIMESTAMP
            datos["estado"] = datos.get("estado", "pendiente")
            ref = self._db.collection("facturas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_factura: {e}")
            return None

    def obtener_facturas(self, user_id=None):
        if not self.is_configured(): return []
        try:
            uid = user_id or self.get_current_user_id()
            query = self._db.collection("facturas")
            if uid:
                query = query.where("user_id", "==", uid)
            docs = query.stream()
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
            if not datos.get("user_id"):
                datos["user_id"] = self.get_current_user_id()
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

    def obtener_todas_recetas(self, user_id=None):
        if not self.is_configured(): return []
        try:
            uid = user_id or self.get_current_user_id()
            query = self._db.collection("recetas")
            if uid:
                query = query.where("user_id", "==", uid)
            docs = query.stream()
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
            if not datos.get("user_id"):
                datos["user_id"] = self.get_current_user_id()
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("farmacos").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_farmaco: {e}")
            return None

    def obtener_farmacos(self, user_id=None):
        if not self.is_configured(): return []
        try:
            uid = user_id or self.get_current_user_id()
            docs = self._db.collection("farmacos").stream()
            items = []
            for doc in docs:
                d = doc.to_dict() | {"id": doc.id}
                doc_uid = d.get("user_id")
                if not doc_uid or doc_uid == uid or d.get("is_global"):
                    items.append(d)
            return items
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
        """Crear una historia clínica completa en Firestore vinculada al usuario."""
        if not self.is_configured(): return None
        try:
            if not datos.get("user_id"):
                datos["user_id"] = self.get_current_user_id()
            datos["created_at"] = firestore.SERVER_TIMESTAMP
            datos["updated_at"] = firestore.SERVER_TIMESTAMP
            ref = self._db.collection("historias_clinicas").add(datos)
            return ref[1].id
        except Exception as e:
            print(f"[ERROR] crear_historia_clinica: {e}")
            return None

    def obtener_historias_clinicas(self, user_id=None):
        """Listar historias clínicas del usuario actual."""
        if not self.is_configured(): return []
        try:
            uid = user_id or self.get_current_user_id()
            query = self._db.collection("historias_clinicas")
            if uid:
                query = query.where("user_id", "==", uid)
            docs = query.stream()
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
