"""Media Library & Upload API Router."""

from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from app.api.deps import get_current_user
from app.models.asset import Asset, AssetUploadResponse
from app.models.auth import UserInDB
from app.services.asset_service import asset_service

router = APIRouter(prefix="/assets", tags=["Media Assets"])


@router.get("", response_model=List[Asset])
def list_assets(user: UserInDB = Depends(get_current_user)):
    """List all media assets in user's library."""
    return asset_service.list_user_assets(user.id)


@router.post("/upload", response_model=AssetUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset(file: UploadFile = File(...), user: UserInDB = Depends(get_current_user)):
    """Upload an image or asset into the media library."""
    try:
        content = await file.read()
        asset = asset_service.save_uploaded_file(
            user_id=user.id,
            filename=file.filename or "uploaded_image.png",
            content=content,
            content_type=file.content_type or "image/png",
        )
        return AssetUploadResponse(asset=asset, message="Asset uploaded successfully.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload asset: {str(e)}")


@router.delete("/{asset_id}")
def delete_asset(asset_id: str, user: UserInDB = Depends(get_current_user)):
    """Remove asset from library."""
    success = asset_service.delete_asset(asset_id)
    return {"success": success, "message": "Asset deleted successfully."}

