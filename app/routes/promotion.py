from fastapi import APIRouter, Depends
from app.handlars.promotion_handler import PromotionHandler
from app.middleware.middleware import checkAuth
from app.middleware.permission_check import checkPermission

router = APIRouter(prefix="/promotions", tags=["promotions"])

router.post("/", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "create_promotion"))])(PromotionHandler.create_promotion)
router.get("/", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "get_promotion"))])(PromotionHandler.get_promotions)
router.get("/{promotion_id}", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "get_promotion"))])(PromotionHandler.get_promotion)
router.put("/{promotion_id}", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "update_promotion"))])(PromotionHandler.update_promotion)
router.delete("/{promotion_id}", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "delete_promotion"))])(PromotionHandler.delete_promotion)
router.post("/{promotion_id}/toggle", dependencies=[Depends(checkAuth),Depends(checkPermission("promotions", "toggle_promotion"))])(PromotionHandler.toggle_promotion_status)

router.post("/{promotion_id}/submit", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "submit_promotion"))])(PromotionHandler.submit_for_approval)
router.put("/{promotion_id}/approve", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "approve_promotion"))])(PromotionHandler.approve_promotion)
router.put("/{promotion_id}/reject", dependencies=[Depends(checkAuth), Depends(checkPermission("promotions", "reject_promotion"))])(PromotionHandler.reject_promotion)

router.get("/public/promotions")(PromotionHandler.get_public_promotions)
router.post("/public/promotions/{promotion_id}/save", dependencies=[Depends(checkAuth)])(PromotionHandler.save_promotion)
router.post("/public/promotions/redeem")(PromotionHandler.redeem_promotion)

