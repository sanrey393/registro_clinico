"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  CalendarDays,
  FileHeart,
  Stethoscope,
  FileText,
  Pill,
  Receipt,
  LogOut,
  Moon,
  Sun,
  Menu,
  X,
  Activity,
  Calculator,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { CalculatorsModal } from "@/components/CalculatorsModal";

const NAV_ITEMS = [
  { href: "/", label: "Panel Principal", icon: LayoutDashboard },
  { href: "/pacientes", label: "Pacientes", icon: Users },
  { href: "/historias", label: "Historia Clínica", icon: FileHeart },
  { href: "/citas", label: "Agenda y Citas", icon: CalendarDays },
  { href: "/sesiones", label: "Sesiones Clínicas", icon: Stethoscope },
  { href: "/recetas", label: "Recetas Médicas", icon: FileText },
  { href: "/farmacos", label: "Vademécum", icon: Pill },
  { href: "/facturacion", label: "Facturación", icon: Receipt },
];

export function AppShell({
  title,
  subtitle,
  actions,
  children,
}: {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}) {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();
  const [dark, setDark] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [calcOpen, setCalcOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  useEffect(() => {
    const saved = localStorage.getItem("psique_theme");
    const isDark = saved === "dark";
    setDark(isDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("psique_theme", next ? "dark" : "light");
  };

  if (loading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--bg-canvas)]">
        <div className="flex items-center gap-3 text-sm text-[var(--text-secondary)]">
          <Activity className="w-5 h-5 animate-pulse text-[#0F766E]" />
          <span>Cargando entorno clínico PSIQUE...</span>
        </div>
      </div>
    );
  }

  const sidebarContent = (
    <div
      className="flex flex-col h-full text-slate-100 select-none"
      style={{
        background: "linear-gradient(180deg, var(--sidebar-from) 0%, var(--sidebar-to) 100%)",
      }}
    >
      {/* Brand */}
      <div className="px-5 py-5 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <img
            src="/app_icon.png"
            alt="PSIQUE"
            className="w-9 h-9 rounded-lg object-contain bg-white/10 p-0.5 border border-[#2DD4BF]/30"
          />
          <div>
            <div className="text-sm font-bold tracking-wide text-white">PSIQUE</div>
            <div className="text-[11px] text-slate-400">Gestión Clínica</div>
          </div>
        </div>
        <button
          onClick={() => setMobileOpen(false)}
          className="lg:hidden p-1.5 rounded-md text-slate-300 hover:bg-white/10"
          aria-label="Cerrar menú"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] font-medium transition-colors border-l-[3px] ${
                active
                  ? "border-[#2DD4BF] bg-white/12 text-white"
                  : "border-transparent text-slate-300 hover:bg-white/8 hover:text-white"
              }`}
            >
              <Icon
                className={`w-[18px] h-[18px] shrink-0 ${
                  active ? "text-[#2DD4BF]" : "text-slate-400"
                }`}
                strokeWidth={1.75}
              />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer / User */}
      <div className="p-3 border-t border-white/10 space-y-2">
        <button
          onClick={() => setCalcOpen(true)}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-[#2DD4BF] bg-[#2DD4BF]/10 hover:bg-[#2DD4BF]/20 transition-colors"
        >
          <Calculator className="w-4 h-4" />
          <span>Calculadoras Clínicas</span>
        </button>
        <div className="px-3 py-2 rounded-lg bg-white/5">
          <div className="text-xs font-semibold text-white truncate">
            {user.display_name || "Profesional"}
          </div>
          <div className="text-[11px] text-slate-400 truncate">{user.email}</div>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={toggleTheme}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-slate-300 hover:bg-white/10 transition-colors"
            title="Alternar tema"
          >
            {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            <span>{dark ? "Claro" : "Oscuro"}</span>
          </button>
          <button
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-rose-300 hover:bg-rose-500/15 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Salir</span>
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-[var(--bg-canvas)] text-[var(--text-primary)]">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:block w-64 shrink-0 sticky top-0 h-screen">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-slate-950/50 backdrop-blur-xs"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative w-64 max-w-[80vw] h-full z-10">
            {sidebarContent}
          </aside>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="sticky top-0 z-20 bg-[var(--bg-surface)]/95 backdrop-blur-sm border-b border-[var(--border-color)] px-4 sm:px-6 py-3.5">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setMobileOpen(true)}
                className="lg:hidden p-2 rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-subtle)]"
                aria-label="Abrir menú"
              >
                <Menu className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-base sm:text-lg font-bold tracking-tight text-[var(--text-primary)]">
                  {title}
                </h1>
                {subtitle && (
                  <p className="text-xs text-[var(--text-secondary)]">{subtitle}</p>
                )}
              </div>
            </div>
            {actions && <div className="flex items-center gap-2">{actions}</div>}
          </div>
        </header>

        <main className="flex-1 p-4 sm:p-6">
          <div className="max-w-7xl mx-auto">{children}</div>
        </main>
      </div>
      <CalculatorsModal open={calcOpen} onClose={() => setCalcOpen(false)} />
    </div>
  );
}
