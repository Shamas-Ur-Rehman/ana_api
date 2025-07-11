from sqlalchemy.orm import Session
from app.models.promotion import Promotion
from app.schemas.promotion import PromotionCreate, PromotionUpdate, PromotionApproval
from fastapi import status
from app.models.user import User
from app.repo.promotion_repo import PromotionRepository
from datetime import datetime
from app.utils.response_helper import success_response, error_response
import logging

logger = logging.getLogger(__name__)


class PromotionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PromotionRepository(db)

    def create_promotion(self, data: PromotionCreate, user_id: int):
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return error_response("User not found", 404)
            if not user.role or user.role.name.lower() != "vendor":
                return error_response("Only vendors are allowed to create promotions.", 403)

            promo = Promotion(
                **data.dict(),
                created_by=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                status="draft"
            )
            self.repo.create(promo)
            return success_response("Promotion created successfully", data={"id": promo.id})
        except Exception as e:
            logger.error(f"Error creating promotion: {str(e)}")
            return error_response("Failed to create promotion", 500)

    def submit_for_approval(self, promotion_id: int, user_id: int):
        try:
            promotion = self.repo.get_by_id(promotion_id)
            if not promotion:
                return error_response("Promotion not found", 404)
            if promotion.created_by != user_id:
                return error_response("You are not allowed to submit this promotion", 403)
            if promotion.status != "draft":
                return error_response("Only draft promotions can be submitted for approval", 400)

            self.repo.submit_for_approval(promotion)
            return success_response("Promotion submitted for approval")
        except Exception as e:
            logger.error(f"Error submitting promotion for approval: {str(e)}")
            return error_response("Failed to submit promotion for approval", 500)

    def update_promotion(self, promo_id: int, data: PromotionUpdate, user_id: int):
        try:
            promo = self.repo.get_by_id(promo_id)
            if not promo:
                return error_response("Promotion not found", 404)
            if promo.created_by != user_id:
                return error_response("Not allowed to update this promotion", 403)
            if promo.status in ["approved", "active"]:
                return error_response("Approved or active promotions cannot be edited", 400)

            for key, value in data.dict(exclude_unset=True).items():
                setattr(promo, key, value)

            promo.updated_by = user_id
            promo.updated_at = datetime.utcnow()
            self.repo.update()
            return success_response("Promotion updated successfully")
        except Exception as e:
            logger.error(f"Error updating promotion: {str(e)}")
            return error_response("Failed to update promotion", 500)

    def delete_promotion(self, promo_id: int, user_id: int):
        try:
            promo = self.repo.get_by_id(promo_id)
            if not promo:
                return error_response("Promotion not found", 404)
            if promo.created_by != user_id:
                return error_response("Not allowed to delete this promotion", 403)

            self.repo.delete(promo)
            return success_response("Promotion deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting promotion: {str(e)}")
            return error_response("Failed to delete promotion", 500)

    def get_promotion(self, promo_id: int):
        try:
            promo = self.repo.get_by_id(promo_id)
            if not promo:
                return error_response("Promotion not found", 404)
            return success_response("Promotion fetched successfully", data=promo)
        except Exception as e:
            logger.error(f"Error fetching promotion: {str(e)}")
            return error_response("Failed to fetch promotion", 500)

    def get_all_promotions(self, status=None):
        try:
            promotions = self.repo.get_all(status)
            data = [
                {
                    "id": p.id,
                    "title": p.title,
                    "status": p.status,
                    "description": p.description,
                    "start_date": p.start_date.isoformat() if p.start_date else None,
                    "end_date": p.end_date.isoformat() if p.end_date else None,
                    "discount": p.discount,
                    "image_url": p.image_url,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                    "created_by": p.created_by,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in promotions
            ]
            return success_response("Promotions fetched successfully", data=data)
        except Exception as e:
            logger.error(f"Error fetching promotions: {str(e)}")
            return error_response("Failed to fetch promotions", 500)

    def toggle_promotion_status(self, promo_id: int, user_id: int):
        try:
            promo = self.repo.get_by_id(promo_id)
            if not promo:
                return error_response("Promotion not found", 404)
            if promo.created_by != user_id:
                return error_response("Not allowed to change status of this promotion", 403)
            if promo.status not in ["approved", "active", "inactive"]:
                return error_response("Only approved promotions can be activated or deactivated", 400)

            promo.status = "inactive" if promo.status == "active" else "active"
            promo.updated_by = user_id
            promo.updated_at = datetime.utcnow()
            self.repo.update()
            return success_response(
                message=f"Promotion {'deactivated' if promo.status == 'inactive' else 'activated'}",
                data={"status": promo.status}
            )
        except Exception as e:
            logger.error(f"Error toggling promotion status: {str(e)}")
            return error_response("Failed to toggle promotion status", 500)

    def approve_promotion(self, promo_id: int, data: PromotionApproval, user_id: int):
        try:
            promo = self.repo.get_by_id(promo_id)
            user = self.db.query(User).filter(User.id == user_id).first()

            if not promo:
                return error_response("Promotion not found", 404)
            if not user or not user.role or user.role.name.lower() != "admin":
                return error_response("Only admins can approve promotions", 403)
            if promo.status != "pending":
                return error_response("Only pending promotions can be approved", 400)

            promo.status = "approved"
            promo.approval_comments = data.comments
            promo.updated_at = datetime.utcnow()
            promo.updated_by = user_id
            self.repo.update()
            return success_response(
                message="Promotion approved successfully",
                data={"promotion_id": promo.id, "status": promo.status}
            )
        except Exception as e:
            logger.error(f"Error approving promotion: {str(e)}")
            return error_response("Failed to approve promotion", 500)

    def reject_promotion(self, promo_id: int, data: PromotionApproval, user_id: int):
        try:
            promo = self.repo.get_by_id(promo_id)
            user = self.db.query(User).filter(User.id == user_id).first()

            if not promo:
                return error_response("Promotion not found", 404)
            if not user or not user.role or user.role.name.lower() != "admin":
                return error_response("Only admins can reject promotions", 403)
            if promo.status != "pending":
                return error_response("Only pending promotions can be rejected", 400)

            promo.status = "rejected"
            promo.approval_comments = data.comments
            promo.updated_at = datetime.utcnow()
            promo.updated_by = user_id
            self.repo.update()
            return success_response(
                message="Promotion rejected successfully",
                data={"promotion_id": promo.id, "status": promo.status}
            )
        except Exception as e:
            logger.error(f"Error rejecting promotion: {str(e)}")
            return error_response("Failed to reject promotion", 500)

    def get_public_promotions(self):
        try:
            promotions = self.repo.get_public_promotions()
            return success_response("Public promotions fetched successfully", data=promotions)
        except Exception as e:
            logger.error(f"Error fetching public promotions: {str(e)}")
            return error_response("Failed to fetch public promotions", 500)

    def save_promotion(self, promotion_id: int, user_id: int):
        try:
            result = self.repo.save_promotion_for_user(promotion_id, user_id)
            return success_response("Promotion saved successfully", data=result)
        except Exception as e:
            logger.error(f"Error saving promotion: {str(e)}")
            return error_response("Failed to save promotion", 500)

    def redeem_promotion(self, code: str):
        try:
            result = self.repo.redeem_promotion_by_code(code)
            return success_response("Promotion redeemed successfully", data=result)
        except Exception as e:
            logger.error(f"Error redeeming promotion: {str(e)}")
            return error_response("Failed to redeem promotion", 500)
