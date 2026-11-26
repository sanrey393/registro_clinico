"use client";

import React, { useState } from "react";
import { X, Calculator } from "lucide-react";

export function CalculatorsModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<"imc" | "dosis" | "edad">("imc");

  // IMC
  const [peso, setPeso] = useState("70");
  const [talla, setTalla] = useState("1.70");

  // Dosis
  const [pesoDosis, setPesoDosis] = useState("25");
  const [mgKg, setMgKg] = useState("15");
  const [tomas, setTomas] = useState("3");

  // Edad
  const [fechaNac, setFechaNac] = useState("2000-01-15");

  if (!open) return null;

  const pNum = parseFloat(peso) || 0;
  const tNum = parseFloat(talla) || 0;
  const imc = tNum > 0 ? pNum / (tNum * tNum) : 0;
  const imcCat =
    imc <= 0
      ? "—"
      : imc < 18.5
      ? "Bajo peso"
      : imc < 25
      ? "Peso normal"
      : imc < 30
      ? "Sobrepeso"
      : imc < 35
      ? "Obesidad Grado I"
      : imc < 40
      ? "Obesidad Grado II"
      : "Obesidad Grado III";

  const pdNum = parseFloat(pesoDosis) || 0;
  const mkNum = parseFloat(mgKg) || 0;
  const tomasNum = Math.max(1, parseInt(tomas, 10) || 1);
  const dosisDiaria = pdNum * mkNum;
  const dosisPorToma = dosisDiaria / tomasNum;

  const calcEdadExacta = () => {
    if (!fechaNac) return null;
    const nac = new Date(fechaNac + "T00:00:00");
    const hoy = new Date();
    if (isNaN(nac.getTime()) || nac > hoy) return null;
    let years = hoy.getFullYear() - nac.getFullYear();
    let months = hoy.getMonth() - nac.getMonth();
    let days = hoy.getDate() - nac.getDate();
    if (days < 0) {
      months -= 1;
      const prevMonth = new Date(hoy.getFullYear(), hoy.getMonth(), 0);
      days += prevMonth.getDate();
    }
    if (months < 0) {
      years -= 1;
      months += 12;
    }
    return { years, months, days };
  };

  const edadRes = calcEdadExacta();

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
      <div className="clinical-card w-full max-w-lg p-6">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-color)]">
          <div className="flex items-center gap-2">
            <Calculator className="w-5 h-5 text-[#0F766E]" />
            <h2 className="text-base font-bold">Calculadoras Clínicas</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-[var(--bg-subtle)]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-1 rounded-lg bg-[var(--bg-subtle)] mb-5">
          {[
            { id: "imc", label: "IMC" },
            { id: "dosis", label: "Dosis por Peso" },
            { id: "edad", label: "Edad Exacta" },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id as "imc" | "dosis" | "edad")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-colors ${
                tab === t.id
                  ? "bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-xs"
                  : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {tab === "imc" && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Peso (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={peso}
                  onChange={(e) => setPeso(e.target.value)}
                  className="clinical-input w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Estatura (m)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={talla}
                  onChange={(e) => setTalla(e.target.value)}
                  className="clinical-input w-full"
                />
              </div>
            </div>
            <div className="p-4 rounded-xl bg-teal-50/70 dark:bg-teal-950/30 border border-teal-200 dark:border-teal-800">
              <div className="text-xs text-[var(--text-secondary)]">
                Índice de Masa Corporal (IMC)
              </div>
              <div className="text-2xl font-bold text-[#0F766E] dark:text-[#2DD4BF] mt-1">
                {imc > 0 ? imc.toFixed(2) : "—"} kg/m²
              </div>
              <div className="text-xs font-semibold mt-1">
                Clasificación OMS: {imcCat}
              </div>
            </div>
          </div>
        )}

        {tab === "dosis" && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Peso (kg)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={pesoDosis}
                  onChange={(e) => setPesoDosis(e.target.value)}
                  className="clinical-input w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  mg / kg / día
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={mgKg}
                  onChange={(e) => setMgKg(e.target.value)}
                  className="clinical-input w-full"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                  Tomas / día
                </label>
                <input
                  type="number"
                  min={1}
                  max={12}
                  value={tomas}
                  onChange={(e) => setTomas(e.target.value)}
                  className="clinical-input w-full"
                />
              </div>
            </div>
            <div className="p-4 rounded-xl bg-blue-50/70 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
              <div className="text-xs text-[var(--text-secondary)]">
                Cálculo Posológico
              </div>
              <div className="text-xl font-bold text-[#2A72DE] mt-1">
                {dosisPorToma.toFixed(1)} mg por toma
              </div>
              <div className="text-xs text-[var(--text-secondary)] mt-1">
                Dosis diaria total: <strong>{dosisDiaria.toFixed(1)} mg/día</strong> cada{" "}
                {(24 / tomasNum).toFixed(0)} horas
              </div>
            </div>
          </div>
        )}

        {tab === "edad" && (
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[var(--text-secondary)] mb-1">
                Fecha de Nacimiento
              </label>
              <input
                type="date"
                value={fechaNac}
                onChange={(e) => setFechaNac(e.target.value)}
                className="clinical-input w-full"
              />
            </div>
            <div className="p-4 rounded-xl bg-[var(--bg-subtle)] border border-[var(--border-color)]">
              <div className="text-xs text-[var(--text-secondary)]">
                Edad Cronológica Exacta
              </div>
              <div className="text-xl font-bold mt-1">
                {edadRes
                  ? `${edadRes.years} años, ${edadRes.months} meses y ${edadRes.days} días`
                  : "Fecha inválida"}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
