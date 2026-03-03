import json
import os

class MetadataStore:
    def __init__(self, file_path="memory/metadata.json"):
        self.file_path = file_path
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return []

    def add_entry(self, entry):
        self.data.append(entry)
        self._save()

    def get_entries(self, indices):
        return [self.data[i] for i in indices if i < len(self.data) and i != -1]

    def get_all_entries(self):
        return self.data

    def _save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f, indent=4)
