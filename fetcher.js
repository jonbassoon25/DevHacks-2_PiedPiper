// You need your Supermemory MCP server URL and (optionally) API key, plus Gemini 2.5 Flash endpoint and credentials

const SUPERMEMORY_MCP_URL = "https://api.supermemory.ai/mcp"; // Replace with your MCP URL
const GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"; // Example endpoint

const SUPERMEMORY_API_KEY = "sm_7v34ad1Mm5XeKoiM2gNd2V_IZMERieGyPMWxXBJEeoiTNLeVyBKFznTiBielvymJErPcdiCrXTlXDevMqWYKirP"; // If self-hosted; otherwise, URL may be enough
const GEMINI_API_KEY = "AIzaSyAkvDsC5hBAWi_-7d-jb1Pdkz7u8_lO0eE"; // Replace with real key

async function fetchMemories(prompt) {
  const url = "https://api.supermemory.ai/v3/search";  // Use main API, not /mcp
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${SUPERMEMORY_API_KEY}`
      },
      body: JSON.stringify({
        q: prompt,  // Changed from 'query' to 'q'
        limit: 10,  // Optional: adjust as needed
        containerTag: 'default'  // Add this to target Default project (verify tag in console)
      })
    });

    if (!response.ok) {
      console.error(`API Error: ${response.status} - ${response.statusText}`);
      return [];
    }

    const data = await response.json();
    console.log("Full API Response:", data);  // For debugging
    return data.results || [];
  } catch (error) {
    console.error("Fetch Error:", error);
    return [];
  }
}

async function askGemini(memories, prompt) {
  // Construct a message with context from memories
  const systemPrompt =
    "Use ONLY the following user memories to help answer the prompt:\n" +
    memories.map((m, i) => `${i + 1}. ${m.content || m.text}`).join('\n');
  const requestBody = {
    contents: [
      { role: "user", parts: [{ text: prompt }] },
      { role: "system", parts: [{ text: systemPrompt }] }
    ]
  };

  const res = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });
  const reply = await res.json();
  return reply?.candidates?.[0]?.content?.parts?.[0]?.text || "No reply.";
}

// Main function
async function supermemoryGeminiAssistant(userPrompt) {
  console.log("User Prompt:", userPrompt);

  // Step 1: Retrieve relevant memories
  const memories = await fetchMemories(userPrompt);
  console.log("Relevant memories:", memories);

  // Step 2: Generate response with Gemini
  const reply = await askGemini(memories, userPrompt);
  console.log("Gemini Reply:", reply);
}

// Example usage:
supermemoryGeminiAssistant("How big is tempe marketplace?");

