"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import {
  AuthSession,
  apiFetch,
  getStoredSession,
  setStoredSession,
} from "@/lib/api";
import { signInWithGooglePopup } from "@/lib/firebase-client";

interface AuthContextValue {
  user: AuthSession | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  register: (nombre: string, email: string, password: string, rol?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = getStoredSession();
    if (stored?.id_token) {
      setUser(stored);
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await apiFetch<AuthSession>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setStoredSession(data);
    setUser(data);
  }, []);

  const loginWithGoogle = useCallback(async () => {
    const googleCred = await signInWithGooglePopup();
    const data = await apiFetch<AuthSession>("/api/auth/google", {
      method: "POST",
      body: JSON.stringify(googleCred),
    });
    setStoredSession(data);
    setUser(data);
  }, []);

  const register = useCallback(
    async (nombre_completo: string, email: string, password: string, rol = "psicologo") => {
      const data = await apiFetch<AuthSession>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify({ nombre_completo, email, password, rol }),
      });
      setStoredSession(data);
      setUser(data);
    },
    []
  );

  const logout = useCallback(() => {
    setStoredSession(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, loginWithGoogle, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }
  return ctx;
}
