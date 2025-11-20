// src/components/InputBox.jsx
import SendIcon from "@mui/icons-material/Send";

export default function InputBox({ query, setQuery, handleAsk }) {
  return (
    <div style={{
      display: "flex",
      gap: "10px",
      padding: "10px",
      borderTop: "1px solid #333",
      background: "#1a1a1a",
    }}>
      <textarea
        style={{
          flex: 1,
          background: "#111",
          color: "white",
          padding: "5px",
          borderRadius: "8px",
          resize: "none",
          minHeight: "40px",
          maxHeight: "120px",
          border: "1px solid #333",
        }}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        rows={1}
      />

      <button
        onClick={handleAsk}
        style={{
          background: "#76B900",
          border: "none",
          padding: "0 18px",
          borderRadius: "8px",
          cursor: "pointer"
        }}>
        <SendIcon />
      </button>
    </div>
  );
}
