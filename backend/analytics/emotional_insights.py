from memory.metadata_store import MetadataStore

class EmotionalInsights:
    def __init__(self, metadata_store=None):
        self.metadata_store = metadata_store or MetadataStore()

    def get_insights(self):
        entries = self.metadata_store.get_all_entries()
        if not entries:
            return "No logs found to generate insights."

        # Compute simple stats
        recent_entries = entries[-7:] # Last 7 logs
        stress_levels = [e['stress_level'] for e in recent_entries]
        emotions = [e['final_emotion'] for e in entries]

        avg_stress = sum(stress_levels) / len(stress_levels)
        dominant_emotion = max(set(emotions), key=emotions.count)
        
        trend = "improving" if len(stress_levels) > 1 and stress_levels[-1] < stress_levels[0] else "stable/fluctuating"
        
        insight_text = f"Analyzed {len(entries)} historical logs.\n"
        insight_text += f"Average stress (recent): {avg_stress:.1f}/10\n"
        insight_text += f"Most frequent emotion: {dominant_emotion}\n"
        insight_text += f"Stress trend: {trend}\n"
        
        # Identify triggers
        all_triggers = []
        for e in entries:
            all_triggers.extend(e.get('triggers', []))
        
        if all_triggers:
            common_trigger = max(set(all_triggers), key=all_triggers.count)
            insight_text += f"Common stress trigger: {common_trigger}\n"

        return insight_text
