from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models import Deal, DealStageHistory, Stage
from app.models.user import User
from app.schemas.deal import DealCreate, DealOut, DealStageUpdate, DealUpdate

router = APIRouter(prefix="/deals", tags=["deals"])


@router.get("/", response_model=list[DealOut])
def list_deals(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[DealOut]:
    return (
        db.query(Deal)
        .filter(Deal.workspace_id == current_user.workspace_id)
        .order_by(Deal.created_at.desc())
        .all()
    )


@router.post("/", response_model=DealOut, status_code=status.HTTP_201_CREATED)
def create_deal(
    payload: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DealOut:
    stage = (
        db.query(Stage)
        .join(Stage.pipeline)
        .filter(Stage.id == payload.stage_id)
        .first()
    )
    if not stage or stage.pipeline.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    deal = Deal(
        title=payload.title,
        amount=payload.amount,
        currency=payload.currency,
        stage_id=payload.stage_id,
        owner_id=payload.owner_id,
        priority=payload.priority,
        expected_close_date=payload.expected_close_date,
        workspace_id=current_user.workspace_id,
    )
    db.add(deal)
    db.flush()
    db.add(DealStageHistory(deal_id=deal.id, from_stage_id=None, to_stage_id=deal.stage_id))
    db.commit()
    db.refresh(deal)
    return deal


@router.patch("/{deal_id}", response_model=DealOut)
def update_deal(
    deal_id: int,
    payload: DealUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DealOut:
    deal = (
        db.query(Deal)
        .filter(Deal.id == deal_id, Deal.workspace_id == current_user.workspace_id)
        .first()
    )
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(deal, field, value)
    db.commit()
    db.refresh(deal)
    return deal


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    deal = (
        db.query(Deal)
        .filter(Deal.id == deal_id, Deal.workspace_id == current_user.workspace_id)
        .first()
    )
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    db.delete(deal)
    db.commit()


@router.patch("/{deal_id}/stage", response_model=DealOut)
def update_deal_stage(
    deal_id: int,
    payload: DealStageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DealOut:
    deal = (
        db.query(Deal)
        .filter(Deal.id == deal_id, Deal.workspace_id == current_user.workspace_id)
        .first()
    )
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    stage = (
        db.query(Stage)
        .join(Stage.pipeline)
        .filter(Stage.id == payload.stage_id)
        .first()
    )
    if not stage or stage.pipeline.workspace_id != current_user.workspace_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    from_stage = deal.stage_id
    deal.stage_id = payload.stage_id
    db.add(DealStageHistory(deal_id=deal.id, from_stage_id=from_stage, to_stage_id=payload.stage_id))
    db.commit()
    db.refresh(deal)
    return deal
