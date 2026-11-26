"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Lock, Mail, ArrowRight, AlertCircle, CheckCircle2, Moon, Sun } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { apiFetch } from "@/lib/api";

function GoogleIcon() {
  return (
    <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="#4285F4"
        d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17Z"
      />
      <path
        fill="#34A853"
        d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.11-6.72-4.96H1.29v3.14C3.26 21.3 7.31 24 12 24Z"
      />
      <path
        fill="#FBBC05"
        d="M5.28 14.24c-.24-.72-.38-1.49-.38-2.24s.14-1.52.38-2.24V6.62H1.29C.47 8.24 0 10.06 0 12s.47 3.76 1.29 5.38l3.99-3.14Z"
      />
      <path
        fill="#EA4335"
        d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.26 2.7 1.29 6.62l3.99 3.14c.95-2.85 3.6-4.96 6.72-4.96Z"
      />
    </svg>
  );
}

export default function LoginPage() {
  const { user, login, loginWithGoogle } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [dark, setDark] = useState(false);

  const [resetMode, setResetMode] = useState(false);
  const [resetMsg, setResetMsg] = useState("");

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
      await login(email.trim(), password);
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al iniciar sesión");
    } finally {
      setSubmitting(false);
    }
  };

  const handleGoogle = async () => {
    setError("");
    setGoogleLoading(true);
    try {
      await loginWithGoogle();
      router.replace("/");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "No se pudo iniciar sesión con Google."
      );
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setResetMsg("");
    setSubmitting(true);
    try {
      const res = await apiFetch<{ message: string }>("/api/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ email: email.trim() }),
      });
      setResetMsg(res.message || "Correo de recuperación enviado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo enviar el correo");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-[var(--bg-canvas)] text-[var(--text-primary)]">
      {/* Left Clinical Slate Panel */}
      <div
        className="hidden lg:flex lg:w-[44%] flex-col justify-between p-12 text-white"
        style={{
          background: "linear-gradient(160deg, #132A2E 0%, #0D1F22 100%)",
        }}
      >
        <div className="flex items-center gap-3">
          <img
            src="/app_icon.png"
            alt="PSIQUE"
            className="w-11 h-11 rounded-xl object-contain bg-white/10 p-1 border border-[#2DD4BF]/30"
          />
          <div>
            <span className="text-lg font-bold tracking-wide">PSIQUE</span>
            <p className="text-xs text-slate-400">Sistema de Gestión Clínico Psicológica</p>
          </div>
        </div>

        <div className="space-y-4 max-w-md">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/8 border border-white/10 text-xs text-[#2DD4BF]">
            Sincronización en la nube · Firebase Firestore
          </div>
          <h2 className="text-3xl font-bold leading-tight tracking-tight">
            Tu consulta clínica, organizada y accesible desde cualquier lugar.
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            Accede a expedientes de pacientes, historias clínicas, sesiones terapéuticas,
            agenda de citas, recetas médicas con exportación a PDF y control de facturación.
          </p>
        </div>

        <div className="text-xs text-slate-400">
          PSIQUE Web · Compatible con la versión de escritorio
        </div>
      </div>

      {/* Right Form Panel */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 sm:p-10 relative">
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
            <div className="lg:hidden flex items-center gap-2.5 mb-4">
              <img src="/app_icon.png" alt="PSIQUE" className="w-8 h-8 rounded-lg object-contain" />
              <span className="font-bold text-base">PSIQUE</span>
            </div>
            <h1 className="text-xl font-bold text-[var(--text-primary)]">
              {resetMode ? "Recuperar contraseña" : "Iniciar sesión"}
            </h1>
            <p className="text-xs text-[var(--text-secondary)] mt-1">
              {resetMode
                ? "Ingresa tu correo para recibir el enlace de restablecimiento."
                : "Ingresa con tu cuenta profesional de Firebase o Google."}
            </p>
          </div>

          {error && (
            <div className="mb-4 flex items-start gap-2.5 p-3 rounded-lg bg-[var(--danger-bg)] border border-red-200 text-xs text-[var(--danger)]">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {resetMsg && (
            <div className="mb-4 flex items-start gap-2.5 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800">
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
              <span className="whitespace-pre-line">{resetMsg}</span>
            </div>
          )}

          <form onSubmit={resetMode ? handleReset : handleSubmit} className="space-y-4">
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

            {!resetMode && (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-medium text-[var(--text-secondary)]">
                    Contraseña
                  </label>
                  <button
                    type="button"
                    onClick={() => {
                      setResetMode(true);
                      setError("");
                    }}
                    className="text-xs text-[#2A72DE] hover:underline"
                  >
                    ¿Olvidaste tu contraseña?
                  </button>
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 text-slate-400 pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="clinical-input w-full pl-10"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={submitting || googleLoading}
              className="clinical-btn-primary w-full py-2.5 text-sm flex items-center justify-center gap-2 disabled:opacity-60"
            >
              <span>
                {submitting
                  ? "Procesando..."
                  : resetMode
                  ? "Enviar enlace de recuperación"
                  : "Ingresar al sistema"}
              </span>
              {!submitting && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          {!resetMode && (
            <>
              <div className="my-4 flex items-center gap-3">
                <div className="flex-1 h-px bg-[var(--border-color)]" />
                <span className="text-[11px] uppercase tracking-wider text-[var(--text-secondary)]">
                  o continuar con
                </span>
                <div className="flex-1 h-px bg-[var(--border-color)]" />
              </div>

              <button
                type="button"
                onClick={handleGoogle}
                disabled={googleLoading || submitting}
                className="w-full py-2.5 px-4 rounded-lg border border-[var(--border-input)] bg-[var(--bg-surface)] hover:bg-[var(--bg-subtle)] text-sm font-medium flex items-center justify-center gap-2.5 transition-colors disabled:opacity-60"
              >
                <GoogleIcon />
                <span>{googleLoading ? "Conectando con Google..." : "Continuar con Google"}</span>
              </button>
            </>
          )}

          <div className="mt-6 pt-5 border-t border-[var(--border-color)] flex items-center justify-between text-xs text-[var(--text-secondary)]">
            {resetMode ? (
              <button
                type="button"
                onClick={() => {
                  setResetMode(false);
                  setError("");
                  setResetMsg("");
                }}
                className="text-[#2A72DE] font-medium hover:underline"
              >
                ← Volver a iniciar sesión
              </button>
            ) : (
              <>
                <span>¿No tienes cuenta?</span>
                <Link href="/register" className="text-[#2A72DE] font-semibold hover:underline">
                  Crear cuenta profesional
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
