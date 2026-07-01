"use client";

import { useState } from "react";

type PlanBlock = {
  day: string;
  time_range: string;
  activity: string;
  interest_area: string;
  intensity: "low" | "medium" | "high";
  rationale: string;
};

type WeeklyPlan = {
  week_summary: string;
  blocks: PlanBlock[];
  burnout_risk_notes: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

const intensityColor: Record<string, string> = {
  low: "bg-emerald-100 text-emerald-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-rose-100 text-rose-800",
};

export default function Home() {
  const [interests, setInterests] = useState("Guitar, Working out, Side project, Reading");
  const [budget, setBudget] = useState(10);
  const [energyNotes, setEnergyNotes] = useState("Mornings are best, weekends are freer");
  const [feedback, setFeedback] = useState("");
  const [plan, setPlan] = useState<WeeklyPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          interests: interests.split(",").map((s) => s.trim()).filter(Boolean),
          weekly_time_budget_hours: budget,
          energy_notes: energyNotes,
          existing_commitments: [],
          past_week_feedback: feedback,
        }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const data = await res.json();
      setPlan(data);
    } catch (e: any) {
      setError(e.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-50 px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <h1 className="text-2xl font-semibold text-neutral-900">Day Planner AI</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Balance multiple interests over time without burning out.
        </p>

        <div className="mt-6 space-y-4 rounded-xl border border-neutral-200 bg-white p-5">
          <label className="block">
            <span className="text-sm font-medium text-neutral-700">
              Interests (comma-separated)
            </span>
            <input
              className="mt-1 w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm"
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-neutral-700">
              Weekly time budget (hours)
            </span>
            <input
              type="number"
              className="mt-1 w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm"
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-neutral-700">Energy notes</span>
            <input
              className="mt-1 w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm"
              value={energyNotes}
              onChange={(e) => setEnergyNotes(e.target.value)}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-neutral-700">
              How did last week feel? (optional)
            </span>
            <input
              className="mt-1 w-full rounded-lg border border-neutral-300 px-3 py-2 text-sm"
              placeholder="e.g. felt rushed on weekdays, weekend was fine"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </label>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full rounded-lg bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {loading ? "Generating..." : "Generate weekly plan"}
          </button>

          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>

        {plan && (
          <div className="mt-8 space-y-4">
            <div className="rounded-xl border border-neutral-200 bg-white p-5">
              <h2 className="text-sm font-semibold text-neutral-900">Week summary</h2>
              <p className="mt-1 text-sm text-neutral-600">{plan.week_summary}</p>
            </div>

            <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">
              <h2 className="text-sm font-semibold text-amber-900">Burnout risk notes</h2>
              <p className="mt-1 text-sm text-amber-800">{plan.burnout_risk_notes}</p>
            </div>

            <div className="space-y-2">
              {plan.blocks.map((b, i) => (
                <div
                  key={i}
                  className="flex items-start justify-between rounded-lg border border-neutral-200 bg-white p-4"
                >
                  <div>
                    <div className="text-sm font-medium text-neutral-900">
                      {b.day} · {b.time_range}
                    </div>
                    <div className="text-sm text-neutral-700">{b.activity}</div>
                    <div className="mt-1 text-xs text-neutral-400">{b.interest_area}</div>
                    <div className="mt-1 text-xs text-neutral-500">{b.rationale}</div>
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-2 py-1 text-xs font-medium ${intensityColor[b.intensity]}`}
                  >
                    {b.intensity}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
