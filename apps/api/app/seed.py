import datetime

from sqlalchemy.orm import Session

from app.models import Deal, DealStageHistory, Pipeline, Stage, User, Workspace
from app.models.user import UserRole
from app.services.auth import hash_password


def seed_data(db: Session) -> None:
    if db.query(Workspace).count() > 0:
        return
    workspace = Workspace(name="Lemonfive")
    db.add(workspace)
    db.flush()

    admin = User(
        email="admin@lemonfive.local",
        full_name="Admin",
        hashed_password=hash_password("admin123"),
        role=UserRole.admin,
        workspace_id=workspace.id,
    )
    db.add(admin)
    db.flush()

    pipeline = Pipeline(name="Pipeline principal", workspace_id=workspace.id)
    db.add(pipeline)
    db.flush()

    stage_names = ["Prospection", "Qualification", "Proposition", "Négociation", "Gagné"]
    stages = []
    for index, name in enumerate(stage_names, start=1):
        stage = Stage(name=name, position=index, pipeline_id=pipeline.id)
        db.add(stage)
        stages.append(stage)
    db.flush()

    deals = [
        ("Orange Industries", 12000),
        ("Bluebird Labs", 8000),
        ("Everest Corp", 15000),
        ("Northwind", 9500),
        ("Contoso", 20000),
    ]
    for idx, (title, amount) in enumerate(deals):
        stage = stages[min(idx, len(stages) - 1)]
        deal = Deal(
            title=title,
            amount=amount,
            currency="EUR",
            stage_id=stage.id,
            owner_id=admin.id,
            priority=2,
            expected_close_date=datetime.date.today() + datetime.timedelta(days=30 + idx * 3),
            workspace_id=workspace.id,
        )
        db.add(deal)
        db.flush()
        db.add(
            DealStageHistory(
                deal_id=deal.id,
                from_stage_id=None,
                to_stage_id=deal.stage_id,
            )
        )

    db.commit()
