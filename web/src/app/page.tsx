"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  CalendarDays,
  Stethoscope,
  FileHeart,
  FileText,
  Receipt,
  Plus,
  Clock,
  ArrowUpRight,
} from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { apiFetch } from "@/lib/api";

interface DashboardSummary {
  counts: {
    pacientes: number;
    citas: number;
    citas_hoy: number;
    citas_programadas: number;
    sesiones: number;
    historias: number;
    recetas: number;
    facturas: number;
    total_cobrado: number;
    total_pendiente: number;
  };
  citas_hoy: Array<{
    id: string;
    paciente_nombre?: string;
    hora?: string;
    tipo?: string;
    estado?: string;
  }>;
  ultimos_pacientes: Array<{
    id: string;
    nombre?: string;
    cedula?: string;
    telefono?: string;
    pnf?: string;
  }>;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    apiFetch<DashboardSummary>("/api/dashboard/summary")
      .then((data) => {
        if (active) setSummary(data);
      })
      .catch((err) => {
        if (active) setError(err instanceof Error ? err.message : "Error cargando resumen");
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const counts = summary?.counts;

  const kpis = [
    {
      label: "Pacientes Activos",
      value: counts?.pacientes ?? "—",
      icon: Users,
      accent: "text-[#2A72DE] bg-blue-50 dark:bg-blue-950/40",
      href: "/pacientes",
    },
    {
      label: "Citas Hoy / Programadas",
      value: counts ? `${counts.citas_hoy} / ${counts.citas_programadas}` : "—",
      icon: CalendarDays,
      accent: "text-[#0F766E] bg-teal-50 dark:bg-teal-950/40",
      href: "/citas",
    },
    {
      label: "Historias Clínicas",
      value: counts?.historias ?? "—",
      icon: FileHeart,
      accent: "text-indigo-600 bg-indigo-50 dark:bg-indigo-950/40",
      href: "/historias",
    },
    {
      label: "Sesiones Registradas",
      value: counts?.sesiones ?? "—",
      icon: Stethoscope,
      accent: "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/40",
      href: "/sesiones",
    },
    {
      label: "Recetas Emitidas",
      value: counts?.recetas ?? "—",
      icon: FileText,
      accent: "text-amber-600 bg-amber-50 dark:bg-amber-950/40",
      href: "/recetas",
    },
    {
      label: "Cobrado / Pendiente",
      value: counts ? `$${counts.total_cobrado} / $${counts.total_pendiente}` : "—",
      icon: Receipt,
      accent: "text-slate-700 bg-slate-100 dark:bg-slate-800 dark:text-slate-200",
      href: "/facturacion",
    },
  ];

  return (
    <AppShell
      title="Panel Principal"
      subtitle="Resumen general de actividad clínica en tiempo real"
      actions={
        <div className="flex items-center gap-2">
          <Link
            href="/pacientes"
            className="clinical-btn-primary px-3.5 py-2 text-xs flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Nuevo Paciente</span>
          </Link>
          <Link
            href="/citas"
            className="px-3.5 py-2 text-xs font-medium rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] hover:bg-[var(--bg-subtle)] flex items-center gap-1.5"
          >
            <CalendarDays className="w-3.5 h-3.5" />
            <span>Agendar Cita</span>
          </Link>
        </div>
      }
    >
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-[var(--danger-bg)] text-[var(--danger)] text-xs border border-red-200">
          {error}
        </div>
      )}

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <Link
              key={kpi.label}
              href={kpi.href}
              className="clinical-card p-5 hover:border-[#2A72DE]/40 transition-colors group"
            >
              <div className="flex items-start justify-between">
                <div className={`p-2.5 rounded-lg ${kpi.accent}`}>
                  <Icon className="w-5 h-5" strokeWidth={1.75} />
                </div>
                <ArrowUpRight className="w-4 h-4 text-[var(--text-secondary)] opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <div className="mt-4">
                <div className="text-2xl font-bold tracking-tight text-[var(--text-primary)]">
                  {loading ? "..." : kpi.value}
                </div>
                <div className="text-xs text-[var(--text-secondary)] mt-0.5">
                  {kpi.label}
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Two-Column Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Citas de Hoy */}
        <div className="clinical-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#0F766E]" />
              <h2 className="text-sm font-bold">Citas de Hoy</h2>
            </div>
            <Link href="/citas" className="text-xs text-[#2A72DE] hover:underline">
              Ver agenda
            </Link>
          </div>
          {loading ? (
            <p className="text-xs text-[var(--text-secondary)]">Cargando citas...</p>
          ) : summary?.citas_hoy?.length ? (
            <div className="divide-y divide-[var(--border-color)]">
              {summary.citas_hoy.map((c) => (
                <div key={c.id} className="py-2.5 flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm font-medium">{c.paciente_nombre || "Paciente"}</div>
                    <div className="text-xs text-[var(--text-secondary)]">
                      {c.tipo || "Consulta"} · {c.hora || "--:--"}
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-teal-50 text-[#0F766E] dark:bg-teal-950/50 dark:text-teal-300">
                    {c.estado || "programada"}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[var(--text-secondary)] py-6 text-center">
              No hay citas registradas para hoy.
            </p>
          )}
        </div>

        {/* Pacientes Recientes */}
        <div className="clinical-card p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-[#2A72DE]" />
              <h2 className="text-sm font-bold">Pacientes Recientes</h2>
            </div>
            <Link href="/pacientes" className="text-xs text-[#2A72DE] hover:underline">
              Ver directorio
            </Link>
          </div>
          {loading ? (
            <p className="text-xs text-[var(--text-secondary)]">Cargando pacientes...</p>
          ) : summary?.ultimos_pacientes?.length ? (
            <div className="divide-y divide-[var(--border-color)]">
              {summary.ultimos_pacientes.map((p) => (
                <div key={p.id} className="py-2.5 flex items-center justify-between gap-3">
                  <div>
                    <div className="text-sm font-medium">{p.nombre || "Sin nombre"}</div>
                    <div className="text-xs text-[var(--text-secondary)]">
                      {p.cedula || "Sin cédula"} {p.pnf ? `· ${p.pnf}` : ""}
                    </div>
                  </div>
                  <div className="text-xs text-[var(--text-secondary)]">
                    {p.telefono || "—"}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-[var(--text-secondary)] py-6 text-center">
              Aún no hay pacientes registrados.
            </p>
          )}
        </div>
      </div>
    </AppShell>
  );
}
