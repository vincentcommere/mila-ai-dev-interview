// src/theme.js
import { createTheme } from "@mui/material";

export const darkTheme = createTheme({
  palette: {
    mode: "dark",
    background: {
      default: "#0b0b0b",  // 🌑 fond global
      paper: "#111",       // 🌑 fond des composants (chat container)
    },
    primary: {
      main: "#76B900",     // bouton send
    },
    text: {
      primary: "#eaeaea",
      secondary: "#aaa",
    },
  },

  shape: {
    borderRadius: 12,
  },

  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: "#111",
        }
      }
    }
  }
});