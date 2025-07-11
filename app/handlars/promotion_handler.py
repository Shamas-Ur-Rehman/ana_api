from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.promotion import RedeemRequest

from app.schemas.promotion import (
    PromotionCreate,
    PromotionUpdate,
    PromotionApproval,
)
from app.services.promotion_service import PromotionService
from app.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel


class PromotionHandler:
    async def create_promotion(
        promotion: PromotionCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).create_promotion(promotion, current_user.id)

    async def submit_for_approval(
        promotion_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).submit_for_approval(promotion_id, current_user.id)


    async def approve_promotion(
        promotion_id: int,
        data: PromotionApproval,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).approve_promotion(promotion_id, data, current_user.id)

    async def reject_promotion(
        promotion_id: int,
        data: PromotionApproval,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).reject_promotion(promotion_id, data, current_user.id)

    async def get_promotions(
        status: str = None,
        db: Session = Depends(get_db),
    ):
        return PromotionService(db).get_all_promotions(status)

    async def get_promotion(
        promotion_id: int,
        db: Session = Depends(get_db),
    ):
        return PromotionService(db).get_promotion(promotion_id)

    async def update_promotion(
        promotion_id: int,
        promotion: PromotionUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).update_promotion(promotion_id, promotion, current_user.id)
    async def delete_promotion(
        promotion_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).delete_promotion(promotion_id, current_user.id)
    async def toggle_promotion_status(
        promotion_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).toggle_promotion_status(promotion_id, current_user.id)
    
    async def get_public_promotions(db: Session = Depends(get_db)):
        return PromotionService(db).get_public_promotions()

    async def save_promotion(
        promotion_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        return PromotionService(db).save_promotion(promotion_id, current_user.id)

    async def redeem_promotion(
        data: RedeemRequest,
        db: Session = Depends(get_db),
    ):
        return PromotionService(db).redeem_promotion(data.code)