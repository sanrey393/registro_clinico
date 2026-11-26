const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const STORAGE_KEY = "psique_session";

export interface AuthSession {
  uid: string;
  email: string;
  display_name: string;
  rol: string;
  id_token: string;
  refresh_token: string;
}

export function getStoredSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AuthSession) : null;
  } catch {
    return null;
  }
}

export function setStoredSession(session: AuthSession | null): void {
  if (typeof window === "undefined") return;
  if (!session) {
    localStorage.removeItem(STORAGE_KEY);
  } else {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }
}

async function tryRefreshSession(): Promise<AuthSession | null> {
  const current = getStoredSession();
  if (!current?.refresh_token) return null;
  try {
    const res = await fetch(`${API_BASE}/api/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: current.refresh_token }),
    });
    if (!res.ok) {
      setStoredSession(null);
      return null;
    }
    const data = await res.json();
    const updated: AuthSession = {
      uid: data.uid || current.uid,
      email: data.email || current.email,
      display_name: data.display_name || current.display_name,
      rol: data.rol || current.rol,
      id_token: data.id_token,
      refresh_token: data.refresh_token || current.refresh_token,
    };
    setStoredSession(updated);
    return updated;
  } catch {
    return null;
  }
}

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const session = getStoredSession();
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (session?.id_token) {
    headers.set("Authorization", `Bearer ${session.id_token}`);
  }

  let res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401 && session?.refresh_token) {
    const refreshed = await tryRefreshSession();
    if (refreshed?.id_token) {
      headers.set("Authorization", `Bearer ${refreshed.id_token}`);
      res = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
      });
    }
  }

  if (!res.ok) {
    let message = `Error ${res.status}`;
    try {
      const err = await res.json();
      message = err.detail || err.message || message;
    } catch {
      // ignore non-json error
    }
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

export async function downloadPdf(
  endpoint: string,
  payload: unknown,
  fallbackFilename: string
): Promise<void> {
  const session = getStoredSession();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (session?.id_token) {
    headers["Authorization"] = `Bearer ${session.id_token}`;
  }

  let res = await fetch(`${API_BASE}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (res.status === 401 && session?.refresh_token) {
    const refreshed = await tryRefreshSession();
    if (refreshed?.id_token) {
      headers["Authorization"] = `Bearer ${refreshed.id_token}`;
      res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });
    }
  }

  if (!res.ok) {
    let message = `No se pudo generar el PDF (${res.status})`;
    try {
      const err = await res.json();
      message = err.detail || message;
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fallbackFilename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
