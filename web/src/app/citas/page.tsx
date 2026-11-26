"use client";

import React, { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Plus,
  FileDown,
  Edit3,
  Trash2,
  X,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  Calendar as CalIcon,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch, downloadPdf } from "@/lib/api";

interface Paciente {
  id: string;
  nombre: string;
  cedula: string;
}

interface Cita {
  id: string;
  paciente_id: string;
  paciente_nombre: string;
  paciente_cedula?: string;
  fecha: string;
  hora: string;
  tipo: string;
  estado: string;
  notas?: string;
}

const MONTH_NAMES = [
  "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
  "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
];

function CitasContent() {
  const searchParams = useSearchParams();
  const targetPacienteId = searchParams.get("paciente_id");

  const [citas, setCitas] = useState<Cita[]>([]);
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Calendar state (initialized safely in useEffect)
  const [viewYear, setViewYear] = useState(2026);
  const [viewMonth, setViewMonth] = useState(0);
  const [selectedDate, setSelectedDate] = useState<string>("");

  const [form, setForm] = useState({
    paciente_id: "",
    fecha: "",
    hora: "09:00",
    tipo: "Evaluación Inicial",
    estado: "programada",
    notas: "",
  });

  useEffect(() => {
    const now = new Date();
    setViewYear(now.getFullYear());
    setViewMonth(now.getMonth());
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [cList, pList] = await Promise.all([
        apiFetch<Cita[]>("/api/citas"),
        apiFetch<Paciente[]>("/api/pacientes"),
      ]);
      setCitas(cList);
      setPacientes(pList);
      return pList;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData().then((pList) => {
      if (targetPacienteId && pList) {
        setEditingId(null);
        setForm({
          paciente_id: targetPacienteId,
          fecha: new Date().toISOString().slice(0, 10),
          hora: "09:00",
          tipo: "Evaluación Inicial",
          estado: "programada",
          notas: "",
        });
        setModalOpen(true);
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetPacienteId]);

  const datesWithCitas = useMemo(() => {
    const set = new Set<string>();
    citas.forEach((c) => {
      if (c.fecha) set.add(c.fecha.trim());
    });
    return set;
  }, [citas]);

  const calendarDays = useMemo(() => {
    const firstDay = new Date(viewYear, viewMonth, 1).getDay();
    const offset = firstDay === 0 ? 6 : firstDay - 1; // Monday-first
    const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
    const cells: Array<{ day: number | null; iso: string }> = [];
    for (let i = 0; i < offset; i++) cells.push({ day: null, iso: "" });
    for (let d = 1; d <= daysInMonth; d++) {
      const mm = String(viewMonth + 1).padStart(2, "0");
      const dd = String(d).padStart(2, "0");
      cells.push({ day: d, iso: `${viewYear}-${mm}-${dd}` });
    }
    return cells;
  }, [viewYear, viewMonth]);

  const filteredCitas = useMemo(() => {
    if (!selectedDate) return citas;
    return citas.filter((c) => (c.fecha || "").trim() === selectedDate);
  }, [citas, selectedDate]);

  const conflictCita = useMemo(() => {
    if (!form.fecha || !form.hora) return null;
    return citas.find(
      (c) =>
        c.id !== editingId &&
        c.fecha === form.fecha &&
        c.hora === form.hora &&
        (c.estado || "").toLowerCase() !== "cancelada"
    );
  }, [citas, form.fecha, form.hora, editingId]);

  const openNew = () => {
    setEditingId(null);
    setForm({
      paciente_id: pacientes[0]?.id || "",
      fecha: selectedDate || new Date().toISOString().slice(0, 10),
      hora: "09:00",
      tipo: "Evaluación Inicial",
      estado: "programada",
      notas: "",
    });
    setModalOpen(true);
  };

  const openEdit = (c: Cita) => {
    setEditingId(c.id);
    setForm({
      paciente_id: c.paciente_id || "",
      fecha: c.fecha || "",
      hora: c.hora || "",
      tipo: c.tipo || "Consulta",
      estado: c.estado || "programada",
      notas: c.notas || "",
    });
    setModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (conflictCita) {
      const ok = confirm(
        `Conflicto de horario: Ya existe una cita con ${conflictCita.paciente_nombre} el ${form.fecha} a las ${form.hora}. ¿Deseas agendarla de todas formas?`
      );
      if (!ok) return;
    }
    setSaving(true);
    try {
      const pac = pacientes.find((p) => p.id === form.paciente_id);
      const payload = {
        ...form,
        paciente_nombre: pac?.nombre || "Paciente",
        paciente_cedula: pac?.cedula || "",
      };
      if (editingId) {
        await apiFetch(`/api/citas/${editingId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
      } else {
        await apiFetch("/api/citas", {
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
    if (!confirm("¿Eliminar esta cita?")) return;
    await apiFetch(`/api/citas/${id}`, { method: "DELETE" });
    await loadData();
  };

  return (
    <AppShell
      title="Agenda y Citas"
      subtitle={
        selectedDate
          ? `Mostrando ${filteredCitas.length} citas del ${selectedDate}`
          : `${citas.length} citas registradas`
      }
      actions={
        <div className="flex items-center gap-2">
          <button
            onClick={() =>
              downloadPdf(
                "/api/pdf/agenda-citas",
                {
                  citas: filteredCitas,
                  titulo_filtro: selectedDate ? `Agenda del ${selectedDate}` : "Agenda Completa",
                },
                "Agenda_Citas_PSIQUE.pdf"
              )
            }
            className="px-3.5 py-2 text-xs font-medium rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] hover:bg-[var(--bg-subtle)] flex items-center gap-1.5"
          >
            <FileDown className="w-3.5 h-3.5" />
            <span>{selectedDate ? "Imprimir Día PDF" : "Exportar Agenda PDF"}</span>
          </button>
          <button
            onClick={openNew}
            className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Nueva Cita</span>
          </button>
        </div>
      }
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive Monthly Calendar */}
        <div className="lg:col-span-4 clinical-card p-5 h-fit">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <CalIcon className="w-4 h-4 text-[#0F766E]" />
              <span className="text-sm font-bold">
                {MONTH_NAMES[viewMonth]} {viewYear}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={() => {
                  if (viewMonth === 0) {
                    setViewMonth(11);
                    setViewYear((y) => y - 1);
                  } else {
                    setViewMonth((m) => m - 1);
                  }
                }}
                className="p-1.5 rounded hover:bg-[var(--bg-subtle)]"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  if (viewMonth === 11) {
                    setViewMonth(0);
                    setViewYear((y) => y + 1);
                  } else {
                    setViewMonth((m) => m + 1);
                  }
                }}
                className="p-1.5 rounded hover:bg-[var(--bg-subtle)]"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="grid grid-cols-7 gap-1 text-center text-[11px] font-semibold text-[var(--text-secondary)] mb-2">
            {["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"].map((d) => (
              <div key={d} className="py-1">
                {d}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-1">
            {calendarDays.map((cell, idx) => {
              if (!cell.day) return <div key={idx} className="h-9" />;
              const hasCita = datesWithCitas.has(cell.iso);
              const isSelected = selectedDate === cell.iso;
              return (
                <button
                  key={cell.iso}
                  type="button"
                  onClick={() => setSelectedDate(isSelected ? "" : cell.iso)}
                  className={`h-9 rounded-lg text-xs font-medium relative flex items-center justify-center transition-colors ${
                    isSelected
                      ? "bg-[#2A72DE] text-white font-bold"
                      : hasCita
                      ? "bg-teal-50 text-[#0F766E] dark:bg-teal-950/40 dark:text-[#2DD4BF] font-semibold"
                      : "hover:bg-[var(--bg-subtle)]"
                  }`}
                >
                  {cell.day}
                  {hasCita && !isSelected && (
                    <span className="w-1.5 h-1.5 rounded-full bg-[#0F766E] dark:bg-[#2DD4BF] absolute bottom-1" />
                  )}
                </button>
              );
            })}
          </div>

          {selectedDate && (
            <button
              onClick={() => setSelectedDate("")}
              className="mt-4 w-full py-1.5 text-xs font-medium rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-subtle)]"
            >
              Ver todas las fechas
            </button>
          )}
        </div>

        {/* Table */}
        <div className="lg:col-span-8 clinical-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[var(--border-color)] bg-[var(--bg-subtle)] text-[11px] font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                  <th className="py-3 px-4">Fecha y Hora</th>
                  <th className="py-3 px-4">Paciente</th>
                  <th className="py-3 px-4">Tipo</th>
                  <th className="py-3 px-4">Estado</th>
                  <th className="py-3 px-4 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border-color)] text-sm">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                      Cargando agenda...
                    </td>
                  </tr>
                ) : filteredCitas.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-8 text-center text-xs text-[var(--text-secondary)]">
                      No hay citas para el criterio seleccionado.
                    </td>
                  </tr>
                ) : (
                  filteredCitas.map((c) => (
                    <tr key={c.id} className="hover:bg-[var(--bg-subtle)]/50">
                      <td className="py-3 px-4 font-mono text-xs">
                        <div className="font-semibold text-[var(--text-primary)]">{c.fecha}</div>
                        <div className="text-[var(--text-secondary)]">{c.hora}</div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-medium">{c.paciente_nombre}</div>
                        <div className="text-xs text-[var(--text-secondary)]">{c.paciente_cedula}</div>
                      </td>
                      <td className="py-3 px-4 text-xs">{c.tipo}</td>
                      <td className="py-3 px-4">
                        <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-teal-50 text-[#0F766E] dark:bg-teal-950/40 dark:text-teal-300">
                          {c.estado}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="inline-flex items-center gap-1">
                          <button
                            onClick={() =>
                              downloadPdf(
                                "/api/pdf/cita",
                                c,
                                `Cita_${(c.paciente_nombre || "Paciente").replace(/\s+/g, "_")}.pdf`
                              )
                            }
                            title="Comprobante PDF"
                            className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#0F766E]"
                          >
                            <FileDown className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => openEdit(c)}
                            title="Editar"
                            className="p-1.5 rounded-md hover:bg-[var(--bg-subtle)] text-[#2A72DE]"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(c.id)}
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
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
          <div className="clinical-card w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-color)]">
              <h2 className="text-base font-bold">
                {editingId ? "Editar Cita" : "Agendar Nueva Cita"}
              </h2>
              <button onClick={() => setModalOpen(false)} className="p-1 rounded hover:bg-[var(--bg-subtle)]">
                <X className="w-4 h-4" />
              </button>
            </div>

            {conflictCita && (
              <div className="mb-4 flex items-start gap-2.5 p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>
                  Conflicto de horario detectado con <strong>{conflictCita.paciente_nombre}</strong> a las {form.hora}.
                </span>
              </div>
            )}

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
                  <option value="">Selecciona un paciente...</option>
                  {pacientes.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.nombre} ({p.cedula})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
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
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Hora
                  </label>
                  <input
                    type="time"
                    required
                    value={form.hora}
                    onChange={(e) => setForm({ ...form, hora: e.target.value })}
                    className="clinical-input w-full"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                    Tipo de consulta
                  </label>
                  <select
                    value={form.tipo}
                    onChange={(e) => setForm({ ...form, tipo: e.target.value })}
                    className="clinical-input w-full"
                  >
                    <option value="Evaluación Inicial">Evaluación Inicial</option>
                    <option value="Sesión Terapéutica">Sesión Terapéutica</option>
                    <option value="Seguimiento">Seguimiento</option>
                    <option value="Control">Control</option>
                  </select>
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
                    <option value="programada">Programada</option>
                    <option value="confirmada">Confirmada</option>
                    <option value="completada">Completada</option>
                    <option value="cancelada">Cancelada</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Notas
                </label>
                <textarea
                  rows={3}
                  value={form.notas}
                  onChange={(e) => setForm({ ...form, notas: e.target.value })}
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
                  {saving ? "Guardando..." : "Guardar Cita"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}

export default function CitasPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs">Cargando agenda...</div>}>
      <CitasContent />
    </Suspense>
  );
}
