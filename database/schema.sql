-- ============================================================
-- SISTEMA DE REGISTRO CLÍNICO — PSICOLOGÍA
-- Script de creación de base de datos para Supabase (PostgreSQL)
-- Versión: 1.0
-- Fecha: 2026-05-06
-- ============================================================

-- Habilitar extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ============================================================
-- ENUMERACIONES (TIPOS PERSONALIZADOS)
-- ============================================================

CREATE TYPE rol_usuario     AS ENUM ('admin', 'psicologo', 'recepcionista');
CREATE TYPE genero_paciente  AS ENUM ('masculino', 'femenino', 'otro', 'prefiero_no_decir');
CREATE TYPE estado_civil_tipo AS ENUM ('soltero', 'casado', 'divorciado', 'viudo', 'union_libre', 'otro');
CREATE TYPE modalidad_cita   AS ENUM ('presencial', 'virtual');
CREATE TYPE estado_cita      AS ENUM ('programada', 'completada', 'cancelada', 'no_asistio');
CREATE TYPE estado_emocional AS ENUM ('muy_mal', 'mal', 'regular', 'bien', 'muy_bien');
CREATE TYPE clasificacion_dx AS ENUM ('DSM-5', 'CIE-11', 'otro');
CREATE TYPE estado_pago      AS ENUM ('pendiente', 'pagado', 'anulado');
CREATE TYPE metodo_pago      AS ENUM ('efectivo', 'transferencia', 'tarjeta', 'seguro', 'otro');
CREATE TYPE tipo_documento   AS ENUM ('pdf', 'imagen', 'word', 'otro');


-- ============================================================
-- TABLA: USUARIOS
-- Nota: El 'id' corresponde al UUID generado por Supabase Auth.
--       Se usa auth.uid() en las políticas RLS.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.usuarios (
    id               UUID PRIMARY KEY DEFAULT auth.uid(),
    nombre_completo  VARCHAR(150) NOT NULL,
    email            VARCHAR(150) NOT NULL UNIQUE,
    rol              rol_usuario  NOT NULL DEFAULT 'recepcionista',
    activo           BOOLEAN      NOT NULL DEFAULT TRUE,
    avatar_url       TEXT,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.usuarios IS 'Usuarios con acceso al sistema clínico.';
COMMENT ON COLUMN public.usuarios.id IS 'UUID sincronizado con Supabase Auth (auth.users.id).';


-- ============================================================
-- TABLA: PSICOLOGOS
-- Perfil extendido vinculado a un usuario con rol "psicologo".
-- ============================================================

CREATE TABLE IF NOT EXISTS public.psicologos (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id        UUID NOT NULL UNIQUE REFERENCES public.usuarios(id) ON DELETE CASCADE,
    num_licencia      VARCHAR(50)  NOT NULL UNIQUE,
    especialidad      VARCHAR(100) NOT NULL,
    anios_experiencia INT          NOT NULL DEFAULT 0 CHECK (anios_experiencia >= 0),
    horario_atencion  TEXT,
    telefono_profesional VARCHAR(20),
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.psicologos IS 'Perfil profesional extendido del psicólogo.';


-- ============================================================
-- TABLA: PACIENTES
-- ============================================================

CREATE TABLE IF NOT EXISTS public.pacientes (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombres             VARCHAR(100) NOT NULL,
    apellidos           VARCHAR(100) NOT NULL,
    fecha_nacimiento    DATE         NOT NULL,
    genero              genero_paciente NOT NULL DEFAULT 'prefiero_no_decir',
    num_documento       VARCHAR(30)  NOT NULL UNIQUE,
    email               VARCHAR(150),
    telefono            VARCHAR(20),
    direccion           TEXT,
    estado_civil        estado_civil_tipo,
    ocupacion           VARCHAR(100),
    contacto_emergencia VARCHAR(150),
    tel_emergencia      VARCHAR(20),
    activo              BOOLEAN      NOT NULL DEFAULT TRUE,
    notas_generales     TEXT,
    fecha_registro      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.pacientes IS 'Datos personales y de contacto de cada paciente.';


-- ============================================================
-- TABLA: CITAS
-- ============================================================

CREATE TABLE IF NOT EXISTS public.citas (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id                 UUID NOT NULL REFERENCES public.pacientes(id)   ON DELETE RESTRICT,
    psicologo_id                UUID NOT NULL REFERENCES public.psicologos(id)  ON DELETE RESTRICT,
    fecha_hora                  TIMESTAMPTZ NOT NULL,
    duracion_min                INT  NOT NULL DEFAULT 50 CHECK (duracion_min > 0),
    motivo_consulta             TEXT,
    modalidad                   modalidad_cita NOT NULL DEFAULT 'presencial',
    estado                      estado_cita    NOT NULL DEFAULT 'programada',
    observaciones_cancelacion   TEXT,
    link_virtual                TEXT,
    created_by                  UUID REFERENCES public.usuarios(id),
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.citas IS 'Registro de todas las citas programadas entre paciente y psicólogo.';


-- ============================================================
-- TABLA: SESIONES_CLINICAS
-- Una sesión se genera al completar una cita.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.sesiones_clinicas (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cita_id                 UUID NOT NULL UNIQUE REFERENCES public.citas(id) ON DELETE RESTRICT,
    notas_sesion            TEXT,
    tecnicas_terapeuticas   TEXT,
    progreso_observado      TEXT,
    proximos_objetivos      TEXT,
    estado_emocional_inicio estado_emocional,
    estado_emocional_cierre estado_emocional,
    numero_sesion           INT  NOT NULL DEFAULT 1 CHECK (numero_sesion > 0),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.sesiones_clinicas IS 'Registro clínico detallado de cada sesión terapéutica.';


-- ============================================================
-- TABLA: DIAGNOSTICOS_CATALOGO
-- Catálogo de diagnósticos DSM-5 / CIE-11.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.diagnosticos_catalogo (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo         VARCHAR(20)       NOT NULL UNIQUE,
    clasificacion  clasificacion_dx  NOT NULL DEFAULT 'DSM-5',
    nombre         VARCHAR(200)      NOT NULL,
    descripcion    TEXT,
    activo         BOOLEAN           NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMPTZ       NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.diagnosticos_catalogo IS 'Catálogo de diagnósticos psicológicos según DSM-5 / CIE-11.';


-- ============================================================
-- TABLA: SESION_DIAGNOSTICO  (tabla intermedia N:M)
-- Una sesión puede tener varios diagnósticos, y un diagnóstico
-- puede aparecer en varias sesiones.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.sesion_diagnostico (
    sesion_id       UUID NOT NULL REFERENCES public.sesiones_clinicas(id)     ON DELETE CASCADE,
    diagnostico_id  UUID NOT NULL REFERENCES public.diagnosticos_catalogo(id) ON DELETE RESTRICT,
    observaciones   TEXT,
    es_principal    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (sesion_id, diagnostico_id)
);

COMMENT ON TABLE public.sesion_diagnostico IS 'Relación N:M entre sesiones clínicas y diagnósticos.';


-- ============================================================
-- TABLA: RECETAS
-- Indicaciones o medicamentos por sesión.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.recetas (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sesion_id             UUID NOT NULL REFERENCES public.sesiones_clinicas(id) ON DELETE CASCADE,
    medicamento_indicacion VARCHAR(200) NOT NULL,
    dosis                 VARCHAR(100),
    frecuencia            VARCHAR(100),
    duracion              VARCHAR(100),
    observaciones         TEXT,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.recetas IS 'Recetas o indicaciones terapéuticas generadas en una sesión.';


-- ============================================================
-- TABLA: FACTURAS
-- Control de cobros. Una por cita completada.
-- ============================================================

CREATE TABLE IF NOT EXISTS public.facturas (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cita_id         UUID NOT NULL UNIQUE REFERENCES public.citas(id) ON DELETE RESTRICT,
    numero_factura  VARCHAR(30)  NOT NULL UNIQUE,
    fecha_emision   DATE         NOT NULL DEFAULT CURRENT_DATE,
    monto_total     NUMERIC(10,2) NOT NULL CHECK (monto_total >= 0),
    descuento       NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (descuento >= 0),
    cobertura_seguro BOOLEAN     NOT NULL DEFAULT FALSE,
    nombre_seguro   VARCHAR(100),
    estado_pago     estado_pago  NOT NULL DEFAULT 'pendiente',
    metodo_pago     metodo_pago,
    notas           TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.facturas IS 'Facturación y control de pagos asociados a cada cita.';


-- ============================================================
-- TABLA: DOCUMENTOS
-- Archivos adjuntos al expediente del paciente (Supabase Storage).
-- ============================================================

CREATE TABLE IF NOT EXISTS public.documentos (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    paciente_id   UUID NOT NULL REFERENCES public.pacientes(id)  ON DELETE CASCADE,
    subido_por    UUID NOT NULL REFERENCES public.usuarios(id)   ON DELETE SET NULL,
    nombre_archivo VARCHAR(255) NOT NULL,
    tipo           tipo_documento NOT NULL DEFAULT 'pdf',
    url_storage    TEXT         NOT NULL,
    descripcion    TEXT,
    fecha_carga    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE public.documentos IS 'Documentos adjuntos al expediente clínico del paciente.';


-- ============================================================
-- ÍNDICES PARA OPTIMIZAR CONSULTAS FRECUENTES
-- ============================================================

CREATE INDEX idx_citas_paciente_id    ON public.citas(paciente_id);
CREATE INDEX idx_citas_psicologo_id   ON public.citas(psicologo_id);
CREATE INDEX idx_citas_fecha_hora     ON public.citas(fecha_hora);
CREATE INDEX idx_citas_estado         ON public.citas(estado);

CREATE INDEX idx_sesiones_cita_id     ON public.sesiones_clinicas(cita_id);

CREATE INDEX idx_pacientes_documento  ON public.pacientes(num_documento);
CREATE INDEX idx_pacientes_apellidos  ON public.pacientes(apellidos);

CREATE INDEX idx_facturas_estado_pago ON public.facturas(estado_pago);
CREATE INDEX idx_documentos_paciente  ON public.documentos(paciente_id);


-- ============================================================
-- FUNCIÓN: Actualizar 'updated_at' automáticamente
-- ============================================================

CREATE OR REPLACE FUNCTION public.fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER trg_usuarios_updated_at
    BEFORE UPDATE ON public.usuarios
    FOR EACH ROW EXECUTE FUNCTION public.fn_set_updated_at();

CREATE TRIGGER trg_psicologos_updated_at
    BEFORE UPDATE ON public.psicologos
    FOR EACH ROW EXECUTE FUNCTION public.fn_set_updated_at();

CREATE TRIGGER trg_pacientes_updated_at
    BEFORE UPDATE ON public.pacientes
    FOR EACH ROW EXECUTE FUNCTION public.fn_set_updated_at();

CREATE TRIGGER trg_citas_updated_at
    BEFORE UPDATE ON public.citas
    FOR EACH ROW EXECUTE FUNCTION public.fn_set_updated_at();

CREATE TRIGGER trg_sesiones_updated_at
    BEFORE UPDATE ON public.sesiones_clinicas
    FOR EACH ROW EXECUTE FUNCTION public.fn_set_updated_at();

CREATE TRIGGER trg_facturas_updated_at
    BEFORE UPDATE ON public.facturas
    FOR EACH ROW EXECUTE FUNCTION public.fn_set_updated_at();


-- ============================================================
-- FUNCIÓN: Sincronizar usuario nuevo desde Supabase Auth
-- Se llama automáticamente cuando alguien se registra.
-- ============================================================

CREATE OR REPLACE FUNCTION public.fn_handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.usuarios (id, nombre_completo, email, rol)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'nombre_completo', split_part(NEW.email, '@', 1)),
        NEW.email,
        'recepcionista'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger en auth.users (Supabase)
CREATE TRIGGER trg_on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.fn_handle_new_user();


-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================

ALTER TABLE public.usuarios           ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.psicologos         ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pacientes          ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.citas              ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sesiones_clinicas  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sesion_diagnostico ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.diagnosticos_catalogo ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recetas            ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.facturas           ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documentos         ENABLE ROW LEVEL SECURITY;


-- ── HELPER: función para obtener rol del usuario actual ──────
CREATE OR REPLACE FUNCTION public.fn_get_user_role()
RETURNS TEXT AS $$
    SELECT rol::TEXT FROM public.usuarios WHERE id = auth.uid();
$$ LANGUAGE sql SECURITY DEFINER;


-- ── USUARIOS ─────────────────────────────────────────────────

-- Admin: acceso total
CREATE POLICY pol_usuarios_admin_all ON public.usuarios
    FOR ALL USING (public.fn_get_user_role() = 'admin');

-- Usuarios normales: solo ver y editar su propio perfil
CREATE POLICY pol_usuarios_self_select ON public.usuarios
    FOR SELECT USING (id = auth.uid());

CREATE POLICY pol_usuarios_self_update ON public.usuarios
    FOR UPDATE USING (id = auth.uid());


-- ── PSICÓLOGOS ───────────────────────────────────────────────

CREATE POLICY pol_psicologos_admin ON public.psicologos
    FOR ALL USING (public.fn_get_user_role() = 'admin');

CREATE POLICY pol_psicologos_select ON public.psicologos
    FOR SELECT USING (TRUE);  -- Todos pueden ver la lista

CREATE POLICY pol_psicologos_self_update ON public.psicologos
    FOR UPDATE USING (usuario_id = auth.uid());


-- ── PACIENTES ────────────────────────────────────────────────

CREATE POLICY pol_pacientes_admin ON public.pacientes
    FOR ALL USING (public.fn_get_user_role() = 'admin');

CREATE POLICY pol_pacientes_staff ON public.pacientes
    FOR ALL USING (public.fn_get_user_role() IN ('recepcionista', 'psicologo'));


-- ── CITAS ────────────────────────────────────────────────────

CREATE POLICY pol_citas_admin ON public.citas
    FOR ALL USING (public.fn_get_user_role() = 'admin');

CREATE POLICY pol_citas_recepcionista ON public.citas
    FOR ALL USING (public.fn_get_user_role() = 'recepcionista');

-- Psicólogo: solo ve sus propias citas
CREATE POLICY pol_citas_psicologo ON public.citas
    FOR ALL USING (
        public.fn_get_user_role() = 'psicologo'
        AND psicologo_id = (
            SELECT id FROM public.psicologos WHERE usuario_id = auth.uid()
        )
    );


-- ── SESIONES CLÍNICAS ────────────────────────────────────────

CREATE POLICY pol_sesiones_admin ON public.sesiones_clinicas
    FOR ALL USING (public.fn_get_user_role() = 'admin');

-- Solo el psicólogo que atendió la cita puede ver/editar la sesión
CREATE POLICY pol_sesiones_psicologo ON public.sesiones_clinicas
    FOR ALL USING (
        public.fn_get_user_role() = 'psicologo'
        AND cita_id IN (
            SELECT c.id FROM public.citas c
            JOIN public.psicologos p ON p.id = c.psicologo_id
            WHERE p.usuario_id = auth.uid()
        )
    );


-- ── DIAGNÓSTICOS CATÁLOGO (solo lectura para todos) ──────────

CREATE POLICY pol_dx_catalogo_read ON public.diagnosticos_catalogo
    FOR SELECT USING (TRUE);

CREATE POLICY pol_dx_catalogo_admin ON public.diagnosticos_catalogo
    FOR ALL USING (public.fn_get_user_role() = 'admin');


-- ── SESION_DIAGNOSTICO ───────────────────────────────────────

CREATE POLICY pol_sesion_dx_admin ON public.sesion_diagnostico
    FOR ALL USING (public.fn_get_user_role() = 'admin');

CREATE POLICY pol_sesion_dx_psicologo ON public.sesion_diagnostico
    FOR ALL USING (
        public.fn_get_user_role() = 'psicologo'
        AND sesion_id IN (
            SELECT s.id FROM public.sesiones_clinicas s
            JOIN public.citas c ON c.id = s.cita_id
            JOIN public.psicologos p ON p.id = c.psicologo_id
            WHERE p.usuario_id = auth.uid()
        )
    );


-- ── RECETAS ──────────────────────────────────────────────────

CREATE POLICY pol_recetas_admin ON public.recetas
    FOR ALL USING (public.fn_get_user_role() = 'admin');

CREATE POLICY pol_recetas_psicologo ON public.recetas
    FOR ALL USING (
        public.fn_get_user_role() = 'psicologo'
        AND sesion_id IN (
            SELECT s.id FROM public.sesiones_clinicas s
            JOIN public.citas c ON c.id = s.cita_id
            JOIN public.psicologos p ON p.id = c.psicologo_id
            WHERE p.usuario_id = auth.uid()
        )
    );


-- ── FACTURAS ─────────────────────────────────────────────────

CREATE POLICY pol_facturas_admin ON public.facturas
    FOR ALL USING (public.fn_get_user_role() = 'admin');

CREATE POLICY pol_facturas_recepcionista ON public.facturas
    FOR ALL USING (public.fn_get_user_role() = 'recepcionista');

CREATE POLICY pol_facturas_psicologo_read ON public.facturas
    FOR SELECT USING (public.fn_get_user_role() = 'psicologo');


-- ── DOCUMENTOS ───────────────────────────────────────────────

CREATE POLICY pol_docs_admin ON public.documentos
    FOR ALL USING (public.fn_get_user_role() = 'admin');

CREATE POLICY pol_docs_staff ON public.documentos
    FOR ALL USING (public.fn_get_user_role() IN ('recepcionista', 'psicologo'));


-- ============================================================
-- DATOS SEMILLA (SEED) — Diagnósticos DSM-5 de ejemplo
-- ============================================================

INSERT INTO public.diagnosticos_catalogo (codigo, clasificacion, nombre, descripcion) VALUES
('F32.0',  'CIE-11', 'Episodio depresivo leve',                  'Humor deprimido, reducción de energía y disminución de actividad.'),
('F32.1',  'CIE-11', 'Episodio depresivo moderado',              'Dificultad para continuar con actividades ordinarias.'),
('F32.2',  'CIE-11', 'Episodio depresivo grave sin síntomas psicóticos', 'Angustia o agitación considerable, baja autoestima.'),
('F40.00', 'CIE-11', 'Agorafobia sin trastorno de pánico',       'Miedo a lugares o situaciones de las que puede ser difícil escapar.'),
('F40.10', 'CIE-11', 'Fobia social',                             'Miedo marcado y persistente a situaciones sociales.'),
('F41.0',  'CIE-11', 'Trastorno de pánico',                      'Ataques recurrentes e inesperados de pánico intenso.'),
('F41.1',  'CIE-11', 'Trastorno de ansiedad generalizada',       'Ansiedad y preocupación excesiva sobre varios eventos o actividades.'),
('F43.1',  'CIE-11', 'Trastorno por estrés postraumático (TEPT)','Reexperimentación de un trauma severo previo.'),
('F60.3',  'CIE-11', 'Trastorno límite de la personalidad',      'Patrón de inestabilidad en relaciones interpersonales, autoimagen e impulsividad.'),
('F90.0',  'CIE-11', 'Trastorno por déficit de atención con hiperactividad (TDAH)', 'Patrón de inatención y/o hiperactividad-impulsividad.'),
('296.21', 'DSM-5',  'Trastorno depresivo mayor, episodio único, leve',   'Un solo episodio depresivo mayor de intensidad leve.'),
('300.02', 'DSM-5',  'Trastorno de ansiedad generalizada',                'Ansiedad y preocupación excesiva, la mayoría de los días, por al menos 6 meses.'),
('309.81', 'DSM-5',  'Trastorno por estrés postraumático',                'Exposición a muerte real o amenaza, lesión grave o violencia sexual.'),
('314.01', 'DSM-5',  'TDAH, presentación combinada',                      'Cumple criterios de inatención e hiperactividad-impulsividad.'),
('301.83', 'DSM-5',  'Trastorno límite de la personalidad',               'Patrón dominante de inestabilidad de las relaciones interpersonales y de la autoimagen.')
ON CONFLICT (codigo) DO NOTHING;


-- ============================================================
-- FIN DEL SCRIPT
-- ============================================================
