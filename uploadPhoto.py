import os
import uuid
from supabase import create_client, Client

class SupabaseStorageService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Faltan las credenciales de Supabase en las variables de entorno.")
        self.client: Client = create_client(url, key)
        self.bucket_name = "fotos"

    async def upload_file(self, file_bytes: bytes, original_filename: str, content_type: str) -> str:
        """Sube los bytes de un archivo al bucket y retorna su URL pública."""
        ext = original_filename.split(".")[-1] if "." in original_filename else "jpg"
        unique_name = f"{uuid.uuid4()}.{ext}"
        
        # Subida al bucket
        self.client.storage.from_(self.bucket_name).upload(
            path=unique_name,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        
        # Retornar URL pública
        return self.client.storage.from_(self.bucket_name).get_public_url(unique_name)