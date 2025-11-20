// frontend/src/api.js

export async function askDumbQuestion(query) {
  try {
    const res = await fetch("/api/dumb", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "query": query }),
    });

    if (!res.ok) {
      throw new Error("Backend error: " + res.status);
    }

    const data = await res.json();
    return data.answer;
  } catch (err) {
    console.error("API error:", err);
    throw err;
  }
}

export async function askQuestionLLM(query) {
  try {
    const res = await fetch("/api/llm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "query": query }),
    });

    if (!res.ok) {
      throw new Error("Backend error: " + res.status);
    }

    const data = await res.json();
    return data.answer;
  } catch (err) {
    console.error("API error:", err);
    throw err;
  }
}

export async function askQuestionRAG(query) {
  try {
    const res = await fetch("/api/rag", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "query": query }),
    });

    if (!res.ok) {
      throw new Error("Backend error: " + res.status);
    }

    const data = await res.json();
    return data.answer;
  } catch (err) {
    console.error("API error:", err);
    throw err;
  }
}

// export async function askQuestionLLM(query) {
//   try {
//     const controller = new AbortController();
//     const timeout = setTimeout(() => controller.abort(), 20000); // 20 sec timeout

//     const res = await fetch("/api/llm", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ "query": query }),
//       signal: controller.signal
//     });

//     clearTimeout(timeout);

//     // Backend responded but with error code
//     if (!res.ok) {
//       let message = `Backend error: ${res.status}`;

//       try {
//         const errData = await res.json();
//         if (errData?.answer) message += ` – ${errData.answer}`;
//       } catch (_) {
//         /* ignore JSON parse errors */
//       }

//       throw new Error(message);
//     }

//     // Parse answer
//     const data = await res.json();
//     return data.answer;

//   } catch (err) {
//     // Network or timeout issues
//     if (err.name === "AbortError") {
//       throw new Error("Request timed out (server took too long).");
//     }

//     console.error("API error:", err);
//     throw err;
//   }
// }
