import os
import uuid
from supabase import create_client, Client

class SupabaseStorageService:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("Error: Falta configurar SUPABASE_URL o SUPABASE_KEY en el .env")
        
        self.client: Client = create_client(url, key)
        self.bucket_name = "fotos"

    async def upload_file(self, file_bytes: bytes, original_filename: str, content_type: str, user_id: str) -> str:
        """
        Sube un archivo organizándolo en una subcarpeta única para cada usuario.
        """
        ext = original_filename.split(".")[-1] if "." in original_filename else "jpg"
        unique_name = f"{uuid.uuid4()}.{ext}"
        
        # Estructuramos la ruta usando el ID del usuario como carpeta
        file_path = f"{user_id}/{unique_name}"
        
        # Subida física a Supabase Storage
        self.client.storage.from_(self.bucket_name).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        
        # Retornamos la URL pública
        return self.client.storage.from_(self.bucket_name).get_public_url(file_path)