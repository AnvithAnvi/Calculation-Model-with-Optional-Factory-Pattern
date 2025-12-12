import pytest
from sqlalchemy.orm import Session
from app.stats import compute_stats
from app.database import get_db, Base, engine
from app.models import User, Calculation
from app.security import hash_password


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_compute_stats_basic(test_db: Session):
    # create a user
    u = User(username='stats_user', email='stats@example.com', password_hash=hash_password('x'))
    test_db.add(u)
    test_db.commit()
    test_db.refresh(u)

    # add some calculations
    calcs = [
        Calculation(a=1, b=2, type='add', result=3, user_id=u.id),
        Calculation(a=10, b=3, type='modulus', result=1, user_id=u.id),
        Calculation(a=2, b=5, type='exponent', result=32, user_id=u.id),
    ]
    for c in calcs:
        test_db.add(c)
    test_db.commit()

    stats = compute_stats(test_db, u.id, recent=3)
    assert stats['total'] == 3
    assert 'modulus' in stats['counts']
    assert any(r['type'] == 'exponent' for r in stats['recent'])
