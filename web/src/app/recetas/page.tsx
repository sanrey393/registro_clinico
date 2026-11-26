"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Plus,
  FileDown,
  Trash2,
  X,
  Edit3,
  AlertTriangle,
  CalendarDays,
  Search,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch, downloadPdf } from "@/lib/api";

interface Paciente {
  id: string;
  nombre: string;
  cedula: string;
}

interface Historia {
  id: string;
  paciente_id?: string;
  alergias?: string;
  medicacion_actual?: string;
  condicion_clinica?: string;
}

interface Farmaco {
  id?: string;
  nombre_comercial: string;
  nombre_generico: string;
  recetacion_dosis?: string;
  contraindicaciones?: string;
  efectos_secundarios?: string;
  interacciones?: string;
}

interface Receta {
  id: string;
  paciente_id: string;
  paciente_nombre: string;
  paciente_cedula?: string;
  fecha?: string;
  medicamento: string;
  nombre_comercial?: string;
  nombre_generico?: string;
  dosis?: string;
  frecuencia?: string;
  duracion?: string;
  indicaciones?: string;
  contraindicaciones?: string;
  efectos_secundarios?: string;
  interacciones?: string;
}

function RecetasContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const targetPacienteId = searchParams.get("paciente_id");

  const [recetas, setRecetas] = useState<Receta[]>([]);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [historias, setHistorias] = useState<Historia[]>([]);
  const [farmacos, setFarmacos] = useState<Farmaco[]>([]);

  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    paciente_id: "",
    fecha: "",
    nombre_comercial: "",
    nombre_generico: "",
    medicamento: "",
    dosis: "",
    frecuencia: "",
    duracion: "",
    indicaciones: "",
    contraindicaciones: "",
    efectos_secundarios: "",
    interacciones: "",
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [rList, pList, hList, fData] = await Promise.all([
        apiFetch<Receta[]>("/api/recetas"),
        apiFetch<Paciente[]>("/api/pacientes"),
        apiFetch<Historia[]>("/api/historias"),
        apiFetch<{ base: Farmaco[]; custom: Farmaco[] }>("/api/farmacos"),
      ]);
      setRecetas(rList);
      setPacientes(pList);
      setHistorias(hList);
      setFarmacos([...(fData.base || []), ...(fData.custom || [])]);
      return pList;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData().then((pList) => {
      if (targetPacienteId && pList) {
        setEditingId(null);
        setForm((f) => ({
          ...f,
          paciente_id: targetPacienteId,
          fecha: new Date().toISOString().slice(0, 10),
        }));
        setModalOpen(true);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetPacienteId]);

  const applyFarmaco = (f: Farmaco) => {
    setForm((prev) => ({
      ...prev,
      nombre_comercial: f.nombre_comercial,
      nombre_generico: f.nombre_generico,
      medicamento: `${f.nombre_comercial} (${f.nombre_generico})`,
      indicaciones: f.recetacion_dosis || prev.indicaciones,
      contraindicaciones: f.contraindicaciones || "",
      efectos_secundarios: f.efectos_secundarios || "",
      interacciones: f.interacciones || "",
    }));
  };

  const handleComercialChange = (val: string) => {
    const found = farmacos.find(
      (f) => f.nombre_comercial.toLowerCase() === val.trim().toLowerCase()
    );
    if (found) {
      applyFarmaco(found);
    } else {
      setForm((prev) => ({
        ...prev,
        nombre_comercial: val,
        medicamento: prev.nombre_generico ? `${val} (${prev.nombre_generico})` : val,
      }));
    }
  };

  const handleGenericoChange = (val: string) => {
    const found = farmacos.find(
      (f) => f.nombre_generico.toLowerCase() === val.trim().toLowerCase()
    );
    if (found) {
      applyFarmaco(found);
    } else {
      setForm((prev) => ({
        ...prev,
        nombre_generico: val,
        medicamento: prev.nombre_comercial ? `${prev.nombre_comercial} (${val})` : val,
      }));
    }
  };

  // Alerta clínica inteligente cruzando Historia Clínica del paciente + fármaco
  const clinicalAlert = useMemo(() => {
    if (!form.paciente_id) return null;
    const hc = historias.find((h) => h.paciente_id === form.paciente_id);
    if (!hc) return null;
    const alerts: string[] = [];
    if (hc.alergias && hc.alergias.trim()) {
      alerts.push(`Alergias registradas: ${hc.alergias}`);
    }
    if (hc.medicacion_actual && hc.medicacion_actual.trim()) {
      alerts.push(`Medicación actual: ${hc.medicacion_actual}`);
    }
    if (form.contraindicaciones && form.contraindicaciones.trim()) {
      alerts.push(`Contraindicaciones del fármaco: ${form.contraindicaciones}`);
    }
    return alerts.length > 0 ? alerts : null;
  }, [form.paciente_id, form.contraindicaciones, historias]);

  const openNew = () => {
    setEditingId(null);
    setForm({
      paciente_id: pacientes[0]?.id || "",
      fecha: new Date().toISOString().slice(0, 10),
      nombre_comercial: "",
      nombre_generico: "",
      medicamento: "",
      dosis: "",
      frecuencia: "",
      duracion: "",
      indicaciones: "",
      contraindicaciones: "",
      efectos_secundarios: "",
      interacciones: "",
    });
    setModalOpen(true);
  };

  const openEdit = (r: Receta) => {
    setEditingId(r.id);
    setForm({
      paciente_id: r.paciente_id || "",
      fecha: r.fecha || "",
      nombre_comercial: r.nombre_comercial || r.medicamento || "",
      nombre_generico: r.nombre_generico || "",
      medicamento: r.medicamento || "",
      dosis: r.dosis || "",
      frecuencia: r.frecuencia || "",
      duracion: r.duracion || "",
      indicaciones: r.indicaciones || "",
      contraindicaciones: r.contraindicaciones || "",
      efectos_secundarios: r.efectos_secundarios || "",
      interacciones: r.interacciones || "",
    });
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const pac = pacientes.find((p) => p.id === form.paciente_id);
      const medDisplay =
        form.medicamento ||
        [form.nombre_comercial, form.nombre_generico ? `(${form.nombre_generico})` : ""]
          .filter(Boolean)
          .join(" ");

      const payload = {
        ...form,
        medicamento: medDisplay,
        paciente_nombre: pac?.nombre || "Paciente",
        paciente_cedula: pac?.cedula || "",
      };

      if (editingId) {
        await apiFetch(`/api/recetas/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
      } else {
        await apiFetch("/api/recetas", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      setModalOpen(false);
      await loadData();
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar esta receta?")) return;
    await apiFetch(`/api/recetas/${id}`, { method: "DELETE" });
    await loadData();
  };

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return recetas;
    return recetas.filter(
      (r) =>
        (r.paciente_nombre || "").toLowerCase().includes(q) ||
        (r.medicamento || "").toLowerCase().includes(q)
    );
  }, [recetas, search]);

  return (
    <AppShell
      title="Recetas Médicas e Indicaciones"
      subtitle={`${recetas.length} recetas emitidas · Cruce automático con Vademécum e Historia Clínica`}
      actions={
        <button
          onClick={openNew}
          className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Nueva Receta</span>
        </button>
      }
    >
      <div className="clinical-card p-4 mb-5">
        <div className="relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar receta por paciente o medicamento..."
            className="clinical-input w-full pl-10"
          />
        </div>
      </div>

      <div className="clinical-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border-color)] bg-[var(--bg-subtle)] text-[11px] font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                <th className="py-3 px-4">Fecha</th>
                <th className="py-3 px-4">Paciente</th>
                <th className="py-3 px-4">Medicamento / Posología</th>
                <th className="py-3 px-4 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-color)] text-sm">
              {loading ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    Cargando recetas...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    No hay recetas emitidas.
                  </td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-[var(--bg-subtle)]/50">
                    <td className="py-3 px-4 font-mono text-xs">{r.fecha || "—"}</td>
                    <td className="py-3 px-4">
                      <div className="font-semibold">{r.paciente_nombre}</div>
                      <div className="text-xs text-[var(--text-secondary)]">{r.paciente_cedula}</div>
                    </td>
                    <td className="py-3 px-4 text-xs">
                      <div className="font-semibold text-[var(--text-primary)]">{r.medicamento}</div>
                      <div className="text-[var(--text-secondary)]">
                        {[r.dosis, r.frecuencia, r.duracion].filter(Boolean).join(" · ")}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="inline-flex items-center gap-1">
                        {r.paciente_id && (
                          <button
                            onClick={() => router.push(`/citas?paciente_id=${r.paciente_id}`)}
                            title="Agendar Control"
                            className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#0F766E]"
                          >
                            <CalendarDays className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() =>
                            downloadPdf(
                              "/api/pdf/receta",
                              r,
                              `Receta_${(r.paciente_nombre || "Paciente").replace(/\s+/g, "_")}.pdf`
                            )
                          }
                          title="Descargar Receta PDF"
                          className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#0F766E]"
                        >
                          <FileDown className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => openEdit(r)}
                          title="Editar"
                          className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#2A72DE]"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(r.id)}
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

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <div className="clinical-card w-full max-w-2xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-color)]">
              <h2 className="text-base font-bold">
                {editingId ? "Editar Receta Médica" : "Emitir Receta Médica"}
              </h2>
              <button onClick={() => setModalOpen(false)} className="p-1 rounded hover:bg-[var(--bg-subtle)]">
                <X className="w-4 h-4" />
              </button>
            </div>

            {clinicalAlert && (
              <div className="mb-4 p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>Alerta Clínica del Paciente</span>
                </div>
                {clinicalAlert.map((a, i) => (
                  <div key={i}>• {a}</div>
                ))}
              </div>
            )}

            <form onSubmit={handleSave} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Paciente *
                  </label>
                  <select
                    required
                    value={form.paciente_id}
                    onChange={(e) => setForm({ ...form, paciente_id: e.target.value })}
                    className="clinical-input w-full"
                  >
                    <option value="">Selecciona...</option>
                    {pacientes.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.nombre} ({p.cedula})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Fecha
                  </label>
                  <input
                    type="date"
                    required
                    value={form.fecha}
                    onChange={(e) => setForm({ ...form, fecha: e.target.value })}
                    className="clinical-input w-full"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Nombre Comercial *
                  </label>
                  <input
                    required
                    list="comercial-list"
                    value={form.nombre_comercial}
                    onChange={(e) => handleComercialChange(e.target.value)}
                    placeholder="Ej. Tylenol / Tempra"
                    className="clinical-input w-full"
                  />
                  <datalist id="comercial-list">
                    {farmacos.map((f, idx) => (
                      <option key={f.id || idx} value={f.nombre_comercial} />
                    ))}
                  </datalist>
                </div>
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Principio Activo / Genérico
                  </label>
                  <input
                    list="generico-list"
                    value={form.nombre_generico}
                    onChange={(e) => handleGenericoChange(e.target.value)}
                    placeholder="Ej. Paracetamol"
                    className="clinical-input w-full"
                  />
                  <datalist id="generico-list">
                    {farmacos.map((f, idx) => (
                      <option key={f.id || idx} value={f.nombre_generico} />
                    ))}
                  </datalist>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Dosis
                  </label>
                  <input
                    placeholder="500 mg"
                    value={form.dosis}
                    onChange={(e) => setForm({ ...form, dosis: e.target.value })}
                    className="clinical-input w-full"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Frecuencia
                  </label>
                  <input
                    placeholder="Cada 8h"
                    value={form.frecuencia}
                    onChange={(e) => setForm({ ...form, frecuencia: e.target.value })}
                    className="clinical-input w-full"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Duración
                  </label>
                  <input
                    placeholder="7 días"
                    value={form.duracion}
                    onChange={(e) => setForm({ ...form, duracion: e.target.value })}
                    className="clinical-input w-full"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Indicaciones para el paciente
                </label>
                <textarea
                  rows={3}
                  value={form.indicaciones}
                  onChange={(e) => setForm({ ...form, indicaciones: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-[var(--border-color)]">
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
                  {saving ? "Guardando..." : editingId ? "Actualizar Receta" : "Emitir Receta"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}

export default function RecetasPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs">Cargando recetas...</div>}>
      <RecetasContent />
    </Suspense>
  );
}
