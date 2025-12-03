<h1>GomMold Backend</h1>

<p>
The backend API for the <strong>GomMold</strong> mobile application.  
Handles user authentication, ONNX mold detection, Firebase storage, history management, and chatbot support.
Designed for deployment on <strong>Railway (Linux containers)</strong>.
</p>

<hr>

<h2>🚀 Technology Stack</h2>
<ul>
  <li><strong>Framework:</strong> Flask (Python)</li>
  <li><strong>Database:</strong> Firestore Database</li>
  <li><strong>Storage:</strong> Firebase Storage</li>
  <li><strong>Model:</strong> ONNX Runtime</li>
  <li><strong>Deployment:</strong> Railway</li>
  <li><strong>Chatbot:</strong> OpenAI API</li>
</ul>

<hr>

<h2>📁 Project Structure</h2>

<pre>
GomMold_BackEnd/
├── Procfile
├── requirements.txt
├── runtime.txt
├── .gitignore
│
├── src/
│   ├── app.py
│   ├── firebase_init.py
│   ├── ml_model.py
│   ├── token_utils.py
│   │
│   ├── models/
│   │   └── best.onnx
│   │
│   └── routes/
│       ├── auth.py
│       ├── user.py
│       ├── mold.py
│       ├── history.py
│       └── chatbot.py
</pre>

<hr>

<h2>🔧 Installation</h2>

<ol>
  <li>Clone the repository:
    <pre>git clone https://github.com/GomMold/GomMold_BackEnd.git</pre>
  </li>

  <li>Create and activate a virtual environment:
    <pre>
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
    </pre>
  </li>

  <li>Install dependencies:
    <pre>pip install -r requirements.txt</pre>
  </li>

  <li>Run the server locally:
    <pre>python src/app.py</pre>
  </li>
</ol>

<hr>

<h2>🔐 Environment Variables</h2>
<p>These must be added in Railway:</p>

<ul>
  <li><code>SECRET_KEY</code> — JWT signing key</li>
  <li><code>FIREBASE_BUCKET</code> — Storage bucket name</li>
  <li><code>FIREBASE_CREDENTIALS_BASE64</code> — Base64 service account</li>
  <li><code>OPENAI_API_KEY</code> — Chatbot API key</li>
  <li><code>MODEL_URL</code> — Public ONNX model URL</li>
</ul>

<hr>

<h2>🧠 Mold Detection (ONNX)</h2>

<p>
The backend uses a pre-trained ONNX model for mold detection.  
If <code>best.onnx</code> is not found locally, it is automatically downloaded from the configured <code>MODEL_URL</code>:
</p>

<p>
<strong>MODEL_URL:</strong><br>
<a href="https://firebasestorage.googleapis.com/v0/b/gommold-c6654.firebasestorage.app/o/models%2Fbest.onnx?alt=media&token=75667b68-4ed6-480a-895e-e9502ad5a95a" target="_blank">
https://firebasestorage.googleapis.com/v0/b/gommold-c6654.firebasestorage.app/o/models%2Fbest.onnx?alt=media&token=75667b68-4ed6-480a-895e-e9502ad5a95a
</a>
</p>

<p>
After downloading, the model is used for inference, and detection results are saved to Firestore.
</p>

<p>
For full details on model training, dataset preparation, and ONNX export, refer to the ML repository:<br>
<a href="https://github.com/GomMold/GomMold_ML.git" target="_blank">
<strong>GomMold_ML (Machine Learning Repository)</strong>
</a>
</p>

<p><strong>Output example:</strong></p>

<pre>
{
  "success": true,
  "data": {
    "status": "warning",
    "message": "Mold detected",
    "image_url": "...",
    "predictions": [...],
    "timestamp": "2025-12-03 18:15"
  }
}
</pre>

<hr>

<h2>🔥 API Endpoints</h2>

<h3>Auth</h3>
<ul>
  <li>POST <code>/api/auth/signup</code></li>
  <li>POST <code>/api/auth/login</code></li>
</ul>

<h3>User</h3>
<ul>
  <li>GET <code>/api/user/profile</code></li>
  <li>PATCH <code>/api/user/update</code></li>
</ul>

<h3>Mold Detection</h3>
<ul>
  <li>POST <code>/api/mold/detect</code></li>
</ul>

<h3>History</h3>
<ul>
  <li>GET <code>/api/history/</code></li>
  <li>PUT <code>/api/history/&lt;id&gt;</code></li>
</ul>

<h3>Chatbot</h3>
<ul>
  <li>GET <code>/api/chatbot/start</code></li>
  <li>POST <code>/api/chatbot/query</code></li>
</ul>

<hr>

<h2>☁️ Deployment (Railway)</h2>

<p>Railway automatically builds and runs the app using Linux containers.</p>

<p><strong>Procfile (required):</strong></p>

<pre>
web: gunicorn src.app:app --bind 0.0.0.0:$PORT
</pre>

<p>Steps:</p>
<ol>
  <li>Push to GitHub</li>
  <li>Connect Railway → New Project → Deploy from GitHub</li>
  <li>Add environment variables</li>
  <li>Deploy</li>
</ol>

