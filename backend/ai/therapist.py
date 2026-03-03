import google.generativeai as genai
from utils.config import Config

class TherapistAI:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def start_chat_session(self, current_log, history_summary=""):
        """Initializes a multi-turn chat session with context."""
        instruction = f"""
        You are a supportive psychological consultant (AI Therapist). 
        The user just logged their day: "{current_log['user_text']}"
        Detected Emotion: {current_log['final_emotion']}
        Stress Level: {current_log['stress_level']}

        Historical Context:
        {history_summary}

        Rules:
        - Be empathetic, warm, and professional.
        - If Stress Level is high (7 or above), PRIORITIZE immediate grounding or breathing exercises.
        - Use clean, easy-to-read formatting.
        - Use CBT-style suggestions.
        - Help the user explore their feelings further.
        - Stay in character as a supportive consultant.
        - Keep responses concise and focused on the user's well-being.
        """
        
        # Initialize chat with the system instruction-like prompt
        chat = self.model.start_chat(history=[])
        
        try:
            # Send initial context as the first message to get the therapist's opening
            response = chat.send_message(instruction)
            return chat, response.text
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                return None, "System: API Quota exceeded. The AI Therapist is resting. Please try again later or in 24 hours."
            return None, f"System: An unexpected error occurred: {str(e)}"
