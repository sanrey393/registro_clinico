"use client";

import React, { useEffect, useState } from "react";
import { Plus, CheckCircle2, X } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

interface Paciente {
  id: string;
  nombre: string;
  cedula: string;
}

interface Factura {
  id: string;
  paciente_id: string;
  paciente_nombre?: string;
  concepto: string;
  monto: number;
  estado: string;
}

export default function FacturacionPage() {
  const [facturas, setFacturas] = useState<Factura[]>([]);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    paciente_id: "",
    concepto: "Sesión de Psicoterapia",
    monto: "30",
    estado: "pendiente",
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [fList, pList] = await Promise.all([
        apiFetch<Factura[]>("/api/facturas"),
        apiFetch<Paciente[]>("/api/pacientes"),
      ]);
      setFacturas(fList);
      setPacientes(pList);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const pac = pacientes.find((p) => p.id === form.paciente_id);
      await apiFetch("/api/facturas", {
        method: "POST",
        body: JSON.stringify({
          paciente_id: form.paciente_id,
          paciente_nombre: pac?.nombre || form.paciente_id,
          concepto: form.concepto,
          monto: parseFloat(form.monto) || 0,
          estado: form.estado,
        }),
      });
      setModalOpen(false);
      await loadData();
    } finally {
      setSaving(false);
    }
  };

  const togglePagada = async (f: Factura) => {
    const next = f.estado === "pagada" ? "pendiente" : "pagada";
    await apiFetch(`/api/facturas/${f.id}`, {
      method: "PUT",
      body: JSON.stringify({ estado: next }),
    });
    await loadData();
  };

  const totalPagado = facturas
    .filter((f) => f.estado?.toLowerCase() === "pagada")
    .reduce((acc, f) => acc + Number(f.monto || 0), 0);

  const totalPendiente = facturas
    .filter((f) => f.estado?.toLowerCase() !== "pagada")
    .reduce((acc, f) => acc + Number(f.monto || 0), 0);

  return (
    <AppShell
      title="Facturación y Cobros"
      subtitle="Control de pagos y estados de cuenta"
      actions={
        <button
          onClick={() => {
            setForm((f) => ({ ...f, paciente_id: pacientes[0]?.id || "" }));
            setModalOpen(true);
          }}
          className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
        >
          <Plus className="w-3.5 h-3.5" />
          <span>Nueva Factura</span>
        </button>
      }
    >
      {/* Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
        <div className="clinical-card p-5">
          <div className="text-xs text-[var(--text-secondary)]">Total Cobrado</div>
          <div className="text-2xl font-bold text-[#0F766E] mt-1">
            ${totalPagado.toFixed(2)}
          </div>
        </div>
        <div className="clinical-card p-5">
          <div className="text-xs text-[var(--text-secondary)]">Saldo Pendiente</div>
          <div className="text-2xl font-bold text-amber-600 mt-1">
            ${totalPendiente.toFixed(2)}
          </div>
        </div>
      </div>

      <div className="clinical-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-[var(--border-color)] bg-[var(--bg-subtle)] text-[11px] font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                <th className="py-3 px-4">Paciente</th>
                <th className="py-3 px-4">Concepto</th>
                <th className="py-3 px-4">Monto</th>
                <th className="py-3 px-4">Estado</th>
                <th className="py-3 px-4 text-right">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-color)] text-sm">
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    Cargando facturas...
                  </td>
                </tr>
              ) : facturas.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                    No hay facturas registradas.
                  </td>
                </tr>
              ) : (
                facturas.map((f) => {
                  const pac = pacientes.find((p) => p.id === f.paciente_id);
                  const pagada = f.estado?.toLowerCase() === "pagada";
                  return (
                    <tr key={f.id} className="hover:bg-[var(--bg-subtle)]/50">
                      <td className="py-3 px-4 font-medium">
                        {f.paciente_nombre || pac?.nombre || f.paciente_id}
                      </td>
                      <td className="py-3 px-4 text-xs">{f.concepto}</td>
                      <td className="py-3 px-4 font-mono text-xs font-semibold">
                        ${Number(f.monto || 0).toFixed(2)}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[11px] font-medium ${
                            pagada
                              ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                              : "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300"
                          }`}
                        >
                          {f.estado}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => togglePagada(f)}
                          className="px-2.5 py-1 text-xs rounded-md border border-[var(--border-color)] hover:bg-[var(--bg-subtle)] inline-flex items-center gap-1"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5 text-[#0F766E]" />
                          <span>{pagada ? "Marcar pendiente" : "Marcar pagada"}</span>
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <div className="clinical-card w-full max-w-md p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-color)]">
              <h2 className="text-base font-bold">Nueva Factura</h2>
              <button onClick={() => setModalOpen(false)} className="p-1 rounded hover:bg-[var(--bg-subtle)]">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4">
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
                  Concepto *
                </label>
                <input
                  required
                  value={form.concepto}
                  onChange={(e) => setForm({ ...form, concepto: e.target.value })}
                  className="clinical-input w-full"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Monto ($) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={form.monto}
                    onChange={(e) => setForm({ ...form, monto: e.target.value })}
                    className="clinical-input w-full"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Estado
                  </label>
                  <select
                    value={form.estado}
                    onChange={(e) => setForm({ ...form, estado: e.target.value })}
                    className="clinical-input w-full"
                  >
                    <option value="pendiente">Pendiente</option>
                    <option value="pagada">Pagada</option>
                  </select>
                </div>
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
                  {saving ? "Guardando..." : "Crear Factura"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
