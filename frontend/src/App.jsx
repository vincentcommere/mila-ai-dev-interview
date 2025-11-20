// src/App.jsx
import { useState, useRef, useEffect } from "react";
import { ThemeProvider, CssBaseline, Box } from "@mui/material";

import { darkTheme } from "./theme";
import Messages from "./components/Messages";
import InputBox from "./components/InputBox";
import { askQuestionRAG as askQuestion } from "./api";


export default function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Bonjour 👋 Comment puis-je t’aider ?" }
  ]);
  const bottomRef = useRef(null);


  const handleAsk = async () => {
    if (!query.trim()) return;

    const userInput = query;
    setQuery("");

    // Affiche immédiatement le message user
    setMessages(prev => [...prev, { role: "user", text: userInput }]);

    try {
      // Appel API backend
      const response = await askQuestion(userInput);

      // Ajoute la réponse assistant
      setMessages(prev => [
        ...prev,
        { role: "assistant", text: response }
      ]);

    } catch (err) {
      // Affiche un message assistant d’erreur
      setMessages(prev => [
        ...prev,
        { role: "assistant", text: `❌ Erreur lors de la connexion: ${err.message}` }
      ]);
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />

      <Box
        sx={{
          height: "100vh",
          width: "100vw",
          bgcolor: "background.default", // 🔥 vient du thème
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          p: 2,
        }}
      >
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            height: "100%",
            maxHeight: "900px",
            maxWidth: "700px",
            width: "100%",
            bgcolor: "background.paper", // 🔥 vient du thème
            borderRadius: 1,
            border: "1px solid #222",
            overflow: "hidden",
          }}
        >
          <Messages messages={messages} bottomRef={bottomRef} />
          <InputBox query={query} setQuery={setQuery} handleAsk={handleAsk} />
        </Box>
      </Box>
    </ThemeProvider>
  );
}
