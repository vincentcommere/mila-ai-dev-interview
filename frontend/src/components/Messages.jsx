// src/components/Messages.jsx
import ChatBubble from "./ChatBubble";

export default function Messages({ messages, bottomRef }) {
  return (
    <div style={{
      flexGrow: 1,
      overflowY: "auto",
      padding: "20px",
      display: "flex",
      flexDirection: "column",
      gap: "12px",
      background: "#141414",
    }}>
      {messages.map((msg, i) => (
        <ChatBubble
          key={i}
          text={msg.text}
          isUser={msg.role === "user"}
        />
      ))}

      <div ref={bottomRef} />
    </div>
  );
}
