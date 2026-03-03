# 🚀 Quick Start Guide - MindWell Web App

## ⚡ Fast Setup (3 Steps)

### 1. Install Dependencies
Double-click `install_dependencies.bat` or run:
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Make sure your `.env` file has your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Start the Server
Double-click `start_web.bat` or run:
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

---

## 🎯 First Time Usage

1. **Register** - Create a new account with username and password
2. **Log Your Day** - Navigate to "Log My Day" and describe your day
3. **Chat with AI** - After logging, chat with the AI therapist
4. **View Insights** - Check the Insights page for your emotional trends

---

## 📊 What Changed from CLI to Web?

### ✅ What's New
- **Modern Web UI** - Beautiful, responsive interface
- **Easy Navigation** - Switch between views with a click
- **Real-time Chat** - Smooth therapist conversation interface
- **Visual Analytics** - See your emotions and stress in styled cards
- **Multi-user Support** - Each user gets isolated data storage

### ✅ What Stayed the Same
- All backend logic (emotion analysis, FAISS, embeddings, RAG)
- User authentication system
- Per-user data storage
- Gemini AI integration

### 📝 What's Different
- **Face Detection**: Optional in web version (not required)
- **Authentication**: Now uses JWT tokens instead of simple login
- **Access**: Browser-based instead of terminal

---

## 🌐 Web App Architecture

```
Browser (Frontend)
     ↓ HTTP/REST
Flask API (app.py)
     ↓
Backend Modules
  ├── emotion/ (Analysis)
  ├── ai/ (Therapist)
  ├── memory/ (FAISS + Storage)
  ├── rag/ (Q&A)
  └── analytics/ (Insights)
```

---

## 🎨 Frontend Features

### Navigation Bar
- **Dashboard** - Overview of your current emotional state
- **Log My Day** - Main logging and chat interface
- **Ask My History** - RAG-powered Q&A about past entries
- **Insights** - Analytics and trends visualization

### Color-Coded Stress Levels
- 🟢 **Green (1-3)**: Low stress
- 🟡 **Yellow (4-6)**: Moderate stress
- 🔴 **Red (7-10)**: High stress

---

## 🔧 Troubleshooting

### "Module not found" errors
**Solution**: Run `install_dependencies.bat` or:
```bash
pip install -r requirements.txt
```

### "API Quota exceeded"
**Solution**: You've reached your Gemini API daily limit. Wait 24 hours or upgrade your API plan.

### Port 5000 already in use
**Solution**: Edit `app.py` line 391 and change port to 5001:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Can't access from another device
**Solution**: The server is already configured to accept connections from any device on your network. Access via:
```
http://YOUR_COMPUTER_IP:5000
```

---

## 💡 Pro Tips

1. **Detailed Descriptions**: Write longer, more descriptive logs for better emotion analysis
2. **Daily Logging**: Log consistently for more accurate trend analysis
3. **Explore History**: Use the Q&A feature to discover patterns in your emotions
4. **Engage in Chat**: Have meaningful conversations with the AI therapist

---

## 🆚 CLI vs Web Comparison

| Feature | CLI (main.py) | Web (app.py) |
|---------|---------------|--------------|
| Interface | Terminal | Browser |
| Face Detection | Required webcam | Optional |
| Multi-device | Local only | Any browser |
| Chat | Text-based | Visual bubbles |
| Analytics | Text report | Visual cards |
| Best for | Power users | General users |

**Both work!** You can use either version - they share the same data.

---

## 📱 Mobile Access

The web app is responsive and works on mobile devices:
1. Find your computer's IP address
2. Access from phone: `http://YOUR_IP:5000`
3. Make sure phone is on same WiFi network

---

## 🔐 Security Notes

- Passwords are SHA256 hashed
- JWT tokens expire after 24 hours
- Each user has isolated storage
- Tokens stored in browser localStorage

---

## 🎉 You're Ready!

Double-click `start_web.bat` and start your emotional wellness journey!

For more details, see `README_WEB.md`
