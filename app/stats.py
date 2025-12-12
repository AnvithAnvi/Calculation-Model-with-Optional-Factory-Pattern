from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Dict

from app.models import Calculation


def compute_stats(db: Session, user_id: int, recent: int = 5) -> Dict:
    """Compute basic statistics for a user's calculations.

    Returns total count, averages for `a` and `b`, counts per operation type,
    and a list of the most recent `recent` calculations.
    """
    total = db.query(func.count(Calculation.id)).filter(Calculation.user_id == user_id).scalar() or 0
    avg_a = db.query(func.avg(Calculation.a)).filter(Calculation.user_id == user_id).scalar() or 0
    avg_b = db.query(func.avg(Calculation.b)).filter(Calculation.user_id == user_id).scalar() or 0

    # counts per type
    rows = (
        db.query(Calculation.type, func.count(Calculation.id))
        .filter(Calculation.user_id == user_id)
        .group_by(Calculation.type)
        .all()
    )
    counts = {r[0]: r[1] for r in rows}

    recent_rows = (
        db.query(Calculation)
        .filter(Calculation.user_id == user_id)
        .order_by(Calculation.id.desc())
        .limit(recent)
        .all()
    )

    recent_list = [
        {"id": r.id, "a": r.a, "b": r.b, "type": r.type, "result": r.result, "timestamp": r.timestamp.isoformat()}
        for r in recent_rows
    ]

    return {
        "total": int(total),
        "avg_a": float(avg_a) if avg_a is not None else 0.0,
        "avg_b": float(avg_b) if avg_b is not None else 0.0,
        "counts": counts,
        "recent": recent_list,
    }
