"use client";

import React, { useEffect, useMemo, useState } from "react";
import { Search, Plus, Pill, X } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

interface Farmaco {
  id?: string;
  nombre_comercial: string;
  nombre_generico: string;
  laboratorio?: string;
  descripcion_indicaciones?: string;
  contraindicaciones?: string;
  efectos_secundarios?: string;
  interacciones?: string;
  recetacion_dosis?: string;
  isCustom?: boolean;
}

export default function FarmacosPage() {
  const [farmacos, setFarmacos] = useState<Farmaco[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    nombre_comercial: "",
    nombre_generico: "",
    laboratorio: "",
    descripcion_indicaciones: "",
    contraindicaciones: "",
    recetacion_dosis: "",
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await apiFetch<{ base: Farmaco[]; custom: Farmaco[] }>("/api/farmacos");
      const base = (res.base || []).map((f) => ({ ...f, isCustom: false }));
      const custom = (res.custom || []).map((f) => ({ ...f, isCustom: true }));
      setFarmacos([...custom, ...base]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return farmacos;
    return farmacos.filter(
      (f) =>
        (f.nombre_comercial || "").toLowerCase().includes(q) ||
        (f.nombre_generico || "").toLowerCase().includes(q) ||
        (f.laboratorio || "").toLowerCase().includes(q)
    );
  }, [farmacos, search]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await apiFetch("/api/farmacos", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setModalOpen(false);
      setForm({
        nombre_comercial: "",
        nombre_generico: "",
        laboratorio: "",
        descripcion_indicaciones: "",
        contraindicaciones: "",
        recetacion_dosis: "",
      });
      await loadData();
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell
      title="Vademécum Farmacológico"
      subtitle="Catálogo clínico de medicamentos, posología, contraindicaciones e interacciones"
      actions={
        <button
          onClick={() => setModalOpen(true)}
          className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Agregar Fármaco</span>
        </button>
      }
    >
      <div className="clinical-card p-4 mb-5">
        <div className="relative max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nombre comercial, principio activo o laboratorio..."
            className="clinical-input w-full pl-9"
          />
        </div>
      </div>

      {loading ? (
        <div className="clinical-card p-8 text-center text-xs text-[var(--text-secondary)]">
          Cargando vademécum...
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((f, i) => (
            <div key={f.id || i} className="clinical-card p-5 space-y-2.5">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-teal-50 text-[#0F766E] dark:bg-teal-950/40">
                    <Pill className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold">{f.nombre_comercial}</h3>
                    <p className="text-xs text-[var(--text-secondary)]">
                      {f.nombre_generico} {f.laboratorio ? `· ${f.laboratorio}` : ""}
                    </p>
                  </div>
                </div>
                {f.isCustom && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-[#2A72DE]">
                    Personalizado
                  </span>
                )}
              </div>

              {f.descripcion_indicaciones && (
                <p className="text-xs text-[var(--text-primary)] leading-relaxed">
                  <strong>Indicaciones:</strong> {f.descripcion_indicaciones}
                </p>
              )}
              {f.recetacion_dosis && (
                <p className="text-xs text-[#0F766E] leading-relaxed">
                  <strong>Posología:</strong> {f.recetacion_dosis}
                </p>
              )}
              {f.contraindicaciones && (
                <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                  <strong>Contraindicaciones:</strong> {f.contraindicaciones}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <div className="clinical-card w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-color)]">
              <h2 className="text-base font-bold">Registrar Fármaco Personalizado</h2>
              <button onClick={() => setModalOpen(false)} className="p-1 rounded hover:bg-[var(--bg-subtle)]">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Nombre comercial *
                </label>
                <input
                  required
                  value={form.nombre_comercial}
                  onChange={(e) => setForm({ ...form, nombre_comercial: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Principio activo / Genérico *
                </label>
                <input
                  required
                  value={form.nombre_generico}
                  onChange={(e) => setForm({ ...form, nombre_generico: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Laboratorio
                </label>
                <input
                  value={form.laboratorio}
                  onChange={(e) => setForm({ ...form, laboratorio: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Posología recomendada
                </label>
                <textarea
                  rows={2}
                  value={form.recetacion_dosis}
                  onChange={(e) => setForm({ ...form, recetacion_dosis: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Indicaciones
                </label>
                <textarea
                  rows={2}
                  value={form.descripcion_indicaciones}
                  onChange={(e) => setForm({ ...form, descripcion_indicaciones: e.target.value })}
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
                  {saving ? "Guardando..." : "Guardar Fármaco"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
