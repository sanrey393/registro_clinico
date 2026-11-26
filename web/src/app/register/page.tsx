"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Lock, Mail, User, ArrowRight, AlertCircle, Moon, Sun } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function RegisterPage() {
  const { user, register } = useAuth();
  const router = useRouter();
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rol, setRol] = useState("psicologo");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("psique_theme");
    const isDark = saved === "dark";
    setDark(isDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);

  useEffect(() => {
    if (user) {
      router.replace("/");
    }
  }, [user, router]);

  const toggleTheme = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("psique_theme", next ? "dark" : "light");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await register(nombre.trim(), email.trim(), password, rol);
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo crear la cuenta");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[var(--bg-canvas)] text-[var(--text-primary)] relative">
      <button
        type="button"
        onClick={toggleTheme}
        className="absolute top-5 right-5 p-2 rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
        title="Alternar tema"
      >
        {dark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
      </button>

      <div className="w-full max-w-md clinical-card p-8 shadow-xs">
        <div className="mb-6">
          <div className="flex items-center gap-2.5 mb-3">
            <img
              src="/app_icon.png"
              alt="PSIQUE"
              className="w-9 h-9 rounded-lg object-contain bg-[#132A2E] p-1"
            />
            <span className="font-bold text-base">PSIQUE</span>
          </div>
          <h1 className="text-xl font-bold text-[var(--text-primary)]">
            Crear cuenta profesional
          </h1>
          <p className="text-xs text-[var(--text-secondary)] mt-1">
            Tu cuenta se sincronizará con Firebase Auth y Firestore.
          </p>
        </div>

        {error && (
          <div className="mb-4 flex items-start gap-2.5 p-3 rounded-lg bg-[var(--danger-bg)] border border-red-200 text-xs text-[var(--danger)]">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">
              Nombre completo
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                required
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                placeholder="Dra. María González"
                className="clinical-input w-full pl-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">
              Correo electrónico
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="doctor@clinica.com"
                className="clinical-input w-full pl-10"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">
              Especialidad / Rol
            </label>
            <select
              value={rol}
              onChange={(e) => setRol(e.target.value)}
              className="clinical-input w-full"
            >
              <option value="psicologo">Psicólogo / Psicoterapeuta</option>
              <option value="medico">Médico General / Psiquiatra</option>
              <option value="recepcionista">Asistente / Recepción</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1.5">
              Contraseña (mínimo 6 caracteres)
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="clinical-input w-full pl-10"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="clinical-btn-primary w-full py-2.5 text-sm flex items-center justify-center gap-2 disabled:opacity-60"
          >
            <span>{submitting ? "Creando cuenta..." : "Registrarme"}</span>
            {!submitting && <ArrowRight className="w-4 h-4" />}
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-[var(--border-color)] flex items-center justify-between text-xs text-[var(--text-secondary)]">
          <span>¿Ya tienes cuenta?</span>
          <Link href="/login" className="text-[#2A72DE] font-semibold hover:underline">
            Iniciar sesión
          </Link>
        </div>
      </div>
    </div>
  );
}
