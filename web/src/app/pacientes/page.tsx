"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Plus,
  Edit3,
  Trash2,
  FileDown,
  X,
  FolderDown,
  FileHeart,
  CalendarDays,
  Pill,
  AlertCircle,
  Filter,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch, downloadPdf } from "@/lib/api";

interface Paciente {
  id: string;
  nombre: string;
  cedula: string;
  sexo?: string;
  fecha_nac?: string;
  edad?: string;
  estado_civil?: string;
  aseguradora?: string;
  email?: string;
  domicilio?: string;
  telefono?: string;
  otros_datos?: string;
  pnf?: string;
  trayecto?: string;
  seccion?: string;
  anio_academico?: string;
}

interface Historia {
  id: string;
  paciente_id?: string;
  cedula?: string;
}

interface Catalogs {
  pnf: string[];
  pnf_trayectos: Record<string, string[]>;
}

const EMAIL_DOMAINS = [
  "gmail.com",
  "hotmail.com",
  "outlook.com",
  "outlook.es",
  "yahoo.com",
  "icloud.com",
];

const TEL_PREFIXES = ["0412", "0414", "0424", "0416", "0426", "0212"];
const CEDULA_TYPES = ["V-", "E-", "J-", "P-"];

function calcEdadFromDate(fechaIso: string): string {
  if (!fechaIso) return "";
  const nac = new Date(fechaIso + "T00:00:00");
  const hoy = new Date();
  if (isNaN(nac.getTime()) || nac > hoy) return "";
  let age = hoy.getFullYear() - nac.getFullYear();
  const m = hoy.getMonth() - nac.getMonth();
  if (m < 0 || (m === 0 && hoy.getDate() < nac.getDate())) age--;
  return age >= 0 ? `${age} años` : "";
}

function splitCedula(raw: string): { tipo: string; num: string } {
  const s = (raw || "").trim();
  for (const t of CEDULA_TYPES) {
    if (s.toUpperCase().startsWith(t)) {
      return { tipo: t, num: s.slice(t.length).replace(/\D/g, "") };
    }
  }
  return { tipo: "V-", num: s.replace(/\D/g, "") };
}

function splitTelefono(raw: string): { prefijo: string; num: string } {
  const digits = (raw || "").replace(/\D/g, "");
  if (digits.length >= 11) {
    const p = digits.slice(0, 4);
    if (TEL_PREFIXES.includes(p)) return { prefijo: p, num: digits.slice(4, 11) };
  }
  return { prefijo: "0414", num: digits.slice(-7) };
}

function normalizeSeccion(raw: string): string {
  const v = (raw || "").trim();
  if (!v) return "";
  if (/^\d+$/.test(v)) {
    const n = parseInt(v, 10);
    if (n >= 1 && n <= 99) return n.toString().padStart(2, "0");
  }
  return v;
}

const EMPTY_FORM = {
  nombre: "",
  tipo_cedula: "V-",
  cedula_num: "",
  sexo: "Masculino",
  fecha_nac_iso: "",
  edad: "",
  estado_civil: "Soltero(a)",
  aseguradora: "",
  email: "",
  domicilio: "",
  tel_prefijo: "0414",
  tel_num: "",
  otros_datos: "",
  pnf: "No aplica / Externo",
  trayecto: "",
  seccion: "",
  anio_academico: "",
};

export default function PacientesPage() {
  const router = useRouter();
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [historias, setHistorias] = useState<Historia[]>([]);
  const [catalogs, setCatalogs] = useState<Catalogs | null>(null);
  const [search, setSearch] = useState("");
  const [filterPnf, setFilterPnf] = useState("");
  const [filterTrayecto, setFilterTrayecto] = useState("");
  const [filterSeccion, setFilterSeccion] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const loadData = async () => {
    setLoading(true);
    try {
      const [pList, hList, cat] = await Promise.all([
        apiFetch<Paciente[]>("/api/pacientes"),
        apiFetch<Historia[]>("/api/historias"),
        apiFetch<Catalogs>("/api/catalogs"),
      ]);
      setPacientes(pList);
      setHistorias(hList);
      setCatalogs(cat);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error cargando pacientes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return pacientes.filter((p) => {
      if (q) {
        const matchQ =
          (p.nombre || "").toLowerCase().includes(q) ||
          (p.cedula || "").toLowerCase().includes(q) ||
          (p.pnf || "").toLowerCase().includes(q);
        if (!matchQ) return false;
      }
      if (filterPnf && (p.pnf || "") !== filterPnf) return false;
      if (filterTrayecto && (p.trayecto || "") !== filterTrayecto) return false;
      if (filterSeccion && (p.seccion || "") !== filterSeccion) return false;
      return true;
    });
  }, [pacientes, search, filterPnf, filterTrayecto, filterSeccion]);

  const seccionesDisponibles = useMemo(() => {
    const set = new Set<string>();
    pacientes.forEach((p) => {
      if (p.seccion) set.add(p.seccion);
    });
    return Array.from(set).sort();
  }, [pacientes]);

  const openNew = () => {
    setEditingId(null);
    setForm({
      ...EMPTY_FORM,
      anio_academico: new Date().getFullYear().toString(),
    });
    setError("");
    setModalOpen(true);
  };

  const openEdit = (p: Paciente) => {
    const ced = splitCedula(p.cedula || "");
    const tel = splitTelefono(p.telefono || "");
    let fechaIso = "";
    if (p.fecha_nac && /^\d{2}\/\d{2}\/\d{4}$/.test(p.fecha_nac)) {
      const [dd, mm, yyyy] = p.fecha_nac.split("/");
      fechaIso = `${yyyy}-${mm}-${dd}`;
    } else if (p.fecha_nac && /^\d{4}-\d{2}-\d{2}$/.test(p.fecha_nac)) {
      fechaIso = p.fecha_nac;
    }

    setEditingId(p.id);
    setForm({
      nombre: p.nombre || "",
      tipo_cedula: ced.tipo,
      cedula_num: ced.num,
      sexo: p.sexo || "Masculino",
      fecha_nac_iso: fechaIso,
      edad: p.edad || calcEdadFromDate(fechaIso),
      estado_civil: p.estado_civil || "Soltero(a)",
      aseguradora: p.aseguradora || "",
      email: p.email || "",
      domicilio: p.domicilio || "",
      tel_prefijo: tel.prefijo,
      tel_num: tel.num,
      otros_datos: p.otros_datos || "",
      pnf: p.pnf || "No aplica / Externo",
      trayecto: p.trayecto || "",
      seccion: p.seccion || "",
      anio_academico: p.anio_academico || "",
    });
    setError("");
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const cedNum = form.cedula_num.trim();
    if (!/^\d{6,9}$/.test(cedNum) || new Set(cedNum).size === 1) {
      setError("La cédula debe contener entre 6 y 9 dígitos numéricos válidos.");
      return;
    }

    const cedulaCompleta = `${form.tipo_cedula}${cedNum}`;
    const duplicado = pacientes.find(
      (p) =>
        (p.cedula || "").trim().toLowerCase() === cedulaCompleta.toLowerCase() &&
        p.id !== editingId
    );
    if (duplicado) {
      setError(
        `Ya existe un paciente registrado con la cédula ${cedulaCompleta} (${duplicado.nombre}).`
      );
      return;
    }

    const telNum = form.tel_num.trim();
    if (telNum && !/^\d{7}$/.test(telNum)) {
      setError("El teléfono debe tener exactamente 7 dígitos después del prefijo.");
      return;
    }

    const telefonoCompleto = telNum ? `${form.tel_prefijo}-${telNum}` : "";
    const seccionNorm = normalizeSeccion(form.seccion);
    let fechaNacDmy = "";
    if (form.fecha_nac_iso) {
      const [y, m, d] = form.fecha_nac_iso.split("-");
      fechaNacDmy = `${d}/${m}/${y}`;
    }

    const payload = {
      nombre: form.nombre.trim(),
      cedula: cedulaCompleta,
      sexo: form.sexo,
      fecha_nac: fechaNacDmy,
      edad: form.edad || calcEdadFromDate(form.fecha_nac_iso),
      estado_civil: form.estado_civil,
      aseguradora: form.aseguradora.trim(),
      email: form.email.trim(),
      domicilio: form.domicilio.trim(),
      telefono: telefonoCompleto,
      otros_datos: form.otros_datos.trim(),
      motivo_consulta: form.otros_datos.trim(),
      pnf: form.pnf,
      trayecto: form.pnf === "No aplica / Externo" ? "" : form.trayecto,
      seccion: form.pnf === "No aplica / Externo" ? "" : seccionNorm,
      anio_academico: form.pnf === "No aplica / Externo" ? "" : form.anio_academico,
    };

    setSaving(true);
    try {
      if (editingId) {
        await apiFetch(`/api/pacientes/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        // Sincronizar hacia Historia Clínica si ya existe
        const hc = historias.find((h) => h.paciente_id === editingId);
        if (hc) {
          await apiFetch(`/api/historias/${hc.id}`, {
            method: "PUT",
            body: JSON.stringify({
              nombre: payload.nombre,
              cedula: payload.cedula,
              sexo: payload.sexo,
              edad: payload.edad,
              telefono: payload.telefono,
              direccion: payload.domicilio,
              pnf: payload.pnf,
              trayecto: payload.trayecto,
              seccion: payload.seccion,
            }),
          });
        }
      } else {
        await apiFetch("/api/pacientes", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      setModalOpen(false);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string, nombre: string) => {
    if (!confirm(`¿Desactivar al paciente "${nombre}"?`)) return;
    await apiFetch(`/api/pacientes/${id}`, { method: "DELETE" });
    await loadData();
  };

  const handleExportExpediente = async (p: Paciente) => {
    const [sesiones, recetas] = await Promise.all([
      apiFetch<unknown[]>(`/api/sesiones?paciente_id=${p.id}`),
      apiFetch<unknown[]>(`/api/recetas?paciente_id=${p.id}`),
    ]);
    await downloadPdf(
      "/api/pdf/expediente",
      { paciente: p, sesiones, recetas },
      `Expediente_${(p.nombre || "Paciente").replace(/\s+/g, "_")}.pdf`
    );
  };

  const trayectos = catalogs?.pnf_trayectos?.[form.pnf] || [];
  const emailSuggestions = useMemo(() => {
    const val = form.email;
    if (!val || val.includes("@")) return [];
    return EMAIL_DOMAINS.map((d) => `${val}@${d}`);
  }, [form.email]);

  return (
    <AppShell
      title="Identificación y Directorio de Pacientes"
      subtitle={`${filtered.length} de ${pacientes.length} pacientes activos`}
      actions={
        <div className="flex items-center gap-2">
          <button
            onClick={() =>
              downloadPdf(
                "/api/pdf/listado-pacientes",
                {
                  pacientes: filtered,
                  filtros: {
                    busqueda: search,
                    pnf: filterPnf,
                    trayecto: filterTrayecto,
                    seccion: filterSeccion,
                  },
                },
                "Listado_Pacientes_PSIQUE.pdf"
              )
            }
            className="px-3.5 py-2 text-xs font-medium rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] hover:bg-[var(--bg-subtle)] flex items-center gap-1.5"
          >
            <FileDown className="w-3.5 h-3.5" />
            <span>Exportar Listado PDF</span>
          </button>
          <button
            onClick={openNew}
            className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Registrar Paciente</span>
          </button>
        </div>
      }
    >
      {/* Search + Filters */}
      <div className="clinical-card p-4 mb-5 space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar por nombre, cédula o PNF..."
              className="clinical-input w-full pl-10"
            />
          </div>
          <button
            type="button"
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3.5 py-2 text-xs font-medium rounded-lg border flex items-center gap-1.5 ${
              showFilters || filterPnf || filterTrayecto || filterSeccion
                ? "border-[#2A72DE] text-[#2A72DE] bg-blue-50/50 dark:bg-blue-950/30"
                : "border-[var(--border-color)] hover:bg-[var(--bg-subtle)]"
            }`}
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Filtros Académicos</span>
          </button>
          {(search || filterPnf || filterTrayecto || filterSeccion) && (
            <button
              type="button"
              onClick={() => {
                setSearch("");
                setFilterPnf("");
                setFilterTrayecto("");
                setFilterSeccion("");
              }}
              className="text-xs text-[var(--text-secondary)] hover:text-[var(--text-primary)] underline"
            >
              Limpiar
            </button>
          )}
        </div>

        {showFilters && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 border-t border-[var(--border-color)]">
            <select
              value={filterPnf}
              onChange={(e) => {
                setFilterPnf(e.target.value);
                setFilterTrayecto("");
              }}
              className="clinical-input text-xs"
            >
              <option value="">Todos los PNF</option>
              {(catalogs?.pnf || []).map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
            <select
              value={filterTrayecto}
              onChange={(e) => setFilterTrayecto(e.target.value)}
              className="clinical-input text-xs"
            >
              <option value="">Todos los Trayectos</option>
              {(filterPnf
                ? catalogs?.pnf_trayectos?.[filterPnf] || []
                : ["Trayecto I", "Trayecto II", "Trayecto III", "Trayecto IV", "Trayecto V"]
              ).map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <select
              value={filterSeccion}
              onChange={(e) => setFilterSeccion(e.target.value)}
              className="clinical-input text-xs"
            >
              <option value="">Todas las Secciones</option>
              {seccionesDisponibles.map((s) => (
                <option key={s} value={s}>
                  Sección {s}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="clinical-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border-color)] bg-[var(--bg-subtle)] text-[11px] font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                <th className="py-3 px-4">Paciente</th>
                <th className="py-3 px-4">Cédula</th>
                <th className="py-3 px-4">Contacto</th>
                <th className="py-3 px-4">PNF / Académico</th>
                <th className="py-3 px-4 text-right">Acciones Rápidas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-color)] text-sm">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    Cargando pacientes...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    No se encontraron pacientes con esos criterios.
                  </td>
                </tr>
              ) : (
                filtered.map((p) => (
                  <tr key={p.id} className="hover:bg-[var(--bg-subtle)]/50 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-[var(--text-primary)]">{p.nombre}</div>
                      <div className="text-xs text-[var(--text-secondary)]">
                        {p.sexo || "—"} {p.edad ? `· ${p.edad}` : ""}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono text-xs">{p.cedula || "—"}</td>
                    <td className="py-3 px-4 text-xs">
                      <div>{p.telefono || "—"}</div>
                      <div className="text-[var(--text-secondary)]">{p.email || ""}</div>
                    </td>
                    <td className="py-3 px-4 text-xs">
                      <div>{p.pnf || "Externo"}</div>
                      <div className="text-[var(--text-secondary)]">
                        {[p.trayecto, p.seccion ? `Sec. ${p.seccion}` : ""].filter(Boolean).join(" · ")}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="inline-flex items-center gap-1">
                        <button
                          onClick={() => router.push(`/historias?paciente_id=${p.id}`)}
                          title="Abrir Historia Clínica"
                          className="p-1.5 rounded-md hover:bg-indigo-50 text-indigo-600 dark:hover:bg-indigo-950/40"
                        >
                          <FileHeart className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => router.push(`/citas?paciente_id=${p.id}`)}
                          title="Agendar Cita"
                          className="p-1.5 rounded-md hover:bg-teal-50 text-[#0F766E] dark:hover:bg-teal-950/40"
                        >
                          <CalendarDays className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => router.push(`/recetas?paciente_id=${p.id}`)}
                          title="Recetar Fármaco"
                          className="p-1.5 rounded-md hover:bg-amber-50 text-amber-600 dark:hover:bg-amber-950/40"
                        >
                          <Pill className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleExportExpediente(p)}
                          title="Descargar Expediente Completo PDF"
                          className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#0F766E]"
                        >
                          <FolderDown className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openEdit(p)}
                          title="Editar"
                          className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#2A72DE]"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(p.id, p.nombre)}
                          title="Desactivar"
                          className="p-1.5 rounded-md hover:bg-red-50 text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <div className="clinical-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-color)]">
              <h2 className="text-base font-bold">
                {editingId ? "Editar Paciente" : "Registrar Nuevo Paciente"}
              </h2>
              <button onClick={() => setModalOpen(false)} className="p-1 rounded hover:bg-[var(--bg-subtle)]">
                <X className="w-4 h-4" />
              </button>
            </div>

            {error && (
              <div className="mb-4 flex items-start gap-2 p-3 rounded-lg bg-[var(--danger-bg)] border border-red-200 text-xs text-[var(--danger)]">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSave} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Nombre completo *
                </label>
                <input
                  required
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Cédula (6-9 dígitos) *
                </label>
                <div className="flex gap-2">
                  <select
                    value={form.tipo_cedula}
                    onChange={(e) => setForm({ ...form, tipo_cedula: e.target.value })}
                    className="clinical-input w-20"
                  >
                    {CEDULA_TYPES.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                  <input
                    required
                    maxLength={9}
                    placeholder="12345678"
                    value={form.cedula_num}
                    onChange={(e) =>
                      setForm({ ...form, cedula_num: e.target.value.replace(/\D/g, "") })
                    }
                    className="clinical-input flex-1 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Sexo
                </label>
                <select
                  value={form.sexo}
                  onChange={(e) => setForm({ ...form, sexo: e.target.value })}
                  className="clinical-input w-full"
                >
                  <option value="Masculino">Masculino</option>
                  <option value="Femenino">Femenino</option>
                  <option value="Otro">Otro</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Fecha de Nacimiento (calcula edad)
                </label>
                <input
                  type="date"
                  value={form.fecha_nac_iso}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      fecha_nac_iso: e.target.value,
                      edad: calcEdadFromDate(e.target.value),
                    })
                  }
                  className="clinical-input w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Edad (Automática)
                </label>
                <input
                  value={form.edad}
                  onChange={(e) => setForm({ ...form, edad: e.target.value })}
                  placeholder="Calculada al elegir fecha"
                  className="clinical-input w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Teléfono (Prefijo + 7 dígitos)
                </label>
                <div className="flex gap-2">
                  <select
                    value={form.tel_prefijo}
                    onChange={(e) => setForm({ ...form, tel_prefijo: e.target.value })}
                    className="clinical-input w-24"
                  >
                    {TEL_PREFIXES.map((p) => (
                      <option key={p} value={p}>
                        {p}
                      </option>
                    ))}
                  </select>
                  <input
                    maxLength={7}
                    placeholder="1234567"
                    value={form.tel_num}
                    onChange={(e) =>
                      setForm({ ...form, tel_num: e.target.value.replace(/\D/g, "") })
                    }
                    className="clinical-input flex-1 font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Correo electrónico
                </label>
                <input
                  type="email"
                  list="email-suggestions"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="clinical-input w-full"
                />
                <datalist id="email-suggestions">
                  {emailSuggestions.map((s) => (
                    <option key={s} value={s} />
                  ))}
                </datalist>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Estado Civil
                </label>
                <select
                  value={form.estado_civil}
                  onChange={(e) => setForm({ ...form, estado_civil: e.target.value })}
                  className="clinical-input w-full"
                >
                  <option value="Soltero(a)">Soltero(a)</option>
                  <option value="Casado(a)">Casado(a)</option>
                  <option value="Divorciado(a)">Divorciado(a)</option>
                  <option value="Viudo(a)">Viudo(a)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Aseguradora / Institución
                </label>
                <input
                  value={form.aseguradora}
                  onChange={(e) => setForm({ ...form, aseguradora: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Domicilio
                </label>
                <input
                  value={form.domicilio}
                  onChange={(e) => setForm({ ...form, domicilio: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  PNF / Programa Académico
                </label>
                <select
                  value={form.pnf}
                  onChange={(e) => setForm({ ...form, pnf: e.target.value, trayecto: "" })}
                  className="clinical-input w-full"
                >
                  {(catalogs?.pnf || ["No aplica / Externo"]).map((pnf) => (
                    <option key={pnf} value={pnf}>
                      {pnf}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Trayecto
                </label>
                <select
                  value={form.trayecto}
                  disabled={trayectos.length === 0}
                  onChange={(e) => setForm({ ...form, trayecto: e.target.value })}
                  className="clinical-input w-full disabled:opacity-50"
                >
                  <option value="">No aplica</option>
                  {trayectos.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Sección (normalizada 01, 02...)
                </label>
                <input
                  placeholder="01"
                  value={form.seccion}
                  onChange={(e) => setForm({ ...form, seccion: e.target.value })}
                  onBlur={() => setForm((f) => ({ ...f, seccion: normalizeSeccion(f.seccion) }))}
                  className="clinical-input w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Año Académico
                </label>
                <input
                  value={form.anio_academico}
                  onChange={(e) => setForm({ ...form, anio_academico: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Motivo de consulta / Observaciones
                </label>
                <textarea
                  rows={3}
                  value={form.otros_datos}
                  onChange={(e) => setForm({ ...form, otros_datos: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div className="sm:col-span-2 flex justify-end gap-2 pt-3 border-t border-[var(--border-color)]">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-subtle)]"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="clinical-btn-primary px-4 py-2 text-xs disabled:opacity-60"
                >
                  {saving ? "Guardando..." : editingId ? "Actualizar Paciente" : "Guardar Paciente"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
