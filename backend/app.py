"""
MindWell Web API - Flask REST API for the Emotional Wellness App
Provides endpoints for authentication, emotion logging, chat, insights, and RAG Q&A
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import os
import sys
from datetime import timedelta
import base64
import io

# Import existing backend modules
from utils.config import Config
from utils.user_manager import UserManager
from utils.timestamp import get_current_timestamp

# Try to import face detector - optional dependency
try:
    from emotion.face_detector import FaceEmotionDetector
    FACE_DETECTION_AVAILABLE = True
except Exception as e:
    print(f"Face detection unavailable: {e}")
    FaceEmotionDetector = None
    FACE_DETECTION_AVAILABLE = False

from emotion.text_emotion import TextEmotionAnalyzer
from emotion.fusion_engine import FusionEngine
from memory.embeddings import get_embeddings
from memory.faiss_manager import FAISSManager
from memory.metadata_store import MetadataStore
from rag.history_qa import HistoryQA
from analytics.emotional_insights import EmotionalInsights
from ai.therapist import TherapistAI

# Initialize Flask app
app = Flask(__name__, static_folder='frontend', static_url_path='')

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'mindwell-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Enable CORS for frontend
CORS(app)

# Initialize JWT
jwt = JWTManager(app)

# Validate config
try:
    Config.validate()
except ValueError as e:
    print(f"Warning: {e}")
    print("Some features may not work without GEMINI_API_KEY")

# Initialize global components
user_manager = UserManager()
face_detector = FaceEmotionDetector() if FACE_DETECTION_AVAILABLE else None
text_analyzer = TextEmotionAnalyzer()

# Dictionary to store active chat sessions per user
active_chats = {}

# Helper function to get user-specific components
def get_user_components(user_id):
    """Initialize user-specific FAISS, metadata store, and other components"""
    user_dir = user_manager.get_user_dir(user_id)
    faiss_path = os.path.join(user_dir, "faiss_index.bin")
    metadata_path = os.path.join(user_dir, "metadata.json")
    
    faiss_manager = FAISSManager(index_path=faiss_path)
    metadata_store = MetadataStore(file_path=metadata_path)
    rag_qa = HistoryQA(faiss_manager=faiss_manager, metadata_store=metadata_store)
    insights_engine = EmotionalInsights(metadata_store=metadata_store)
    
    return {
        'faiss_manager': faiss_manager,
        'metadata_store': metadata_store,
        'rag_qa': rag_qa,
        'insights_engine': insights_engine
    }

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        success, result = user_manager.create_user(username, password)
        
        if success:
            user_id = result
            access_token = create_access_token(identity=user_id)
            return jsonify({
                'success': True,
                'message': f'Account created successfully! Welcome, {username}.',
                'user_id': user_id,
                'token': access_token
            }), 201
        else:
            return jsonify({'error': result}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    """Login existing user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        success, result = user_manager.login(username, password)
        
        if success:
            user_id = result
            access_token = create_access_token(identity=user_id)
            return jsonify({
                'success': True,
                'message': f'Welcome back, {username}!',
                'user_id': user_id,
                'token': access_token
            }), 200
        else:
            return jsonify({'error': result}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== LOG MY DAY ENDPOINT ====================

@app.route('/log', methods=['POST'])
@jwt_required()
def log_day():
    """
    Log a new day entry with text emotion analysis and optional face detection
    Returns fused emotion data + therapist opening message
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_text = data.get('text', '').strip()
        
        if not user_text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Get user-specific components
        components = get_user_components(user_id)
        
        # Analyze text emotion
        text_analysis = text_analyzer.analyze_text(user_text)
        
        # Face emotion analysis (optional, can be None if no image provided)
        face_analysis = None
        if 'face_image' in data and data['face_image'] and face_detector:
            # If frontend sends base64 image data
            try:
                face_analysis = face_detector.detect_emotion_from_base64(data['face_image'])
                if face_analysis:
                    print(f"Face emotion detected: {face_analysis}")
            except Exception as e:
                print(f"Face detection error: {e}")
        
        # Fuse emotions
        fused_log = FusionEngine.fuse(text_analysis, face_analysis)
        fused_log['user_text'] = user_text
        fused_log['timestamp'] = get_current_timestamp()
        
        # Save to user-specific memory
        vector = get_embeddings(user_text)
        components['faiss_manager'].add_vector(vector)
        components['metadata_store'].add_entry(fused_log)
        
        # Start therapist chat session
        therapist = TherapistAI()
        history_summary = components['insights_engine'].get_insights()
        chat_session, initial_response = therapist.start_chat_session(fused_log, history_summary)
        
        # Store chat session for this user
        if chat_session:
            active_chats[user_id] = chat_session
        
        return jsonify({
            'success': True,
            'log': {
                'emotion': fused_log['final_emotion'],
                'stress_level': fused_log['stress_level'],
                'sentiment_score': fused_log['sentiment_score'],
                'triggers': fused_log['triggers'],
                'summary': fused_log['summary'],
                'face_detected': fused_log.get('face_detected', False),
                'face_emotion': fused_log.get('face_emotion'),
                'timestamp': fused_log['timestamp']
            },
            'therapist_message': initial_response
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CHAT ENDPOINT ====================

@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    """Continue multi-turn conversation with therapist"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get active chat session
        if user_id not in active_chats:
            return jsonify({'error': 'No active chat session. Please log your day first.'}), 400
        
        chat_session = active_chats[user_id]
        
        # Send message and get response
        response = chat_session.send_message(user_message)
        
        return jsonify({
            'success': True,
            'response': response.text
        }), 200
        
    except Exception as e:
        # Handle API quota errors gracefully
        if "429" in str(e) or "ResourceExhausted" in str(e):
            return jsonify({
                'error': 'API quota exceeded. Please try again later.'
            }), 429
        return jsonify({'error': str(e)}), 500

# ==================== INSIGHTS ENDPOINT ====================

@app.route('/insights', methods=['GET'])
@jwt_required()
def get_insights():
    """Get emotional insights and analytics for the current user"""
    try:
        user_id = get_jwt_identity()
        components = get_user_components(user_id)
        
        insights_text = components['insights_engine'].get_insights()
        
        # Parse insights into structured data for frontend
        entries = components['metadata_store'].get_all_entries()
        
        if not entries:
            return jsonify({
                'total_logs': 0,
                'avg_stress': 0,
                'dominant_emotion': 'neutral',
                'trend': 'No data yet',
                'insights_text': insights_text
            }), 200
        
        recent_entries = entries[-7:]
        stress_levels = [e['stress_level'] for e in recent_entries]
        emotions = [e['final_emotion'] for e in entries]
        
        avg_stress = sum(stress_levels) / len(stress_levels)
        dominant_emotion = max(set(emotions), key=emotions.count)
        trend = "improving" if len(stress_levels) > 1 and stress_levels[-1] < stress_levels[0] else "stable"
        
        # Get common trigger
        all_triggers = []
        for e in entries:
            all_triggers.extend(e.get('triggers', []))
        common_trigger = max(set(all_triggers), key=all_triggers.count) if all_triggers else "None identified"
        
        return jsonify({
            'total_logs': len(entries),
            'avg_stress': round(avg_stress, 1),
            'dominant_emotion': dominant_emotion,
            'trend': trend,
            'common_trigger': common_trigger,
            'insights_text': insights_text,
            'recent_logs': recent_entries[-5:]  # Last 5 logs for display
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== RAG Q&A ENDPOINT ====================

@app.route('/history-qa', methods=['POST'])
@jwt_required()
def history_qa():
    """Ask questions about emotional history using RAG"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        components = get_user_components(user_id)
        answer = components['rag_qa'].answer_question(question)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== OPTIONAL: FACE DETECTION ENDPOINT ====================

@app.route('/detect-face', methods=['POST'])
@jwt_required()
def detect_face():
    """
    Optional endpoint for face emotion detection from uploaded image
    Expects base64 encoded image in request
    """
    try:
        # This is a placeholder for future implementation
        # Would require adapting face_detector to work with image data instead of webcam
        return jsonify({
            'message': 'Face detection from image not yet implemented in web version',
            'face_detected': False
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== DASHBOARD DATA ENDPOINT ====================

@app.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Get dashboard summary data"""
    try:
        user_id = get_jwt_identity()
        components = get_user_components(user_id)
        
        entries = components['metadata_store'].get_all_entries()
        
        if not entries:
            return jsonify({
                'hasData': False,
                'message': 'No logs yet. Start by logging your day!'
            }), 200
        
        # Get latest entry
        latest = entries[-1]
        
        # Calculate recent stats
        recent_entries = entries[-7:]
        stress_levels = [e['stress_level'] for e in recent_entries]
        avg_stress = sum(stress_levels) / len(stress_levels)
        
        return jsonify({
            'hasData': True,
            'latest_emotion': latest['final_emotion'],
            'latest_stress': latest['stress_level'],
            'latest_timestamp': latest['timestamp'],
            'avg_recent_stress': round(avg_stress, 1),
            'total_logs': len(entries)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SERVE FRONTEND ====================

@app.route('/')
def serve_frontend():
    """Serve the main frontend HTML"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static frontend files"""
    return send_from_directory('frontend', path)

# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MindWell Emotional Wellness API',
        'version': '1.0.0'
    }), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("   MINDWELL EMOTIONAL WELLNESS WEB APP")
    print("="*60)
    print("\n🌟 Starting Flask server...")
    print("📱 Frontend: http://localhost:5000")
    print("🔌 API Base: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  POST /auth/login")
    print("  POST /auth/register")
    print("  POST /log")
    print("  POST /chat")
    print("  GET  /insights")
    print("  POST /history-qa")
    print("  GET  /dashboard")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
