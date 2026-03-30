async function callTogether({
  togetherBaseUrl,
  togetherApiKey,
  togetherModel,
  systemPrompt,
  userMessage,
  temperature = 0.8
}) {
  if (!togetherApiKey) {
    throw new Error("Missing TOGETHER_API_KEY");
  }

  const response = await fetch(`${togetherBaseUrl}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${togetherApiKey}`
    },
    body: JSON.stringify({
      model: togetherModel,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage }
      ],
      temperature
    })
  });

  let data = {};
  try {
    data = await response.json();
  } catch (_) {
    data = {};
  }
  const reply = data?.choices?.[0]?.message?.content;

  if (!response.ok) {
    const detail = data?.error?.message || data?.message || `Together API request failed (${response.status})`;
    throw new Error(detail);
  }
  if (!reply) throw new Error("Together API returned no message content");
  return reply;
}

async function callOllama({
  ollamaUrl,
  ollamaModel,
  systemPrompt,
  userMessage
}) {
  const response = await fetch(ollamaUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: ollamaModel,
      prompt: `${systemPrompt}\n\nUser: ${userMessage}`,
      stream: false
    })
  });

  const data = await response.json();
  const reply = data?.response;

  if (!response.ok) throw new Error(data?.error || "Ollama request failed");
  if (!reply) throw new Error("Ollama returned no response");
  return reply;
}

function createLlmClient(config) {
  return {
    async generate({ provider, systemPrompt, userMessage, temperature }) {
      if (provider === "ollama") {
        return callOllama({
          ollamaUrl: config.ollamaUrl,
          ollamaModel: config.ollamaModel,
          systemPrompt,
          userMessage
        });
      }
      return callTogether({
        togetherBaseUrl: config.togetherBaseUrl,
        togetherApiKey: config.togetherApiKey,
        togetherModel: config.togetherModel,
        systemPrompt,
        userMessage,
        temperature
      });
    }
  };
}

module.exports = {
  createLlmClient
};
