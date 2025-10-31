from typing import Iterable, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, col, func, select

from .models import (
    Agent,
    AgentCreate,
    AgentRead,
    DashboardSummary,
    Movement,
    MovementCreate,
    MovementRead,
    MovementType,
    Voucher,
    VoucherCreate,
    VoucherRead,
    VoucherUpdate,
    VoucherWithMovements,
)


def create_agent(session: Session, payload: AgentCreate) -> AgentRead:
    agent = Agent.model_validate(payload)
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return AgentRead.model_validate(agent)


def list_agents(session: Session) -> Iterable[AgentRead]:
    agents = session.exec(select(Agent).order_by(Agent.name)).all()
    return [AgentRead.model_validate(agent) for agent in agents]


def create_voucher(session: Session, payload: VoucherCreate) -> VoucherRead:
    existing = session.exec(select(Voucher).where(col(Voucher.code) == payload.code)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un voucher con código {payload.code}",
        )

    voucher = Voucher.model_validate(payload)
    session.add(voucher)
    session.commit()
    session.refresh(voucher)
    return VoucherRead.model_validate(voucher)


def list_vouchers(session: Session, status_filter: Optional[str] = None) -> Iterable[VoucherRead]:
    query = select(Voucher)
    if status_filter:
        query = query.where(col(Voucher.status) == status_filter)
    vouchers = session.exec(query.order_by(Voucher.issue_date.desc())).all()
    return [VoucherRead.model_validate(voucher) for voucher in vouchers]


def get_voucher(session: Session, voucher_id: int) -> VoucherWithMovements:
    voucher = session.exec(
        select(Voucher)
        .where(Voucher.id == voucher_id)
        .options(selectinload(Voucher.movements).selectinload(Movement.agent))
    ).one_or_none()

    if voucher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher no encontrado")

    return VoucherWithMovements.model_validate(voucher)


def update_voucher(session: Session, voucher_id: int, payload: VoucherUpdate) -> VoucherRead:
    voucher = session.get(Voucher, voucher_id)
    if voucher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher no encontrado")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(voucher, field, value)
    session.add(voucher)
    session.commit()
    session.refresh(voucher)
    return VoucherRead.model_validate(voucher)


def create_movement(session: Session, payload: MovementCreate) -> MovementRead:
    voucher = session.get(Voucher, payload.voucher_id)
    if voucher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher no encontrado")

    if payload.agent_id is not None:
        agent = session.get(Agent, payload.agent_id)
        if agent is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agente no encontrado")

    movement = Movement.model_validate(payload)
    session.add(movement)
    session.commit()
    session.refresh(movement)
    return MovementRead.model_validate(movement)


def list_movements(session: Session, voucher_id: Optional[int] = None) -> Iterable[MovementRead]:
    query = select(Movement)
    if voucher_id is not None:
        query = query.where(Movement.voucher_id == voucher_id)
    movements = session.exec(query.order_by(Movement.created_at.desc())).all()
    return [MovementRead.model_validate(m) for m in movements]


def dashboard_summary(session: Session) -> DashboardSummary:
    total_vouchers = session.exec(select(func.count(Voucher.id))).one()
    total_ingresos = session.exec(
        select(func.coalesce(func.sum(Movement.amount), 0)).where(Movement.type == MovementType.ingreso)
    ).one()
    total_egresos = session.exec(
        select(func.coalesce(func.sum(Movement.amount), 0)).where(Movement.type == MovementType.egreso)
    ).one()

    saldo_pendiente = total_ingresos - total_egresos

    return DashboardSummary(
        total_vouchers=total_vouchers,
        total_ingresos=total_ingresos,
        total_egresos=total_egresos,
        saldo_pendiente=saldo_pendiente,
    )
