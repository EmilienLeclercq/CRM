"use client";

import { useEffect, useMemo, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Pipeline = { id: number; name: string };

type Stage = { id: number; pipeline_id: number; name: string; position: number };

type Deal = {
  id: number;
  pipeline_id: number;
  stage_id: number;
  title: string;
  value: number;
  notes?: string | null;
};

type TokenResponse = { access_token: string; token_type: string };

const styles: Record<string, React.CSSProperties> = {
  page: {
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    background: "#f7f7fb",
    minHeight: "100vh",
    padding: "32px",
  },
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: "24px",
  },
  card: {
    background: "#fff",
    borderRadius: 12,
    padding: "24px",
    boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)",
  },
  kanban: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "16px",
  },
  column: {
    background: "#f1f5f9",
    borderRadius: 12,
    padding: "12px",
    minHeight: 320,
  },
  deal: {
    background: "#fff",
    borderRadius: 10,
    padding: "12px",
    marginBottom: "10px",
    boxShadow: "0 4px 12px rgba(15, 23, 42, 0.08)",
    cursor: "grab",
  },
  badge: {
    fontSize: 12,
    padding: "2px 8px",
    borderRadius: 999,
    background: "#e2e8f0",
  },
};

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("admin@lemonfive.test");
  const [password, setPassword] = useState("admin123");
  const [pipelines, setPipelines] = useState<Pipeline[]>([]);
  const [stages, setStages] = useState<Stage[]>([]);
  const [deals, setDeals] = useState<Deal[]>([]);
  const [activePipeline, setActivePipeline] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const stored = window.localStorage.getItem("crm-token");
    if (stored) {
      setToken(stored);
    }
  }, []);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    setError(null);
    Promise.all([
      fetch(`${API_URL}/pipelines`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((res) => res.json()),
    ])
      .then(([pipelinesData]) => {
        setPipelines(pipelinesData);
        if (pipelinesData.length > 0) {
          setActivePipeline(pipelinesData[0].id);
        }
      })
      .catch(() => setError("Impossible de charger les pipelines."))
      .finally(() => setLoading(false));
  }, [token]);

  useEffect(() => {
    if (!token || !activePipeline) return;
    setLoading(true);
    setError(null);
    Promise.all([
      fetch(`${API_URL}/pipelines/${activePipeline}/stages`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((res) => res.json()),
      fetch(`${API_URL}/deals?pipeline_id=${activePipeline}`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then((res) => res.json()),
    ])
      .then(([stagesData, dealsData]) => {
        setStages(stagesData);
        setDeals(dealsData);
      })
      .catch(() => setError("Impossible de charger le pipeline."))
      .finally(() => setLoading(false));
  }, [token, activePipeline]);

  const onLogin = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        throw new Error("Bad credentials");
      }
      const data: TokenResponse = await response.json();
      window.localStorage.setItem("crm-token", data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setError("Identifiants invalides.");
    } finally {
      setLoading(false);
    }
  };

  const onLogout = () => {
    window.localStorage.removeItem("crm-token");
    setToken(null);
    setPipelines([]);
    setStages([]);
    setDeals([]);
  };

  const dealsByStage = useMemo(() => {
    const map: Record<number, Deal[]> = {};
    stages.forEach((stage) => {
      map[stage.id] = [];
    });
    deals.forEach((deal) => {
      if (!map[deal.stage_id]) {
        map[deal.stage_id] = [];
      }
      map[deal.stage_id].push(deal);
    });
    return map;
  }, [stages, deals]);

  const onDrop = async (dealId: number, stageId: number) => {
    if (!token) return;
    const previousDeals = deals;
    setDeals((prev) => prev.map((deal) => (deal.id === dealId ? { ...deal, stage_id: stageId } : deal)));
    try {
      const response = await fetch(`${API_URL}/deals/${dealId}/stage`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ stage_id: stageId }),
      });
      if (!response.ok) {
        throw new Error("Failed");
      }
    } catch (err) {
      setDeals(previousDeals);
      setError("Impossible de déplacer le deal.");
    }
  };

  if (!token) {
    return (
      <main style={styles.page}>
        <div style={{ ...styles.card, maxWidth: 420, margin: "0 auto" }}>
          <h1 style={{ marginBottom: 8 }}>CRM Lemonfive</h1>
          <p style={{ marginBottom: 24, color: "#475569" }}>
            Connectez-vous pour accéder au pipeline.
          </p>
          <form onSubmit={onLogin} style={{ display: "grid", gap: 12 }}>
            <label>
              <div style={{ fontSize: 12, marginBottom: 6 }}>Email</div>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #cbd5f5" }}
              />
            </label>
            <label>
              <div style={{ fontSize: 12, marginBottom: 6 }}>Mot de passe</div>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #cbd5f5" }}
              />
            </label>
            <button
              type="submit"
              disabled={loading}
              style={{
                padding: "10px 16px",
                borderRadius: 10,
                border: "none",
                background: "#2563eb",
                color: "white",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {loading ? "Connexion..." : "Se connecter"}
            </button>
            {error && <p style={{ color: "#dc2626" }}>{error}</p>}
          </form>
        </div>
      </main>
    );
  }

  return (
    <main style={styles.page}>
      <div style={styles.header}>
        <div>
          <h1 style={{ marginBottom: 4 }}>Pipeline CRM</h1>
          <p style={{ color: "#64748b" }}>Glisser-déposer pour mettre à jour les deals.</p>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <select
            value={activePipeline ?? ""}
            onChange={(event) => setActivePipeline(Number(event.target.value))}
            style={{ padding: "8px 12px", borderRadius: 8 }}
          >
            {pipelines.map((pipeline) => (
              <option key={pipeline.id} value={pipeline.id}>
                {pipeline.name}
              </option>
            ))}
          </select>
          <button
            onClick={onLogout}
            style={{ padding: "8px 12px", borderRadius: 8, border: "1px solid #cbd5f5", background: "#fff" }}
          >
            Déconnexion
          </button>
        </div>
      </div>

      {loading && <p>Chargement...</p>}
      {error && <p style={{ color: "#dc2626" }}>{error}</p>}

      <section style={styles.kanban}>
        {stages.map((stage) => (
          <div
            key={stage.id}
            style={styles.column}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              const dealId = Number(event.dataTransfer.getData("text/plain"));
              if (dealId) {
                onDrop(dealId, stage.id);
              }
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 12 }}>
              <strong>{stage.name}</strong>
              <span style={styles.badge}>{dealsByStage[stage.id]?.length ?? 0}</span>
            </div>
            {dealsByStage[stage.id]?.map((deal) => (
              <div
                key={deal.id}
                style={styles.deal}
                draggable
                onDragStart={(event) => event.dataTransfer.setData("text/plain", String(deal.id))}
              >
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{deal.title}</div>
                <div style={{ fontSize: 12, color: "#475569" }}>{deal.notes || "Aucune note"}</div>
                <div style={{ marginTop: 8, fontSize: 12, color: "#0f172a" }}>€ {deal.value.toLocaleString()}</div>
              </div>
            ))}
          </div>
        ))}
      </section>
    </main>
  );
}
