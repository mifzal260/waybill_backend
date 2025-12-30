import { useState } from "react";
import axios from "axios";
import ResultCard from "../components/ResultCard";

// ⬇️ Konfigurasi URL
const getBaseUrl = () => {
  const PC_IP = "192.168.0.102"; 
  return `http://${PC_IP}:8000`;
};

const API_BASE = getBaseUrl();

export default function ScannerPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // ⬇️ Function untuk test connection
  const testConnection = async () => {
    try {
      console.log("Testing connection to:", API_BASE);
      const response = await fetch(API_BASE);
      const text = await response.text();
      console.log("Connection test successful:", text.substring(0, 100));
      alert("Connection OK!");
    } catch (err) {
      console.error("Connection test failed:", err);
      alert("Connection failed: " + err.message);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Sila pilih gambar waybill terlebih dahulu.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      console.log("Sending to:", `${API_BASE}/upload-waybill`);
      
      const res = await axios.post(`${API_BASE}/upload-waybill`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(res.data);
    } catch (err) {
      console.error("Upload error:", err);
      setError(`Gagal memproses gambar. Pastikan API FastAPI sedang berjalan di ${API_BASE}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: 450,
        margin: "0 auto",
        padding: 20,
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        minHeight: "100vh",
        background: "#0f172a",
        color: "#e5e7eb",
      }}
    >
      <h2 style={{ textAlign: "center", marginBottom: 6, fontSize: 22 }}>
        📦 Waybill Scanner
      </h2>

      <p
        style={{
          textAlign: "center",
          color: "#9ca3af",
          fontSize: 13,
          marginBottom: 20,
        }}
      >
        Muat naik gambar waybill & sistem akan detect <b>negeri</b> dan{" "}
        <b>tarikh</b>.
      </p>

      {/* Upload box */}
      <div
        style={{
          marginTop: 10,
          padding: 20,
          borderRadius: 16,
          background: "#020617",
          border: "1px solid #1f2937",
          textAlign: "center",
        }}
      >
        <label
          style={{
            display: "block",
            fontSize: 13,
            marginBottom: 8,
            color: "#9ca3af",
          }}
        >
          Pilih gambar waybill
        </label>

        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files[0])}
          style={{
            width: "100%",
            padding: 8,
            borderRadius: 999,
            border: "1px solid #4b5563",
            background: "#020617",
            color: "#e5e7eb",
            fontSize: 13,
          }}
        />

        {file && (
          <p
            style={{
              marginTop: 10,
              fontSize: 12,
              color: "#e5e7eb",
              wordBreak: "break-all",
            }}
          >
            📷 {file.name}
          </p>
        )}
      </div>

      {/* ⬇️ BUTTON TEST CONNECTION */}
      <button 
        onClick={testConnection}
        style={{
          width: "100%",
          marginTop: 10,
          padding: 12,
          background: "#3b82f6",
          color: "white",
          border: "none",
          borderRadius: 8,
          fontSize: 14,
          fontWeight: "600",
        }}
      >
        Test Connection First
      </button>

      {/* Button Upload */}
      <button
        onClick={handleUpload}
        disabled={loading}
        style={{
          width: "100%",
          marginTop: 18,
          padding: 14,
          borderRadius: 999,
          background: loading ? "#6b7280" : "#22c55e",
          color: "#020617",
          border: "none",
          fontSize: 15,
          fontWeight: 700,
          cursor: loading ? "not-allowed" : "pointer",
          boxShadow: "0 8px 20px rgba(34,197,94,0.3)",
        }}
      >
        {loading ? "Memproses..." : "Scan Waybill"}
      </button>

      {/* Error */}
      {error && (
        <p style={{ color: "#fca5a5", marginTop: 10, fontSize: 13 }}>{error}</p>
      )}

      {/* Result */}
      {result && <ResultCard data={result} />}
    </div>
  );
}