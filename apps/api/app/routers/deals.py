from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_current_user, get_db
from ..models import Deal, History, Pipeline, Stage

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("", response_model=list[schemas.DealOut])
def list_deals(
    pipeline_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(Deal).filter(Deal.workspace_id == user.workspace_id)
    if pipeline_id is not None:
        query = query.filter(Deal.pipeline_id == pipeline_id)
    return query.order_by(Deal.created_at.desc()).all()


@router.post("", response_model=schemas.DealOut)
def create_deal(
    payload: schemas.DealCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    stage = db.get(Stage, payload.stage_id)
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    pipeline = db.get(Pipeline, stage.pipeline_id)
    if pipeline is None or pipeline.workspace_id != user.workspace_id:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    deal = Deal(
        workspace_id=user.workspace_id,
        pipeline_id=pipeline.id,
        stage_id=stage.id,
        title=payload.title,
        value=payload.value,
        notes=payload.notes,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.patch("/{deal_id}", response_model=schemas.DealOut)
def update_deal(
    deal_id: int,
    payload: schemas.DealUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    deal = db.get(Deal, deal_id)
    if deal is None or deal.workspace_id != user.workspace_id:
        raise HTTPException(status_code=404, detail="Deal not found")
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(deal, key, value)
    db.commit()
    db.refresh(deal)
    return deal


@router.patch("/{deal_id}/stage", response_model=schemas.DealOut)
def move_deal_stage(
    deal_id: int,
    payload: schemas.DealStageUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    deal = db.get(Deal, deal_id)
    if deal is None or deal.workspace_id != user.workspace_id:
        raise HTTPException(status_code=404, detail="Deal not found")
    new_stage = db.get(Stage, payload.stage_id)
    if new_stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    if new_stage.pipeline_id != deal.pipeline_id:
        raise HTTPException(status_code=400, detail="Stage not in pipeline")
    history = History(
        deal_id=deal.id,
        from_stage_id=deal.stage_id,
        to_stage_id=new_stage.id,
        changed_by_user_id=user.id,
    )
    deal.stage_id = new_stage.id
    db.add(history)
    db.commit()
    db.refresh(deal)
    return deal
