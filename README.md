# MindWell - Emotional Wellness Web App

A modern web-based emotional wellness companion with facial emotion detection using AI to analyze emotions, provide therapy-style support, and track emotional patterns over time.

## 🌟 Features

- **Emotion Analysis**: Analyze text input using Google Gemini AI to detect emotions and stress levels
- **AI Therapist**: Multi-turn conversational AI therapist powered by Gemini
- **Emotional Insights**: Track patterns, trends, and triggers in your emotional journey
- **RAG Q&A**: Ask questions about your emotional history using RAG (Retrieval Augmented Generation)
- **User Authentication**: Secure multi-user support with JWT tokens
- **Beautiful UI**: Calming color palette with responsive design

## 📁 Project Structure

```
LAST AP/
├── app.py                          # Flask REST API server
├── main.py                         # Original CLI entry point
├── menu.py                         # CLI menu (legacy)
├── requirements.txt                # Python dependencies
├── frontend/                       # Web frontend files
│   ├── index.html                  # Main HTML structure
│   ├── style.css                   # Styling (calming blues & purples)
│   └── app.js                      # Frontend JavaScript logic
├── ai/
│   └── therapist.py               # Gemini-powered therapist
├── analytics/
│   └── emotional_insights.py      # Stress trend analytics
├── emotion/
│   ├── face_detector.py           # Webcam emotion detection (FER)
│   ├── fusion_engine.py           # Text + face emotion fusion
│   └── text_emotion.py            # Gemini text emotion analysis
├── memory/
│   ├── embeddings.py              # Sentence transformer embeddings
│   ├── faiss_manager.py           # FAISS vector store
│   └── metadata_store.py          # JSON metadata storage
├── rag/
│   └── history_qa.py              # RAG pipeline for Q&A
└── utils/
    ├── config.py                  # Environment config
    ├── timestamp.py               # Timestamp utilities
    └── user_manager.py            # User authentication

```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Navigate to the project directory**
   ```bash
   cd "LAST AP\LAST AP"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   JWT_SECRET_KEY=your_secret_key_here
   ```

### Running the Web App

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   
   Navigate to: `http://localhost:5000`

3. **Create an account or login**
   
   - Click "Register" to create a new account
   - Enter username and password
   - Start logging your emotions!

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login existing user

### Core Features
- `POST /log` - Log your day (text emotion analysis + therapist session start)
- `POST /chat` - Continue conversation with AI therapist
- `GET /insights` - Get emotional insights and analytics
- `POST /history-qa` - Ask questions about your history (RAG)
- `GET /dashboard` - Get dashboard summary data

### Utility
- `GET /health` - Health check endpoint

## 🎨 Frontend Views

1. **Dashboard** - Overview of your emotional state
   - Current emotion
   - Stress level
   - Recent trends
   - Total logs

2. **Log My Day** - Main logging interface
   - Text input for describing your day
   - Emotion analysis results
   - Interactive chat with AI therapist

3. **Ask My History** - RAG-powered Q&A
   - Ask questions about past entries
   - Get insights from your history

4. **Insights** - Analytics dashboard
   - Stress trends
   - Dominant emotions
   - Common triggers
   - Recent log history

## 🔐 Security

- Passwords are hashed using SHA256
- JWT tokens for session management
- 24-hour token expiration
- Per-user data isolation

## 💾 Data Storage

Each user has their own isolated storage:
- `users/{user_id}/faiss_index.bin` - Vector embeddings
- `users/{user_id}/metadata.json` - Emotional log metadata

## 🎯 Technology Stack

**Backend:**
- Flask - REST API framework
- Flask-CORS - Cross-origin resource sharing
- Flask-JWT-Extended - JWT authentication
- Google Gemini AI - Text analysis and chat
- FAISS - Vector similarity search
- Sentence Transformers - Text embeddings

**Frontend:**
- Vanilla JavaScript - No framework required
- Modern CSS with CSS Grid and Flexbox
- Responsive design for mobile and desktop

**AI/ML:**
- Google Gemini 2.5 Flash - Text emotion analysis and chat
- FER (Facial Expression Recognition) - Optional face detection
- Sentence-BERT (MiniLM) - Text embeddings for RAG

## 🐛 Troubleshooting

### API Quota Exceeded
If you see "API Quota exceeded" errors, you've hit your Gemini API limit. The app will:
- Use fallback neutral emotion values
- Display a friendly message
- Continue functioning for basic features

### Webcam Not Working
The web version doesn't require webcam access. Face detection is optional and gracefully skipped.

### Port Already in Use
If port 5000 is busy, edit [app.py](app.py#L391) and change the port number:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

## 📝 Usage Tips

1. **Be descriptive** - The more detail you provide, the better the emotion analysis
2. **Regular logging** - Log daily for better trend insights
3. **Ask specific questions** - In History Q&A, be specific for better RAG results
4. **Engage with the therapist** - Have a real conversation for better support

## 🔄 Migrating from CLI to Web

The original CLI app ([main.py](main.py)) still works! You can use both:
- Run `python main.py` for CLI experience
- Run `python app.py` for web experience

Both use the same backend modules and data storage.

## 🤝 Contributing

This is a personal wellness app, but feel free to:
- Report bugs
- Suggest features
- Improve documentation

## 📄 License

Personal use only. Not licensed for commercial distribution.

## 🙏 Acknowledgments

- Google Gemini AI for emotion analysis and therapy
- FER library for facial emotion recognition
- FAISS for efficient similarity search
- Sentence Transformers for embeddings

## 📧 Support

For issues or questions, check the troubleshooting section or review the API endpoint documentation.

---

**Made with ✨ for emotional wellness and mental health support**
