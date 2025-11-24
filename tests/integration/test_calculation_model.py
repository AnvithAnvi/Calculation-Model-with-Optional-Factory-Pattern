# tests/integration/test_calculation_model.py
from sqlalchemy.orm import Session
from app.models import Calculation, User
from app.schemas import OperationType
from app.calculation_factory import CalculationFactory

def test_insert_calculation_record(db_session: Session):
    """
    Test explicitly inserting a calculation record into the DB 
    and ensuring fields are mapped correctly (a, b, type).
    """
    # 1. Create a user to attach to
    user = User(username="math_user", email="math@test.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # 2. Create Calculation Data
    a, b = 10.0, 5.0
    op_type = OperationType.MULTIPLY
    result = CalculationFactory.calculate(a, b, op_type)

    # 3. Insert Record
    calc = Calculation(
        a=a,
        b=b,
        type=op_type,
        result=result,
        user_id=user.id
    )
    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    # 4. Verify in DB
    saved_calc = db_session.query(Calculation).filter(Calculation.id == calc.id).first()
    assert saved_calc is not None
    assert saved_calc.a == 10.0
    assert saved_calc.b == 5.0
    assert saved_calc.type == "multiply"
    assert saved_calc.result == 50.0
    assert saved_calc.user_id == user.id

def test_calculation_relationship(db_session: Session):
    """Ensure the user relationship works properly"""
    user = User(username="rel_user", email="rel@test.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    calc = Calculation(a=1, b=1, type="add", result=2, user_id=user.id)
    db_session.add(calc)
    db_session.commit()

    # Fetch user and check calculations list
    db_session.refresh(user)
    assert len(user.calculations) == 1
    assert user.calculations[0].result == 2