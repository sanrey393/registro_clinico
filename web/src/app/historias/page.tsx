"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Plus,
  FileDown,
  Edit3,
  Trash2,
  X,
  Search,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch, downloadPdf } from "@/lib/api";

interface Historia {
  id: string;
  num_historia?: string;
  fecha_ingreso?: string;
  paciente_id?: string;
  nombre: string;
  cedula: string;
  sexo?: string;
  fecha_nacimiento?: string;
  edad?: string;
  direccion?: string;
  telefono?: string;
  pnf?: string;
  trayecto?: string;
  seccion?: string;
  anio_academico?: string;
  motivo_consulta?: string;
  antecedentes_personales?: string;
  antecedentes_familiares?: string;
  antecedentes_medicos?: string;
  alergias?: string;
  medicacion_actual?: string;
  habitos?: string;
  representante_nombre?: string;
  representante_cedula?: string;
  representante_parentesco?: string;
  representante_telefono?: string;
  representante_direccion?: string;
  estado_animo?: string;
  sueno?: string;
  alimentacion?: string;
  relaciones?: string;
  observaciones_emocionales?: string;
  condicion_clinica?: string;
  diagnostico?: string;
  evaluacion_ipx?: string;
  plan_terapeutico?: string;
}

interface Paciente {
  id: string;
  nombre: string;
  cedula: string;
  sexo?: string;
  fecha_nac?: string;
  edad?: string;
  domicilio?: string;
  telefono?: string;
  pnf?: string;
  trayecto?: string;
  seccion?: string;
  anio_academico?: string;
  otros_datos?: string;
}

interface Sesion {
  id: string;
  paciente_id: string;
  fecha?: string;
  diagnostico?: string;
  evolucion?: string;
  notas?: string;
  plan_tratamiento?: string;
}

const PNF_CODES: Record<string, string> = {
  "Informática": "INF",
  "Agroalimentación": "AGR",
  "Administración de Empresas": "ADM",
  "Veterinaria": "VET",
  "No aplica / Externo": "EXT",
};

function generateHistoriaCode(pnf: string, cedula: string, anio: string): string {
  const code = PNF_CODES[pnf] || "GEN";
  const digits = (cedula || "").replace(/\D/g, "");
  const yr = (anio || "").replace(/\D/g, "").slice(0, 4);
  if (digits) {
    if (yr && pnf && pnf !== "No aplica / Externo") {
      return `HC-${code}-${yr}-${digits}`;
    }
    return `HC-${code}-${digits}`;
  }
  return `HC-${code}-001`;
}

const EMPTY_HC = {
  num_historia: "",
  fecha_ingreso: "",
  paciente_id: "",
  nombre: "",
  cedula: "",
  sexo: "Masculino",
  fecha_nacimiento: "",
  edad: "",
  direccion: "",
  telefono: "",
  pnf: "No aplica / Externo",
  trayecto: "",
  seccion: "",
  anio_academico: "",
  motivo_consulta: "",
  antecedentes_personales: "",
  antecedentes_familiares: "",
  antecedentes_medicos: "",
  alergias: "",
  medicacion_actual: "",
  habitos: "",
  representante_nombre: "",
  representante_cedula: "",
  representante_parentesco: "",
  representante_telefono: "",
  representante_direccion: "",
  estado_animo: "",
  sueno: "",
  alimentacion: "",
  relaciones: "",
  observaciones_emocionales: "",
  condicion_clinica: "Sin especificar",
  diagnostico: "",
  evaluacion_ipx: "",
  plan_terapeutico: "",
};

function HistoriasContent() {
  const searchParams = useSearchParams();
  const targetPacienteId = searchParams.get("paciente_id");

  const [historias, setHistorias] = useState<Historia[]>([]);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [condiciones, setCondiciones] = useState<string[]>([]);
  const [cie10, setCie10] = useState<Array<{ codigo: string; descripcion: string }>>([]);
  const [pnfList, setPnfList] = useState<string[]>([]);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState(EMPTY_HC);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState("");

  // Condición personalizada
  const [newCondicion, setNewCondicion] = useState("");

  // Tab 6: Evolución del paciente
  const [sesionesPaciente, setSesionesPaciente] = useState<Sesion[]>([]);
  const [newEvo, setNewEvo] = useState({ diagnostico: "", evolucion: "", plan_tratamiento: "" });
  const [savingEvo, setSavingEvo] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [hList, pList, cat] = await Promise.all([
        apiFetch<Historia[]>("/api/historias"),
        apiFetch<Paciente[]>("/api/pacientes"),
        apiFetch<{
          condiciones_clinicas: string[];
          cie10: Array<{ codigo: string; descripcion: string }>;
          pnf: string[];
        }>("/api/catalogs"),
      ]);
      setHistorias(hList);
      setPacientes(pList);
      setCondiciones(cat.condiciones_clinicas || []);
      setCie10(cat.cie10 || []);
      setPnfList(cat.pnf || ["No aplica / Externo"]);
      return { hList, pList };
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData().then((res) => {
      if (targetPacienteId && res) {
        const existingHc = res.hList.find((h) => h.paciente_id === targetPacienteId);
        if (existingHc) {
          openEdit(existingHc);
        } else {
          const pac = res.pList.find((p) => p.id === targetPacienteId);
          if (pac) {
            openNewForPaciente(pac);
          }
        }
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetPacienteId]);

  const loadSesionesPaciente = async (pacienteId: string) => {
    if (!pacienteId) {
      setSesionesPaciente([]);
      return;
    }
    const items = await apiFetch<Sesion[]>(`/api/sesiones?paciente_id=${pacienteId}`);
    setSesionesPaciente(items);
  };

  const openNewForPaciente = (p: Paciente) => {
    setEditingId(null);
    setActiveTab(0);
    setNotice("");
    const code = generateHistoriaCode(
      p.pnf || "No aplica / Externo",
      p.cedula || "",
      p.anio_academico || new Date().getFullYear().toString()
    );
    setForm({
      ...EMPTY_HC,
      fecha_ingreso: new Date().toISOString().slice(0, 10),
      paciente_id: p.id,
      nombre: p.nombre || "",
      cedula: p.cedula || "",
      sexo: p.sexo || "Masculino",
      fecha_nacimiento: p.fecha_nac || "",
      edad: p.edad || "",
      direccion: p.domicilio || "",
      telefono: p.telefono || "",
      pnf: p.pnf || "No aplica / Externo",
      trayecto: p.trayecto || "",
      seccion: p.seccion || "",
      anio_academico: p.anio_academico || "",
      motivo_consulta: p.otros_datos || "",
      num_historia: code,
    });
    loadSesionesPaciente(p.id);
    setModalOpen(true);
  };

  const handleSelectPaciente = (pid: string) => {
    const existingHc = historias.find((h) => h.paciente_id === pid);
    if (existingHc) {
      openEdit(existingHc);
      setNotice("Regla 1-a-1: Se cargó la Historia Clínica existente de este paciente.");
      return;
    }
    const p = pacientes.find((x) => x.id === pid);
    if (!p) {
      setForm((f) => ({ ...f, paciente_id: "" }));
      setSesionesPaciente([]);
      return;
    }
    const code = generateHistoriaCode(
      p.pnf || "No aplica / Externo",
      p.cedula || "",
      p.anio_academico || new Date().getFullYear().toString()
    );
    setForm((f) => ({
      ...f,
      paciente_id: p.id,
      nombre: p.nombre,
      cedula: p.cedula,
      sexo: p.sexo || "Masculino",
      fecha_nacimiento: p.fecha_nac || "",
      edad: p.edad || "",
      direccion: p.domicilio || "",
      telefono: p.telefono || "",
      pnf: p.pnf || "No aplica / Externo",
      trayecto: p.trayecto || "",
      seccion: p.seccion || "",
      anio_academico: p.anio_academico || "",
      motivo_consulta: f.motivo_consulta || p.otros_datos || "",
      num_historia: f.num_historia || code,
    }));
    loadSesionesPaciente(p.id);
  };

  const openNew = () => {
    setEditingId(null);
    setActiveTab(0);
    setNotice("");
    setSesionesPaciente([]);
    setForm({
      ...EMPTY_HC,
      fecha_ingreso: new Date().toISOString().slice(0, 10),
    });
    setModalOpen(true);
  };

  const openEdit = (h: Historia) => {
    setEditingId(h.id);
    setActiveTab(0);
    setNotice("");
    setForm({
      ...EMPTY_HC,
      ...h,
    });
    loadSesionesPaciente(h.paciente_id || "");
    setModalOpen(true);
  };

  const handleAddCondicion = async () => {
    const val = newCondicion.trim();
    if (!val) return;
    await apiFetch("/api/catalogs/condiciones", {
      method: "POST",
      body: JSON.stringify({ nombre: val }),
    });
    setCondiciones((prev) => Array.from(new Set([...prev, val])).sort());
    setForm((f) => ({ ...f, condicion_clinica: val }));
    setNewCondicion("");
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      let pid = form.paciente_id;
      // Sincronización con Paciente (crear si no existe, actualizar si existe)
      const pacPayload = {
        nombre: form.nombre,
        cedula: form.cedula,
        sexo: form.sexo,
        fecha_nac: form.fecha_nacimiento,
        edad: form.edad,
        domicilio: form.direccion,
        telefono: form.telefono,
        pnf: form.pnf,
        trayecto: form.trayecto,
        seccion: form.seccion,
        anio_academico: form.anio_academico,
        motivo_consulta: form.motivo_consulta,
      };
      if (pid) {
        await apiFetch(`/api/pacientes/${pid}`, {
          method: "PUT",
          body: JSON.stringify(pacPayload),
        });
      } else if (form.cedula.trim()) {
        const createdPac = await apiFetch<Paciente>("/api/pacientes", {
          method: "POST",
          body: JSON.stringify(pacPayload),
        });
        pid = createdPac.id;
      }

      const hcPayload = { ...form, paciente_id: pid };
      if (editingId) {
        await apiFetch(`/api/historias/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(hcPayload),
        });
      } else {
        await apiFetch("/api/historias", {
          method: "POST",
          body: JSON.stringify(hcPayload),
        });
      }
      setModalOpen(false);
      await loadData();
    } finally {
      setSaving(false);
    }
  };

  const handleAddEvolucion = async () => {
    if (!form.paciente_id || !newEvo.evolucion.trim()) return;
    setSavingEvo(true);
    try {
      await apiFetch("/api/sesiones", {
        method: "POST",
        body: JSON.stringify({
          paciente_id: form.paciente_id,
          paciente_nombre: form.nombre,
          paciente_cedula: form.cedula,
          fecha: new Date().toISOString().slice(0, 10),
          diagnostico: newEvo.diagnostico || form.diagnostico,
          evolucion: newEvo.evolucion,
          notas: newEvo.evolucion,
          plan_tratamiento: newEvo.plan_tratamiento,
        }),
      });
      setNewEvo({ diagnostico: "", evolucion: "", plan_tratamiento: "" });
      await loadSesionesPaciente(form.paciente_id);
    } finally {
      setSavingEvo(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar esta historia clínica?")) return;
    await apiFetch(`/api/historias/${id}`, { method: "DELETE" });
    await loadData();
  };

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return historias;
    return historias.filter(
      (h) =>
        (h.nombre || "").toLowerCase().includes(q) ||
        (h.cedula || "").toLowerCase().includes(q) ||
        (h.num_historia || "").toLowerCase().includes(q) ||
        (h.condicion_clinica || "").toLowerCase().includes(q)
    );
  }, [historias, search]);

  const TABS = [
    "1. Filiación",
    "2. Antecedentes",
    "3. Representante",
    "4. Autoexploración",
    "5. Neuro / IPX",
    "6. Evolución",
  ];

  return (
    <AppShell
      title="Historias Clínicas (Expediente Integral)"
      subtitle={`${historias.length} historias registradas · Regla 1-a-1 por paciente`}
      actions={
        <div className="flex items-center gap-2">
          <button
            onClick={() =>
              downloadPdf(
                "/api/pdf/listado-historias",
                { historias: filtered, filtros: { busqueda: search } },
                "Listado_Historias_PSIQUE.pdf"
              )
            }
            className="px-3.5 py-2 text-xs font-medium rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] hover:bg-[var(--bg-subtle)] flex items-center gap-1.5"
          >
            <FileDown className="w-3.5 h-3.5" />
            <span>Listado PDF</span>
          </button>
          <button
            onClick={openNew}
            className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Nueva Historia</span>
          </button>
        </div>
      }
    >
      <div className="clinical-card p-4 mb-5">
        <div className="relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por N° historia, paciente, cédula o condición..."
            className="clinical-input w-full pl-10"
          />
        </div>
      </div>

      <div className="clinical-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border-color)] bg-[var(--bg-subtle)] text-[11px] font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                <th className="py-3 px-4">N° Historia</th>
                <th className="py-3 px-4">Paciente</th>
                <th className="py-3 px-4">Condición / Diagnóstico</th>
                <th className="py-3 px-4 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-color)] text-sm">
              {loading ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    Cargando historias...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    No hay historias clínicas registradas.
                  </td>
                </tr>
              ) : (
                filtered.map((h) => (
                  <tr key={h.id} className="hover:bg-[var(--bg-subtle)]/50">
                    <td className="py-3 px-4 font-mono text-xs font-semibold text-[#0F766E]">
                      {h.num_historia || "—"}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold">{h.nombre}</div>
                      <div className="text-xs text-[var(--text-secondary)]">{h.cedula}</div>
                    </td>
                    <td className="py-3 px-4 text-xs">
                      <div className="font-medium">{h.condicion_clinica || "Sin especificar"}</div>
                      <div className="text-[var(--text-secondary)] truncate max-w-xs">
                        {h.diagnostico || h.motivo_consulta || ""}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="inline-flex items-center gap-1">
                        <button
                          onClick={() =>
                            downloadPdf(
                              "/api/pdf/historia",
                              h,
                              `Historia_${(h.nombre || "Paciente").replace(/\s+/g, "_")}.pdf`
                            )
                          }
                          title="Exportar Historia PDF"
                          className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#0F766E]"
                        >
                          <FileDown className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openEdit(h)}
                          title="Abrir Expediente"
                          className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#2A72DE]"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(h.id)}
                          title="Eliminar"
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

      {/* 6-Tab Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <div className="clinical-card w-full max-w-4xl max-h-[92vh] flex flex-col overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-[var(--border-color)] flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold">
                  {editingId ? `Expediente: ${form.num_historia || form.nombre}` : "Nueva Historia Clínica"}
                </h2>
                {notice && (
                  <p className="text-xs text-[#0F766E] flex items-center gap-1 mt-0.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>{notice}</span>
                  </p>
                )}
              </div>
              <button onClick={() => setModalOpen(false)} className="p-1 rounded hover:bg-[var(--bg-subtle)]">
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Tabs */}
            <div className="px-6 pt-3 border-b border-[var(--border-color)] flex gap-1 overflow-x-auto bg-[var(--bg-subtle)]/50">
              {TABS.map((t, idx) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setActiveTab(idx)}
                  className={`px-3 py-2 text-xs font-semibold rounded-t-lg whitespace-nowrap border-b-2 transition-colors ${
                    activeTab === idx
                      ? "border-[#2A72DE] text-[#2A72DE] bg-[var(--bg-surface)]"
                      : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>

            {/* Body */}
            <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-4">
              {activeTab === 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Vincular Paciente existente
                    </label>
                    <select
                      value={form.paciente_id}
                      onChange={(e) => handleSelectPaciente(e.target.value)}
                      className="clinical-input w-full"
                    >
                      <option value="">Manual / Nuevo</option>
                      {pacientes.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.nombre} ({p.cedula})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      N° de Historia *
                    </label>
                    <div className="flex gap-2">
                      <input
                        required
                        value={form.num_historia}
                        onChange={(e) => setForm({ ...form, num_historia: e.target.value.toUpperCase() })}
                        className="clinical-input flex-1 font-mono"
                      />
                      <button
                        type="button"
                        onClick={() =>
                          setForm((f) => ({
                            ...f,
                            num_historia: generateHistoriaCode(f.pnf, f.cedula, f.anio_academico),
                          }))
                        }
                        title="Autogenerar código"
                        className="px-2.5 rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-subtle)] text-[#0F766E]"
                      >
                        <Sparkles className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div>
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
                      Cédula *
                    </label>
                    <input
                      required
                      value={form.cedula}
                      onChange={(e) => setForm({ ...form, cedula: e.target.value })}
                      className="clinical-input w-full font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Fecha de Ingreso
                    </label>
                    <input
                      type="date"
                      value={form.fecha_ingreso}
                      onChange={(e) => setForm({ ...form, fecha_ingreso: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Teléfono
                    </label>
                    <input
                      value={form.telefono}
                      onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      PNF / Programa
                    </label>
                    <select
                      value={form.pnf}
                      onChange={(e) => setForm({ ...form, pnf: e.target.value })}
                      className="clinical-input w-full"
                    >
                      {pnfList.map((p) => (
                        <option key={p} value={p}>
                          {p}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Edad
                    </label>
                    <input
                      value={form.edad}
                      onChange={(e) => setForm({ ...form, edad: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Dirección / Domicilio
                    </label>
                    <input
                      value={form.direccion}
                      onChange={(e) => setForm({ ...form, direccion: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                </div>
              )}

              {activeTab === 1 && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Antecedentes Personales
                    </label>
                    <textarea
                      rows={2}
                      value={form.antecedentes_personales}
                      onChange={(e) => setForm({ ...form, antecedentes_personales: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Antecedentes Familiares
                    </label>
                    <textarea
                      rows={2}
                      value={form.antecedentes_familiares}
                      onChange={(e) => setForm({ ...form, antecedentes_familiares: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Alergias (Importante para alertas de recetas)
                      </label>
                      <input
                        value={form.alergias}
                        onChange={(e) => setForm({ ...form, alergias: e.target.value })}
                        placeholder="Ej. Penicilina, AINEs..."
                        className="clinical-input w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Medicación Actual
                      </label>
                      <input
                        value={form.medicacion_actual}
                        onChange={(e) => setForm({ ...form, medicacion_actual: e.target.value })}
                        className="clinical-input w-full"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Antecedentes Médicos y Quirúrgicos
                    </label>
                    <textarea
                      rows={2}
                      value={form.antecedentes_medicos}
                      onChange={(e) => setForm({ ...form, antecedentes_medicos: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Hábitos (sueño, alimentación, sustancias)
                    </label>
                    <textarea
                      rows={2}
                      value={form.habitos}
                      onChange={(e) => setForm({ ...form, habitos: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                </div>
              )}

              {activeTab === 2 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Nombre del Representante / Acudiente
                    </label>
                    <input
                      value={form.representante_nombre}
                      onChange={(e) => setForm({ ...form, representante_nombre: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Cédula del Representante
                    </label>
                    <input
                      value={form.representante_cedula}
                      onChange={(e) => setForm({ ...form, representante_cedula: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Parentesco
                    </label>
                    <input
                      placeholder="Madre, Padre, Tutor..."
                      value={form.representante_parentesco}
                      onChange={(e) => setForm({ ...form, representante_parentesco: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Teléfono del Representante
                    </label>
                    <input
                      value={form.representante_telefono}
                      onChange={(e) => setForm({ ...form, representante_telefono: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Dirección del Representante
                    </label>
                    <input
                      value={form.representante_direccion}
                      onChange={(e) => setForm({ ...form, representante_direccion: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                </div>
              )}

              {activeTab === 3 && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Motivo de Consulta
                    </label>
                    <textarea
                      rows={3}
                      value={form.motivo_consulta}
                      onChange={(e) => setForm({ ...form, motivo_consulta: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Estado de Ánimo
                      </label>
                      <input
                        value={form.estado_animo}
                        onChange={(e) => setForm({ ...form, estado_animo: e.target.value })}
                        className="clinical-input w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Patrón de Sueño
                      </label>
                      <input
                        value={form.sueno}
                        onChange={(e) => setForm({ ...form, sueno: e.target.value })}
                        className="clinical-input w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Alimentación
                      </label>
                      <input
                        value={form.alimentacion}
                        onChange={(e) => setForm({ ...form, alimentacion: e.target.value })}
                        className="clinical-input w-full"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Relaciones Interpersonales
                      </label>
                      <input
                        value={form.relaciones}
                        onChange={(e) => setForm({ ...form, relaciones: e.target.value })}
                        className="clinical-input w-full"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Observaciones de Autoexploración
                    </label>
                    <textarea
                      rows={2}
                      value={form.observaciones_emocionales}
                      onChange={(e) => setForm({ ...form, observaciones_emocionales: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                </div>
              )}

              {activeTab === 4 && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Condición Clínica / Patología (IPX)
                      </label>
                      <select
                        value={form.condicion_clinica}
                        onChange={(e) => setForm({ ...form, condicion_clinica: e.target.value })}
                        className="clinical-input w-full"
                      >
                        {condiciones.map((c) => (
                          <option key={c} value={c}>
                            {c}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                        Agregar nueva condición al catálogo
                      </label>
                      <div className="flex gap-2">
                        <input
                          value={newCondicion}
                          onChange={(e) => setNewCondicion(e.target.value)}
                          placeholder="Ej. Disgrafía..."
                          className="clinical-input flex-1"
                        />
                        <button
                          type="button"
                          onClick={handleAddCondicion}
                          className="px-3 rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-subtle)] text-xs font-semibold"
                        >
                          + Agregar
                        </button>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Diagnóstico CIE-10
                    </label>
                    <input
                      list="hc-cie10"
                      value={form.diagnostico}
                      onChange={(e) => setForm({ ...form, diagnostico: e.target.value })}
                      className="clinical-input w-full"
                    />
                    <datalist id="hc-cie10">
                      {cie10.map((c) => (
                        <option key={c.codigo} value={`[${c.codigo}] ${c.descripcion}`} />
                      ))}
                    </datalist>
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Evaluación Neuropsicológica / IPX
                    </label>
                    <textarea
                      rows={3}
                      value={form.evaluacion_ipx}
                      onChange={(e) => setForm({ ...form, evaluacion_ipx: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                      Plan Terapéutico
                    </label>
                    <textarea
                      rows={3}
                      value={form.plan_terapeutico}
                      onChange={(e) => setForm({ ...form, plan_terapeutico: e.target.value })}
                      className="clinical-input w-full"
                    />
                  </div>
                </div>
              )}

              {activeTab === 5 && (
                <div className="space-y-4">
                  {form.paciente_id ? (
                    <div className="p-4 rounded-xl bg-[var(--bg-subtle)] space-y-3">
                      <div className="text-xs font-bold">Registrar nueva evolución / visita</div>
                      <input
                        placeholder="Diagnóstico de sesión (opcional)"
                        value={newEvo.diagnostico}
                        onChange={(e) => setNewEvo({ ...newEvo, diagnostico: e.target.value })}
                        className="clinical-input w-full"
                      />
                      <textarea
                        rows={2}
                        placeholder="Notas de evolución clínica..."
                        value={newEvo.evolucion}
                        onChange={(e) => setNewEvo({ ...newEvo, evolucion: e.target.value })}
                        className="clinical-input w-full"
                      />
                      <div className="flex justify-end">
                        <button
                          type="button"
                          onClick={handleAddEvolucion}
                          disabled={savingEvo || !newEvo.evolucion.trim()}
                          className="clinical-btn-primary px-3.5 py-1.5 text-xs disabled:opacity-50"
                        >
                          {savingEvo ? "Guardando..." : "+ Agregar Evolución"}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-[var(--text-secondary)]">
                      Guarda primero la Historia Clínica para vincular sesiones de evolución.
                    </p>
                  )}

                  <div className="space-y-2">
                    <div className="text-xs font-bold text-[var(--text-secondary)]">
                      Historial de Sesiones ({sesionesPaciente.length})
                    </div>
                    {sesionesPaciente.map((s) => (
                      <div key={s.id} className="p-3 rounded-lg border border-[var(--border-color)] text-xs space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-mono font-semibold text-[#0F766E]">{s.fecha || "Sin fecha"}</span>
                          {s.diagnostico && <span className="text-[#2A72DE]">{s.diagnostico}</span>}
                        </div>
                        <p className="text-[var(--text-primary)]">{s.evolucion || s.notas}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Footer buttons */}
              <div className="flex justify-end gap-2 pt-4 border-t border-[var(--border-color)]">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg border border-[var(--border-color)]"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="clinical-btn-primary px-4 py-2 text-xs disabled:opacity-60"
                >
                  {saving ? "Guardando..." : editingId ? "Actualizar Historia" : "Guardar Historia"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}

export default function HistoriasPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs">Cargando historias...</div>}>
      <HistoriasContent />
    </Suspense>
  );
}
