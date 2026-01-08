from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models import Pipeline, Stage
from app.models.user import User, UserRole
from app.schemas.stage import StageCreate, StageOut, StageUpdate

router = APIRouter(prefix="/stages", tags=["stages"])


@router.get("/", response_model=list[StageOut])
def list_stages(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[StageOut]:
    return (
        db.query(Stage)
        .join(Pipeline)
        .filter(
            Stage.pipeline_id == pipeline_id,
            Pipeline.workspace_id == current_user.workspace_id,
        )
        .order_by(Stage.position)
        .all()
    )


@router.post("/", response_model=StageOut, status_code=status.HTTP_201_CREATED)
def create_stage(
    payload: StageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> StageOut:
    pipeline = (
        db.query(Pipeline)
        .filter(
            Pipeline.id == payload.pipeline_id,
            Pipeline.workspace_id == current_user.workspace_id,
        )
        .first()
    )
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    stage = Stage(name=payload.name, position=payload.position, pipeline_id=payload.pipeline_id)
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage


@router.patch("/{stage_id}", response_model=StageOut)
def update_stage(
    stage_id: int,
    payload: StageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> StageOut:
    stage = (
        db.query(Stage)
        .join(Pipeline)
        .filter(Stage.id == stage_id, Pipeline.workspace_id == current_user.workspace_id)
        .first()
    )
    if not stage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    if payload.name is not None:
        stage.name = payload.name
    if payload.position is not None:
        stage.position = payload.position
    db.commit()
    db.refresh(stage)
    return stage


@router.delete("/{stage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stage(
    stage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> None:
    stage = (
        db.query(Stage)
        .join(Pipeline)
        .filter(Stage.id == stage_id, Pipeline.workspace_id == current_user.workspace_id)
        .first()
    )
    if not stage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")
    db.delete(stage)
    db.commit()
