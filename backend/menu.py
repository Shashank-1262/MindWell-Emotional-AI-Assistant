class Menu:
    @staticmethod
    def display_header():
        print("\n" + "="*40)
        print("   🧠 AI EMOTIONAL WELLNESS ASSISTANT   ")
        print("="*40)

    @staticmethod
    def get_main_choice():
        print("\nMenu:")
        print("1. Log My Day (Multimodal)")
        print("2. Ask About My History (RAG)")
        print("3. Emotional Insights (Analytics)")
        print("4. Exit")
        choice = input("\nSelect an option (1-4): ")
        return choice

    @staticmethod
    def clear_screen():
        # print("\033c", end="") # Clear terminal
        pass
