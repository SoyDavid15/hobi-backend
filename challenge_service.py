from datetime import datetime, timezone
from sqlalchemy.orm import Session
import models
from models import UserProgress, Foto

class ChallengeService:
    @staticmethod
    def process_challenge_completion(db: Session, user_id: str, filename: str, file_size: int, url_publica: str):
        """
        Registra la foto en la base de datos y actualiza la gamificación del usuario
        en una sola transacción atómica.
        """
        # 1. Guardar metadatos de la foto
        new_photo = Foto(
            nombre=filename,
            ruta=url_publica,
            fecha=datetime.now(timezone.utc),
            tamanio=file_size
        )
        db.add(new_photo)
        
        # 2. Gestionar progreso y rachas
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        today = datetime.now(timezone.utc)
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                completed_challenges=1,
                streak=1,
                last_completed_date=today
            )
            db.add(progress)
        else:
            if progress.last_completed_date:
                last_date = progress.last_completed_date.date()
                today_date = today.date()
                diff_days = (today_date - last_date).days
                
                if diff_days == 1:
                    progress.streak += 1
                elif diff_days > 1:
                    progress.streak = 1
                elif diff_days == 0 and progress.streak == 0:
                    progress.streak = 1
            else:
                progress.streak = 1
                
            progress.completed_challenges += 1
            progress.last_completed_date = today
            
        db.commit()
        db.refresh(progress)
        return progress