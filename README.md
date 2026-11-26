# Sistema de Registro Clínico y Gestión Médica

Sistema de escritorio completo para la gestión de historias clínicas, pacientes, citas médicas, recetas, catálogo de fármacos y facturación, desarrollado en Python con **PyQt6** y sincronización en la nube mediante **Firebase**.

---

## 🚀 Características Principales

- **Gestión Integral de Pacientes:** Registro, historial clínico detallado, antecedentes patológicos y no patológicos.
- **Sesiones Clínicas y Consultas:** Registro de signos vitales, evolución médica, diagnósticos (CIE-10) y planes terapéuticos.
- **Generación de Recetas en PDF:** Impresión y exportación automatizada de recetas médicas con formato profesional mediante ReportLab.
- **Catálogo Farmacológico:** Búsqueda rápida de medicamentos por nombre comercial, principio activo, dosis e indicaciones.
- **Agenda y Citas:** Control y programación de turnos y consultas médicas.
- **Facturación y Cobros:** Módulo de seguimiento de pagos, presupuestos y estados de cuenta de pacientes.
- **Acceso Libre con Firebase Auth / Google:** Cualquier profesional registrado (correo/contraseña o Google Sign-In) puede ingresar directamente sin activación de licencia por hardware.
- **Versión Web + Escritorio Sincronizadas:** Incluye aplicación de escritorio (**PyQt6**) y plataforma web (**FastAPI** en `api/` + **Next.js** en `web/`) conectadas a la misma base de datos en **Firebase Firestore**.
- **Soporte Offline y Online:** Caché local en SQLite con sincronización automática hacia Firebase Firestore.

---

## 📂 Estructura del Proyecto

```text
registro_clinico/
├── api/                    # Backend REST en Python (FastAPI) para la versión web
├── web/                    # Frontend Web moderno en Next.js + Tailwind (Oura + Linear)
├── core/                   # Lógica de negocio (autenticación, sincronización, updater)
├── data/                   # Catálogos estáticos (medicamentos, diagnósticos, etc.)
├── database/               # Conexión Firebase y base de datos local SQLite (caché)
├── styles/                 # Hojas de estilo QSS e iconos de interfaz
├── ui/                     # Vistas principales y diálogos modales (PyQt6)
│   ├── dialogs/            # Calculadoras médicas, generador PDF, reportes
│   └── views/              # Vistas de pacientes, citas, recetas, dashboard, facturación
├── .env.example            # Plantilla de variables de entorno
├── build_exe.py            # Script automatizado para compilar a ejecutable (.exe)
├── installer_setup.iss     # Script para crear instalador de Windows con Inno Setup
├── install_linux.sh        # Instalador universal para Linux
├── main.py                 # Punto de entrada de la aplicación de escritorio
├── version.json            # Versión actual para el actualizador automático
└── requirements.txt        # Dependencias de Python
```

---

## 🛠️ Requisitos Previos

- **Python 3.10 o superior**
- Cuenta de **Google Firebase** con proyecto configurado (Firestore Database y Authentication).
- (Opcional) **Inno Setup 6** si deseas generar el instalador ejecutable `.exe`.

---

## ⚙️ Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd registro_clinico
   ```

2. **Crear y activar un entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno y credenciales:**
   - Copia `.env.example` a `.env`:
     ```bash
     copy .env.example .env
     ```
   - Completa las variables con las claves de tu proyecto Firebase.
   - Coloca tu archivo `firebase_service_account.json` en la raíz del proyecto para habilitar las funciones administrativas en Firestore.

5. **Ejecutar la aplicación de escritorio:**
   ```bash
   python main.py
   ```

6. **Ejecutar la versión Web (opcional, en dos terminales):**
   ```bash
   # Terminal 1: Backend FastAPI
   python -m uvicorn api.main:app --reload --port 8000

   # Terminal 2: Frontend Next.js
   cd web
   npm install
   npm run dev
   ```

---

## 📦 Compilación y Distribución

Para generar la carpeta distribuible y el ejecutable independiente:

```bash
python build_exe.py
```

El resultado se generará en la carpeta `dist/SistemaClinico/`. Luego, puedes compilar el archivo `installer_setup.iss` con Inno Setup para obtener el instalador final para Windows.

---

## 🔒 Seguridad y Privacidad

Por motivos de seguridad, los archivos de credenciales (`.env`, `firebase_service_account.json`), llaves criptográficas privadas (`.vault.key`, `keygen.py`) y archivos de compilación (`build/`, `dist/`) se encuentran excluidos del control de versiones mediante `.gitignore`.
