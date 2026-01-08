from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models import Pipeline
from app.models.user import User, UserRole
from app.schemas.pipeline import PipelineCreate, PipelineOut

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("/", response_model=list[PipelineOut])
def list_pipelines(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[PipelineOut]:
    return (
        db.query(Pipeline)
        .filter(Pipeline.workspace_id == current_user.workspace_id)
        .all()
    )


@router.post("/", response_model=PipelineOut, status_code=status.HTTP_201_CREATED)
def create_pipeline(
    payload: PipelineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> PipelineOut:
    pipeline = Pipeline(name=payload.name, workspace_id=current_user.workspace_id)
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return pipeline


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pipeline(
    pipeline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.admin, UserRole.manager)),
) -> None:
    pipeline = (
        db.query(Pipeline)
        .filter(
            Pipeline.id == pipeline_id,
            Pipeline.workspace_id == current_user.workspace_id,
        )
        .first()
    )
    if not pipeline:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found")
    db.delete(pipeline)
    db.commit()
