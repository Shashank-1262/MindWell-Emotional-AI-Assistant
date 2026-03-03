import google.generativeai as genai
from memory.faiss_manager import FAISSManager
from memory.metadata_store import MetadataStore
from memory.embeddings import get_embeddings
from utils.config import Config

class HistoryQA:
    def __init__(self, faiss_manager=None, metadata_store=None):
        self.faiss_manager = faiss_manager or FAISSManager()
        self.metadata_store = metadata_store or MetadataStore()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def answer_question(self, question):
        """RAG pipeline to answer questions about history."""
        # 1. Embed query
        query_vector = get_embeddings(question)

        # 2. Retrieve memories (Increased k to 10 for better coverage)
        indices, distances = self.faiss_manager.search(query_vector, k=10)
        relevant_memories = self.metadata_store.get_entries(indices)

        if not relevant_memories:
            return "I don't have enough history to answer that yet. Try logging more days!"

        # 3. Format context
        context = "\n---\n".join([
            f"Date: {m.get('timestamp', 'Unknown')}\nText: {m.get('user_text', 'No text')}\nEmotion: {m.get('final_emotion', 'neutral')}\nStress: {m.get('stress_level', 'N/A')}"
            for m in relevant_memories
        ])

        # 4. Generate answer
        prompt = f"""
        You are an AI Emotional Assistant with access to the user's past emotional logs.
        Your goal is to answer questions about the user's history accurately, supportively, and comprehensively.

        HISTORICAL LOGS (Context):
        {context}

        USER QUESTION: "{question}"
        
        INSTRUCTIONS:
        1. Answer the question based on the provided logs.
        2. If the user asks for "all" or "all my inputs", summarize the key themes and list specific examples from the logs above.
        3. Be empathetic and supportive.
        4. If the logs don't contain the answer, politely let the user know.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                return "The AI History analyst is currently at capacity. Please try asking again in a few minutes."
            return f"I'm sorry, I encountered an error while retrieving your history: {str(e)}"
