from sqlalchemy.orm import Session

from .models import Deal, Pipeline, Stage, User, Workspace
from .security import hash_password


DEFAULT_PASSWORD = "admin123"


def seed_initial_data(db: Session) -> None:
    if db.query(Workspace).first():
        return

    workspace = Workspace(name="Lemonfive")
    db.add(workspace)
    db.flush()

    admin = User(
        workspace_id=workspace.id,
        email="admin@lemonfive.test",
        hashed_password=hash_password(DEFAULT_PASSWORD),
        role="admin",
    )
    db.add(admin)
    db.flush()

    pipeline = Pipeline(workspace_id=workspace.id, name="Default Pipeline")
    db.add(pipeline)
    db.flush()

    stage_names = ["Lead", "Qualified", "Proposal", "Won"]
    stages = []
    for idx, name in enumerate(stage_names):
        stage = Stage(pipeline_id=pipeline.id, name=name, position=idx)
        stages.append(stage)
        db.add(stage)

    db.flush()

    deals = [
        Deal(
            workspace_id=workspace.id,
            pipeline_id=pipeline.id,
            stage_id=stages[0].id,
            title="Acme Corp",
            value=12000,
        ),
        Deal(
            workspace_id=workspace.id,
            pipeline_id=pipeline.id,
            stage_id=stages[0].id,
            title="Globex",
            value=8500,
        ),
        Deal(
            workspace_id=workspace.id,
            pipeline_id=pipeline.id,
            stage_id=stages[1].id,
            title="Initech",
            value=15000,
        ),
        Deal(
            workspace_id=workspace.id,
            pipeline_id=pipeline.id,
            stage_id=stages[2].id,
            title="Umbrella",
            value=22000,
        ),
        Deal(
            workspace_id=workspace.id,
            pipeline_id=pipeline.id,
            stage_id=stages[3].id,
            title="Stark Industries",
            value=50000,
        ),
    ]
    db.add_all(deals)
    db.commit()
