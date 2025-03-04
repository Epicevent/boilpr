import uuid

class FileManager:
    def __init__(self):
        self.uploaded_files = []

    def upload_files(self, uploaded_files):
        """Handle file uploads."""
        new_files = []
        for file in uploaded_files:
            # Prevent duplicates
            if not any(doc["name"] == file.name for doc in self.uploaded_files):
                file_info = {
                    "id": str(uuid.uuid4()),
                    "name": file.name,
                    "size": len(file.getvalue()),
                    "type": file.type,
                    "data": file.getvalue(),
                }
                self.uploaded_files.append(file_info)
                new_files.append(file_info)
        return new_files

    def delete_files(self, file_names):
        """Delete files by names."""
        self.uploaded_files = [doc for doc in self.uploaded_files if doc["name"] not in file_names]

    def search_files(self, query):
        """Search files by query."""
        return [doc for doc in self.uploaded_files if query.lower() in doc["name"].lower()]

    def get_files(self):
        """Retrieve all uploaded files."""
        return self.uploaded_files
