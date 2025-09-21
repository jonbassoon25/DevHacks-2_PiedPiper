# DevHacks-2_PiedPiper — Quick Start

This repository produces per-row location/activity tags with a local Ollama model (gemma2), converts tags to fixed-size vectors, and runs the application that consumes those vectors.

Summary run order (canonical)
1. Start Ollama (gemma2) and keep it running.
2. Generate per-row tags: Python_ML/build_tags.py → produces `location_tags.json` and `location_tags.npy`.
3. Vectorize tags: Python_ML/vectorize_tags.py → produces `location_vectors.npy`.
4. Start the app: `node app.js`

Prerequisites
- Python 3.12.x
- Node.js (for app.js)
- Ollama installed with the model `gemma2` pulled
- From project root, install Python 3.12 deps if you need them and then install the requirements

Start Ollama (required for high-quality tags)
- In a terminal:
  ollama run gemma2
- If Ollama starts on a different host/port, set the OLLAMA_URL environment variable:
  - PowerShell (session):
    $env:OLLAMA_URL = 'http://127.0.0.1:11434'
    $env:OLLAMA_MODEL = 'gemma2'

Step 1 — Generate tags (build_tags.py)
- Go to Python_ML and run:
  python build_tags.py
- Behavior:
- The script requires Ollama to be running and will raise an error if Ollama is unreachable.
- Outputs (Python_ML folder):
  - location_tags.npy — NumPy object-array (one element per row; each element is a list of tags). Load with np.load(..., allow_pickle=True).
  - location_tags.json — JSON list-of-lists (same data, human readable)

Step 2 — Vectorize tags (vectorize_tags.py)
- After tags are produced move the location_tags.npy to the Python_ML directory
- Run vectorize_tags.py
- Expected output:
  - location_vectors.npy — fixed-size numeric vectors for each row (shape: n_rows × n_features)
- Notes:
  - vectorize_tags.py builds a common tag vocabulary so all vectors have the same length.

Step 3 — Run the application (app.js)
- From project root:
  npm install the necessary dependencies 
  node app.js
