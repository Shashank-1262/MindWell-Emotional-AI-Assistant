class FusionEngine:
    @staticmethod
    def fuse(text_analysis, face_analysis):
        """
        Mixes text and face emotions.
        text_analysis: dict from TextEmotionAnalyzer.analyze_text
        face_analysis: dict from FaceEmotionDetector.detect_emotion
        
        Returns a fused emotional profile.
        """
        # Mapping FER emotions to Gemini emotions if necessary
        # Both seem to use standard categories: happy, sad, angry, surprised, neutral, fearful, disgusted
        
        text_weight = 0.6
        face_weight = 0.4

        if not face_analysis:
            # Fallback if no face detected
            return {
                "final_emotion": text_analysis["dominant_emotion"],
                "stress_level": text_analysis["stress_level"],
                "sentiment_score": text_analysis["sentiment_score"],
                "triggers": text_analysis["emotional_triggers"],
                "summary": text_analysis["summary"],
                "face_detected": False
            }

        # Normalize face emotions to match text analysis dominant emotion structure
        fused_emotions = {}
        for emotion in ["happy", "sad", "angry", "surprised", "neutral", "fearful", "disgusted"]:
            text_score = 1.0 if text_analysis["dominant_emotion"] == emotion else 0.0
            face_score = face_analysis.get(emotion, 0.0)
            fused_emotions[emotion] = (text_weight * text_score) + (face_weight * face_score)

        final_emotion = max(fused_emotions, key=fused_emotions.get)
        face_dominant = max(face_analysis, key=face_analysis.get) if face_analysis else None
        
        return {
            "final_emotion": final_emotion,
            "face_emotion": face_dominant,
            "stress_level": text_analysis["stress_level"],
            "sentiment_score": text_analysis["sentiment_score"],
            "triggers": text_analysis["emotional_triggers"],
            "summary": text_analysis["summary"],
            "face_detected": True,
            "emotion_distribution": fused_emotions
        }
