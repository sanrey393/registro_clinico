"use client";

import React, { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Plus, FileDown, Trash2, X, Search, FileHeart } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch, downloadPdf } from "@/lib/api";

interface Paciente {
  id: string;
  nombre: string;
  cedula: string;
  pnf?: string;
}

interface Sesion {
  id: string;
  paciente_id: string;
  paciente_nombre?: string;
  fecha?: string;
  diagnostico?: string;
  motivo?: string;
  notas?: string;
  evolucion?: string;
  plan_tratamiento?: string;
}

export default function SesionesPage() {
  const router = useRouter();
  const [sesiones, setSesiones] = useState<Sesion[]>([]);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [cie10, setCie10] = useState<Array<{ codigo: string; descripcion: string }>>([]);
  const [pnfList, setPnfList] = useState<string[]>([]);

  const [search, setSearch] = useState("");
  const [filterPnf, setFilterPnf] = useState("");
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    paciente_id: "",
    fecha: "",
    diagnostico: "",
    motivo: "",
    notas: "",
    evolucion: "",
    plan_tratamiento: "",
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [sList, pList, cat] = await Promise.all([
        apiFetch<Sesion[]>("/api/sesiones"),
        apiFetch<Paciente[]>("/api/pacientes"),
        apiFetch<{
          cie10: Array<{ codigo: string; descripcion: string }>;
          pnf: string[];
        }>("/api/catalogs"),
      ]);
      setSesiones(sList);
      setPacientes(pList);
      setCie10(cat.cie10 || []);
      setPnfList(cat.pnf || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const pacMap = useMemo(() => {
    const m = new Map<string, Paciente>();
    pacientes.forEach((p) => m.set(p.id, p));
    return m;
  }, [pacientes]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return sesiones.filter((s) => {
      const pac = pacMap.get(s.paciente_id);
      if (filterPnf && (pac?.pnf || "") !== filterPnf) return false;
      if (q) {
        const text = `${s.paciente_nombre || pac?.nombre || ""} ${s.diagnostico || ""} ${
          s.evolucion || s.notas || ""
        }`.toLowerCase();
        if (!text.includes(q)) return false;
      }
      return true;
    });
  }, [sesiones, pacMap, search, filterPnf]);

  const uniquePatientsCount = useMemo(
    () => new Set(filtered.map((s) => s.paciente_id).filter(Boolean)).size,
    [filtered]
  );

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const pac = pacientes.find((p) => p.id === form.paciente_id);
      await apiFetch("/api/sesiones", {
        method: "POST",
        body: JSON.stringify({
          ...form,
          paciente_nombre: pac?.nombre || "Paciente",
          paciente_cedula: pac?.cedula || "",
        }),
      });
      setModalOpen(false);
      await loadData();
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar esta sesión clínica?")) return;
    await apiFetch(`/api/sesiones/${id}`, { method: "DELETE" });
    await loadData();
  };

  return (
    <AppShell
      title="Bitácora y Sesiones Clínicas"
      subtitle="Evolución terapéutica, filtros por PNF y acceso directo al expediente"
      actions={
        <button
          onClick={() => {
            setForm((f) => ({
              ...f,
              paciente_id: pacientes[0]?.id || "",
              fecha: f.fecha || new Date().toISOString().slice(0, 10),
            }));
            setModalOpen(true);
          }}
          className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Registrar Sesión</span>
        </button>
      }
    >
      {/* KPIs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
        <div className="clinical-card p-4">
          <div className="text-xs text-[var(--text-secondary)]">Sesiones Filtradas</div>
          <div className="text-2xl font-bold text-[#2A72DE] mt-1">{filtered.length}</div>
        </div>
        <div className="clinical-card p-4">
          <div className="text-xs text-[var(--text-secondary)]">Pacientes Atendidos</div>
          <div className="text-2xl font-bold text-[#0F766E] mt-1">{uniquePatientsCount}</div>
        </div>
        <div className="clinical-card p-4">
          <div className="text-xs text-[var(--text-secondary)]">Total Histórico</div>
          <div className="text-2xl font-bold mt-1">{sesiones.length}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="clinical-card p-4 mb-5 flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar en bitácora por paciente, diagnóstico o nota..."
            className="clinical-input w-full pl-10"
          />
        </div>
        <select
          value={filterPnf}
          onChange={(e) => setFilterPnf(e.target.value)}
          className="clinical-input text-xs"
        >
          <option value="">Todos los PNF</option>
          {pnfList.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </div>

      {/* List */}
      <div className="space-y-3">
        {loading ? (
          <div className="clinical-card p-8 text-center text-xs text-[var(--text-secondary)]">
            Cargando bitácora...
          </div>
        ) : filtered.length === 0 ? (
          <div className="clinical-card p-8 text-center text-xs text-[var(--text-secondary)]">
            No hay sesiones clínicas para los filtros seleccionados.
          </div>
        ) : (
          filtered.map((s) => {
            const pac = pacMap.get(s.paciente_id);
            return (
              <div
                key={s.id}
                className="clinical-card p-5 flex flex-col sm:flex-row sm:items-start justify-between gap-4"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="font-bold text-sm">
                      {s.paciente_nombre || pac?.nombre || "Paciente"}
                    </span>
                    <span className="text-xs font-mono text-[var(--text-secondary)]">
                      {s.fecha || "Sin fecha"}
                    </span>
                    {pac?.pnf && (
                      <span className="px-2 py-0.5 rounded-md text-[11px] bg-[var(--bg-subtle)] text-[var(--text-secondary)]">
                        {pac.pnf}
                      </span>
                    )}
                    {s.diagnostico && (
                      <span className="px-2 py-0.5 rounded-md text-[11px] font-medium bg-blue-50 text-[#2A72DE] dark:bg-blue-950/40">
                        {s.diagnostico}
                      </span>
                    )}
                  </div>
                  {s.motivo && (
                    <p className="text-xs text-[var(--text-primary)]">
                      <strong>Motivo:</strong> {s.motivo}
                    </p>
                  )}
                  {(s.evolucion || s.notas) && (
                    <p className="text-xs text-[var(--text-secondary)] whitespace-pre-line">
                      {s.evolucion || s.notas}
                    </p>
                  )}
                  {s.plan_tratamiento && (
                    <p className="text-xs text-[#0F766E]">
                      <strong>Plan:</strong> {s.plan_tratamiento}
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-1.5 shrink-0">
                  {s.paciente_id && (
                    <button
                      onClick={() => router.push(`/historias?paciente_id=${s.paciente_id}`)}
                      className="px-2.5 py-1.5 text-xs rounded-md border border-[var(--border-color)] hover:bg-[var(--bg-subtle)] flex items-center gap-1 text-indigo-600"
                    >
                      <FileHeart className="w-3.5 h-3.5" />
                      <span>Historia</span>
                    </button>
                  )}
                  <button
                    onClick={() =>
                      downloadPdf(
                        "/api/pdf/sesion",
                        s,
                        `Sesion_${(s.paciente_nombre || "Paciente").replace(/\s+/g, "_")}.pdf`
                      )
                    }
                    className="px-2.5 py-1.5 text-xs rounded-md border border-[var(--border-color)] hover:bg-[var(--bg-subtle)] flex items-center gap-1 text-[#0F766E]"
                  >
                    <FileDown className="w-3.5 h-3.5" />
                    <span>PDF</span>
                  </button>
                  <button
                    onClick={() => handleDelete(s.id)}
                    className="p-1.5 rounded-md hover:bg-red-50 text-red-600"
                    title="Eliminar"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <div className="clinical-card w-full max-w-xl max-h-[90vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-color)]">
              <h2 className="text-base font-bold">Nueva Sesión Clínica</h2>
              <button onClick={() => setModalOpen(false)} className="p-1 rounded hover:bg-[var(--bg-subtle)]">
                <X className="w-4 h-4" />
              </button>
            </div>

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

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Diagnóstico CIE-10
                </label>
                <input
                  list="cie10-list"
                  value={form.diagnostico}
                  onChange={(e) => setForm({ ...form, diagnostico: e.target.value })}
                  placeholder="Ej. [F41.1] Trastorno de ansiedad generalizada"
                  className="clinical-input w-full"
                />
                <datalist id="cie10-list">
                  {cie10.map((c) => (
                    <option key={c.codigo} value={`[${c.codigo}] ${c.descripcion}`} />
                  ))}
                </datalist>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Motivo de la sesión
                </label>
                <input
                  value={form.motivo}
                  onChange={(e) => setForm({ ...form, motivo: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Evolución / Notas terapéuticas *
                </label>
                <textarea
                  required
                  rows={4}
                  value={form.evolucion}
                  onChange={(e) => setForm({ ...form, evolucion: e.target.value, notas: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Plan terapéutico / Indicaciones
                </label>
                <textarea
                  rows={2}
                  value={form.plan_tratamiento}
                  onChange={(e) => setForm({ ...form, plan_tratamiento: e.target.value })}
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
                  {saving ? "Guardando..." : "Guardar Sesión"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
