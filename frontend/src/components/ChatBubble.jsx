// src/components/ChatBubble.jsx
export default function ChatBubble({ text, isUser }) {
  return (
    <div style={{
      maxWidth: "75%",
      alignSelf: isUser ? "flex-end" : "flex-start",
      background: isUser ? "#3e6fda" : "#76B900",
      color: "white",
      padding: "10px 14px",
      borderRadius: "14px",
      lineHeight: "1.4",
      whiteSpace: "pre-wrap",
      wordBreak: "break-word",
      fontFamily: "system-ui",
    }}>
      {text}
    </div>
  );
}
