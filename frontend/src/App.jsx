import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [msg, setMsg] = useState("");
  const [history, setHistory] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const send = async () => {
    if (!msg || loading) return;
    const text = msg;
    setMsg("");
    setHistory((h) => [...h, { from: "user", text }]);
    setLoading(true);

    try {
      const res = await axios.post("/chat", {
        message: text,
        session_id: sessionId,
      });
      if (res.data.session_id) setSessionId(res.data.session_id);
      setHistory((h) => [...h, { from: "bot", text: res.data.reply }]);
    } catch (e) {
      setHistory((h) => [...h, { from: "bot", text: "Erreur de connexion." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const newSession = () => {
    setHistory([]);
    setSessionId(null);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Assistant RH</h2>
        <button onClick={newSession} style={styles.newBtn}>
          Nouvelle conversation
        </button>
      </div>

      <div style={styles.chatBox}>
        {history.length === 0 && (
          <div style={styles.empty}>
            <p>Bonjour ! Je suis votre assistant RH.</p>
            <p style={{ fontSize: 14, color: "#888" }}>
              Je peux consulter les fiches employes, les soldes de conges, et
              les politiques internes.
            </p>
          </div>
        )}
        {history.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              ...(m.from === "user" ? styles.userMsg : styles.botMsg),
            }}
          >
            <div style={styles.msgLabel}>
              {m.from === "user" ? "Vous" : "Assistant RH"}
            </div>
            <div style={{ whiteSpace: "pre-wrap" }}>{m.text}</div>
          </div>
        ))}
        {loading && (
          <div style={{ ...styles.message, ...styles.botMsg }}>
            <div style={styles.msgLabel}>Assistant RH</div>
            <div style={styles.typing}>Recherche en cours...</div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div style={styles.inputRow}>
        <input
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Posez votre question RH..."
          style={styles.input}
          disabled={loading}
        />
        <button onClick={send} style={styles.sendBtn} disabled={loading}>
          Envoyer
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 700,
    margin: "40px auto",
    fontFamily: "'Segoe UI', Arial, sans-serif",
    display: "flex",
    flexDirection: "column",
    height: "calc(100vh - 80px)",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  title: { margin: 0, color: "#1a1a2e" },
  newBtn: {
    padding: "6px 14px",
    border: "1px solid #ccc",
    borderRadius: 6,
    background: "#fff",
    cursor: "pointer",
    fontSize: 13,
  },
  chatBox: {
    flex: 1,
    overflowY: "auto",
    border: "1px solid #e0e0e0",
    borderRadius: 10,
    padding: 16,
    background: "#fafafa",
    marginBottom: 12,
  },
  empty: { textAlign: "center", padding: "60px 20px", color: "#555" },
  message: {
    marginBottom: 12,
    padding: "10px 14px",
    borderRadius: 10,
    maxWidth: "80%",
    fontSize: 14,
    lineHeight: 1.5,
  },
  userMsg: {
    background: "#d4e6ff",
    marginLeft: "auto",
    textAlign: "right",
  },
  botMsg: {
    background: "#fff",
    border: "1px solid #e0e0e0",
    marginRight: "auto",
  },
  msgLabel: {
    fontWeight: 600,
    fontSize: 12,
    marginBottom: 4,
    color: "#666",
  },
  typing: { color: "#999", fontStyle: "italic" },
  inputRow: { display: "flex", gap: 8 },
  input: {
    flex: 1,
    padding: "10px 14px",
    borderRadius: 8,
    border: "1px solid #ccc",
    fontSize: 14,
  },
  sendBtn: {
    padding: "10px 20px",
    borderRadius: 8,
    border: "none",
    background: "#1a73e8",
    color: "#fff",
    cursor: "pointer",
    fontSize: 14,
    fontWeight: 600,
  },
};
