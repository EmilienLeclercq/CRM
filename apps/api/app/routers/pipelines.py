from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import schemas
from ..deps import get_current_user, get_db, require_admin
from ..models import Pipeline, Stage

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("", response_model=list[schemas.PipelineOut])
def list_pipelines(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Pipeline).filter(Pipeline.workspace_id == user.workspace_id).all()


@router.post("", response_model=schemas.PipelineOut)
def create_pipeline(
    payload: schemas.PipelineCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    pipeline = Pipeline(workspace_id=user.workspace_id, name=payload.name)
    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)
    return pipeline


@router.get("/{pipeline_id}/stages", response_model=list[schemas.StageOut])
def list_stages(
    pipeline_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    pipeline = db.get(Pipeline, pipeline_id)
    if pipeline is None or pipeline.workspace_id != user.workspace_id:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return (
        db.query(Stage)
        .filter(Stage.pipeline_id == pipeline_id)
        .order_by(Stage.position.asc())
        .all()
    )


@router.post("/{pipeline_id}/stages", response_model=schemas.StageOut)
def create_stage(
    pipeline_id: int,
    payload: schemas.StageCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    pipeline = db.get(Pipeline, pipeline_id)
    if pipeline is None or pipeline.workspace_id != user.workspace_id:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    stage = Stage(pipeline_id=pipeline_id, name=payload.name, position=payload.position)
    db.add(stage)
    db.commit()
    db.refresh(stage)
    return stage
