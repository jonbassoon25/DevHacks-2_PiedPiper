import fetch from 'node-fetch';
import dotenv from 'dotenv';

dotenv.config();

const SUPERMEMORY_API_KEY = "sm_7v34ad1Mm5XeKoiM2gNd2V_IZMERieGyPMWxXBJEeoiTNLeVyBKFznTiBielvymJErPcdiCrXTlXDevMqWYKirP";
const GEMINI_API_KEY = "AIzaSyAkvDsC5hBAWi_-7d-jb1Pdkz7u8_lO0eE";

if (!SUPERMEMORY_API_KEY || !GEMINI_API_KEY) {
    console.error("Error: Missing API keys. Please set SUPERMEMORY_API_KEY and GEMINI_API_KEY in your .env file.");
    process.exit(1);
}

// Supermemory API endpoint
const SUPERMEMORY_API_URL = 'https://api.supermemory.ai/v3';

// Gemini API endpoint (for gemini-2.5-flash)
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=';

// The container tag you're using to filter memories (e.g., "Default Project")
const MEMORY_CONTAINER_TAG = "Default Project";

/**
 * Searches Supermemory for relevant memories based on a query.
 * @param {string} query The user's prompt.
 * @returns {Promise<string>} A string of retrieved memories or an empty string.
 */
async function searchSupermemory(query) {
    try {
        const response = await fetch(`${SUPERMEMORY_API_URL}/search`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${SUPERMEMORY_API_KEY}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                q: query,
                containerTags: [MEMORY_CONTAINER_TAG],
                limit: 5 // Get up to 5 relevant memories
            }),
        });

        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            // Combine the top results into a single string
            return data.results.map(result => result.content).join('\n');
        } else {
            return '';
        }
    } catch (error) {
        console.error("Error searching Supermemory:", error);
        return '';
    }
}

/**
 * Sends a prompt to the Gemini API with additional context.
 * @param {string} prompt The full prompt to send.
 * @returns {Promise<string>} The response from the Gemini model.
 */
async function getGeminiResponse(prompt) {
    try {
        const response = await fetch(`${GEMINI_API_URL}${GEMINI_API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text: prompt }]
                }]
            }),
        });

        const data = await response.json();
        const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (text) {
            return text;
        } else {
            console.error("Error: Gemini response was empty or malformed.");
            return "Sorry, I couldn't get a response from Gemini.";
        }
    } catch (error) {
        console.error("Error calling Gemini API:", error);
        return "Sorry, there was an issue connecting to the Gemini API.";
    }
}

/**
 * Main function to run the process.
 */
async function run() {
    const userQuery = "What is the rating and number of reviews for Funtasticks Family Fun Park?";

    console.log(`Searching Supermemory for memories related to: "${userQuery}"...`);
    const retrievedMemories = await searchSupermemory(userQuery);

    // DEBUG: Log the retrieved memories to see what's being found
    console.log("\n--- Retrieved Memories ---");
    console.log(retrievedMemories || "None found.");
    console.log("------------------------\n");

    let fullPrompt;
    if (retrievedMemories && retrievedMemories.trim() !== '') {
        console.log("Memories found! Building a robust prompt.");
        fullPrompt = `You are a helpful assistant with a dedicated memory. Your task is to answer the user's question based ONLY on the information provided below.

---
**Memories:**
${retrievedMemories}
---

**User's Question:** ${userQuery}

**Instructions:**
1. Carefully review the "Memories" section to find the answer.
2. If the answer is found in the memories, provide it directly.
3. If the answer cannot be found in the memories, you MUST respond with "I do not have that information in my memory."
4. Do not use any other knowledge or external sources.`;

    } else {
        console.log("No relevant memories found. Asking Gemini with just the user's query.");
        // If no memories are found, you might not want to call Gemini at all,
        // or you can handle it differently. For now, we'll tell the user.
        console.log("\n--- Gemini's Response ---");
        console.log("I do not have that information in my memory.");
        return; // Exit the function since there's no context to use
    }

    console.log("\nCalling Gemini API...");
    const geminiResponse = await getGeminiResponse(fullPrompt);

    console.log("\n--- Gemini's Response ---");
    console.log(geminiResponse);
}

// Run the program
run();