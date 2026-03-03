import google.generativeai as genai
import json
from utils.config import Config

class TextEmotionAnalyzer:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_text(self, text):
        """Uses Gemini Flash to analyze text emotion and stress level."""
        prompt = f"""
        Analyze the following text for emotional content. 
        Provide a structured JSON response with exactly these keys:
        - dominant_emotion (string: happy, sad, angry, surprised, neutral, fearful, disgusted)
        - stress_level (int: 0 to 10)
        - sentiment_score (float: -1.0 to 1.0)
        - emotional_triggers (list of strings)
        - summary (string: brief summary of the emotional state)

        Text: "{text}"
        """

        try:
            response = self.model.generate_content(prompt)
            # Clean response text in case of markdown formatting
            content = response.text.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
            
            return json.loads(content)
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print("\n[Notice] API Quota exceeded. Using basic emotional analysis for now.")
            else:
                print(f"\n[Notice] Emotional analysis unavailable: {e}")
            
            return {
                "dominant_emotion": "neutral",
                "stress_level": 5,
                "sentiment_score": 0.0,
                "emotional_triggers": [],
                "summary": "AI Analysis is currently offline. Log saved with default values."
            }

if __name__ == "__main__":
    # Test (requires API key)
    analyzer = TextEmotionAnalyzer()
    print(analyzer.analyze_text("I had a very stressful day at work today."))
