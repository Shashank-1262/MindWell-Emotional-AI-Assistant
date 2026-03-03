import sys
import os
from utils.config import Config
from utils.timestamp import get_current_timestamp
from emotion.face_detector import FaceEmotionDetector
from emotion.text_emotion import TextEmotionAnalyzer
from emotion.fusion_engine import FusionEngine
from memory.embeddings import get_embeddings
from memory.faiss_manager import FAISSManager
from memory.metadata_store import MetadataStore
from rag.history_qa import HistoryQA
from analytics.emotional_insights import EmotionalInsights
from ai.therapist import TherapistAI
from menu import Menu

from utils.user_manager import UserManager

def auth_screen(user_manager):
    while True:
        print("\n" + "="*40)
        print("   WELCOME TO MINDWELL AUTHENTICATION")
        print("="*40)
        print("1. Login")
        print("2. Create New Account")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ")
        
        if choice == '1':
            username = input("Username: ")
            password = input("Password: ")
            success, result = user_manager.login(username, password)
            if success:
                print(f"\nWelcome back, {username}!")
                return result
            print(f"\nError: {result}")
            
        elif choice == '2':
            username = input("Choose a Username: ")
            password = input("Choose a Password: ")
            success, result = user_manager.create_user(username, password)
            if success:
                print(f"\nAccount created successfully! Welcome, {username}.")
                return result
            print(f"\nError: {result}")
            
        elif choice == '3':
            sys.exit()

def main():
    # 0. Initial Setup & Validation
    try:
        Config.validate()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please check your .env file.")
        return

    user_manager = UserManager()
    user_id = auth_screen(user_manager)
    
    # Path for user specific data
    user_dir = user_manager.get_user_dir(user_id)
    faiss_path = os.path.join(user_dir, "faiss_index.bin")
    metadata_path = os.path.join(user_dir, "metadata.json")

    # Initialize components
    face_detector = FaceEmotionDetector()
    text_analyzer = TextEmotionAnalyzer()
    
    # User-specific components
    faiss_manager = FAISSManager(index_path=faiss_path)
    metadata_store = MetadataStore(file_path=metadata_path)
    rag_qa = HistoryQA(faiss_manager=faiss_manager, metadata_store=metadata_store)
    insights_engine = EmotionalInsights(metadata_store=metadata_store)
    therapist = TherapistAI()

    while True:
        Menu.display_header()
        print(f"   Mode: Multi-User | Active: {user_id}")
        choice = Menu.get_main_choice()

        if choice == '1':
            # --- FEATURE 1: Log My Day ---
            user_text = input("\nHow was your day? Describe freely: ")
            if not user_text.strip():
                print("Log cancelled: Empty text.")
                continue

            face_analysis = face_detector.detect_emotion(capture_duration=3)
            text_analysis = text_analyzer.analyze_text(user_text)
            fused_log = FusionEngine.fuse(text_analysis, face_analysis)
            fused_log['user_text'] = user_text
            fused_log['timestamp'] = get_current_timestamp()

            # Save to user-specific memory
            vector = get_embeddings(user_text)
            faiss_manager.add_vector(vector)
            metadata_store.add_entry(fused_log)

            print("\n--- Logged Successfully ---")
            print(f"Detected Emotion: {fused_log['final_emotion']} (Stress: {fused_log['stress_level']}/10)")
            if fused_log.get('face_detected') and fused_log.get('face_emotion'):
                print(f"Facial Expression: {fused_log['face_emotion']}")
            
            print("\n" + "✨" + "-"*50 + "✨")
            print("   AI THERAPIST SUPPORTIVE SESSION   ")
            print("-"*52)
            history_summary = insights_engine.get_insights()
            chat_session, initial_response = therapist.start_chat_session(fused_log, history_summary)
            print(f"\nAI: {initial_response}")
            
            if chat_session is None:
                print("✨" + "-"*50 + "✨")
                continue

            while True:
                user_msg = input("\nYou (type 'exit' to return to menu): ").strip()
                if user_msg.lower() in ['exit', 'quit', 'bye']:
                    break
                if not user_msg: continue
                response = chat_session.send_message(user_msg)
                print(f"\nAI: {response.text}")
            print("✨" + "-"*50 + "✨")

        elif choice == '2':
            question = input("\nAsk about your history: ")
            if not question.strip(): continue
            answer = rag_qa.answer_question(question)
            print("\nAnswer:", answer)

        elif choice == '3':
            print("\nGenerating Insights...")
            insights = insights_engine.get_insights()
            print("\n" + insights)

        elif choice == '4':
            print(f"\nGoodbye, {user_id}. Take care!")
            import time
            time.sleep(2)
            sys.exit()

if __name__ == "__main__":
    main()
