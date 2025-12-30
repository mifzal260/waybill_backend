export default function ResultCard({ data }) {
  return (
    <div
      style={{
        marginTop: 20,
        padding: 16,
        borderRadius: 16,
        background:
          "linear-gradient(135deg, rgba(34,197,94,0.1), rgba(59,130,246,0.08))",
        border: "1px solid rgba(148,163,184,0.5)",
      }}
    >
      <h3
        style={{
          marginBottom: 12,
          fontSize: 16,
          fontWeight: 700,
          color: "#e5e7eb",
        }}
      >
        🎉 Keputusan Scan
      </h3>

      <Row label="Waybill ID" value={data.waybill_id || "-"} />
      <Row label="Negeri" value={data.negeri || "-"} />
      <Row label="Tarikh" value={data.scan_date || "-"} />

      {data.raw_text_preview && (
        <div style={{ marginTop: 12 }}>
          <p style={{ fontSize: 12, color: "#cbd5f5", marginBottom: 4 }}>
            Preview Teks:
          </p>
          <pre
            style={{
              background: "#020617",
              color: "#e5e7eb",
              padding: 10,
              borderRadius: 8,
              fontSize: 11,
              maxHeight: 160,
              overflowY: "auto",
              whiteSpace: "pre-wrap",
            }}
          >
            {data.raw_text_preview}
          </pre>
        </div>
      )}
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        marginBottom: 6,
        fontSize: 13,
      }}
    >
      <span style={{ color: "#9ca3af" }}>{label}</span>
      <span style={{ fontWeight: 600, color: "#f9fafb" }}>{value}</span>
    </div>
  );
}
