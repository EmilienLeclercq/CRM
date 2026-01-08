"use client";

import { useEffect, useMemo, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const storageKeys = {
  access: "lemonfive.access",
  refresh: "lemonfive.refresh",
};

async function apiFetch(path, options = {}) {
  const accessToken = window.localStorage.getItem(storageKeys.access);
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Erreur" }));
    throw new Error(error.detail || "Erreur API");
  }
  return response.json();
}

export default function Home() {
  const [email, setEmail] = useState("admin@lemonfive.local");
  const [password, setPassword] = useState("admin123");
  const [authError, setAuthError] = useState("");
  const [user, setUser] = useState(null);
  const [pipelines, setPipelines] = useState([]);
  const [stages, setStages] = useState([]);
  const [deals, setDeals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("Chargement...");

  const selectedPipeline = pipelines[0];

  useEffect(() => {
    const accessToken = window.localStorage.getItem(storageKeys.access);
    if (accessToken) {
      bootstrap();
    } else {
      setStatus("Veuillez vous connecter.");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(event) {
    event.preventDefault();
    setAuthError("");
    setLoading(true);
    try {
      const response = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      window.localStorage.setItem(storageKeys.access, response.access_token);
      window.localStorage.setItem(storageKeys.refresh, response.refresh_token);
      await bootstrap();
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function bootstrap() {
    setLoading(true);
    try {
      const me = await apiFetch("/auth/me");
      setUser(me);
      const pipelineData = await apiFetch("/pipelines");
      setPipelines(pipelineData);
      if (pipelineData.length > 0) {
        const stageData = await apiFetch(`/stages?pipeline_id=${pipelineData[0].id}`);
        setStages(stageData);
      }
      const dealsData = await apiFetch("/deals");
      setDeals(dealsData);
      setStatus("");
    } catch (error) {
      setStatus(error.message);
    } finally {
      setLoading(false);
    }
  }

  const dealsByStage = useMemo(() => {
    return stages.reduce((acc, stage) => {
      acc[stage.id] = deals.filter((deal) => deal.stage_id === stage.id);
      return acc;
    }, {});
  }, [stages, deals]);

  function logout() {
    window.localStorage.removeItem(storageKeys.access);
    window.localStorage.removeItem(storageKeys.refresh);
    setUser(null);
    setPipelines([]);
    setStages([]);
    setDeals([]);
    setStatus("Veuillez vous connecter.");
  }

  async function handleDrop(event, stageId) {
    event.preventDefault();
    const dealId = event.dataTransfer.getData("text/plain");
    if (!dealId) return;
    try {
      const updated = await apiFetch(`/deals/${dealId}/stage`, {
        method: "PATCH",
        body: JSON.stringify({ stage_id: stageId }),
      });
      setDeals((prev) => prev.map((deal) => (deal.id === updated.id ? updated : deal)));
    } catch (error) {
      setStatus(error.message);
    }
  }

  if (!user) {
    return (
      <main className="page">
        <div className="card login-form">
          <h1>Connexion Lemonfive</h1>
          <form onSubmit={login} className="login-form">
            <label>
              Email
              <input value={email} onChange={(event) => setEmail(event.target.value)} />
            </label>
            <label>
              Mot de passe
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {authError && <div className="status">{authError}</div>}
            <button type="submit" disabled={loading}>
              {loading ? "Connexion..." : "Se connecter"}
            </button>
            {status && <div className="status">{status}</div>}
          </form>
        </div>
      </main>
    );
  }

  return (
    <main className="page">
      <div className="header">
        <div>
          <h1>Pipeline {selectedPipeline ? selectedPipeline.name : "-"}</h1>
          <div className="status">Bienvenue {user.full_name || user.email}</div>
        </div>
        <button className="logout" onClick={logout}>
          Se déconnecter
        </button>
      </div>
      {status && <div className="status">{status}</div>}
      <section className="kanban">
        {stages.map((stage) => (
          <div
            key={stage.id}
            className="column"
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => handleDrop(event, stage.id)}
          >
            <div className="column-header">{stage.name}</div>
            {dealsByStage[stage.id]?.map((deal) => (
              <div
                key={deal.id}
                className="deal-card"
                draggable
                onDragStart={(event) => event.dataTransfer.setData("text/plain", deal.id)}
              >
                <div>{deal.title}</div>
                <div className="deal-amount">
                  {deal.amount} {deal.currency}
                </div>
              </div>
            ))}
          </div>
        ))}
      </section>
    </main>
  );
}
