from sqlalchemy.orm import Session
from app.models.promotion import Promotion, SavedPromotion
from datetime import datetime
from app.utils.response_helper import success_response, error_response
import logging

logger = logging.getLogger(__name__)

class PromotionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, promotion: Promotion):
        try:
            self.db.add(promotion)
            self.db.commit()
            self.db.refresh(promotion)
            return promotion
        except Exception as e:
            logger.error(f"Error creating promotion: {str(e)}")
            return error_response("Failed to create promotion", 500)

    def submit_for_approval(self, promotion: Promotion):
        try:
            promotion.status = "pending"
            promotion.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(promotion)
            return success_response("Promotion submitted for approval", data={"promotion_id": promotion.id})
        except Exception as e:
            logger.error(f"Error submitting promotion for approval: {str(e)}")
            return error_response("Failed to submit promotion", 500)

    def get_by_id(self, promo_id: int):
        try:
            return self.db.query(Promotion).filter(Promotion.id == promo_id).first()
        except Exception as e:
            logger.error(f"Error fetching promotion by ID {promo_id}: {str(e)}")
            return None

    def get_all(self, status=None):
        try:
            query = self.db.query(Promotion)
            if status:
                query = query.filter(Promotion.status == status)
            return query.all()
        except Exception as e:
            logger.error(f"Error fetching all promotions: {str(e)}")
            return []

    def delete(self, promotion: Promotion):
        try:
            self.db.delete(promotion)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting promotion ID {promotion.id}: {str(e)}")
            raise

    def update(self):
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during update commit: {str(e)}")
            raise

    def get_public_promotions(self):
        try:
            return self.db.query(Promotion).filter(Promotion.status.in_(["approved", "active"])).all()
        except Exception as e:
            logger.error(f"Error fetching public promotions: {str(e)}")
            return []

    def save_promotion_for_user(self, promotion_id: int, user_id: int):
        try:
            existing = self.db.query(SavedPromotion).filter_by(user_id=user_id, promotion_id=promotion_id).first()
            if existing:
                return error_response("Promotion already saved", 400)

            saved = SavedPromotion(user_id=user_id, promotion_id=promotion_id)
            self.db.add(saved)
            self.db.commit()
            return success_response("Promotion saved successfully")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving promotion for user {user_id}: {str(e)}")
            return error_response("Failed to save promotion", 500)

    def redeem_promotion_by_code(self, code: str):
        try:
            promo = self.db.query(Promotion).filter(
                Promotion.promo_code == code,
                Promotion.status == "active"
            ).first()
            if not promo:
                return error_response("Invalid or expired promo code", 404)
            return success_response("Promotion redeemed successfully", data=promo)
        except Exception as e:
            logger.error(f"Error redeeming promotion code {code}: {str(e)}")
            return error_response("Failed to redeem promotion", 500)
