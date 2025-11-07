from typing import List, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from . import crud, models
from .database import get_session, init_db

app = FastAPI(title="Viaje x Mundo - Gestión de Vouchers", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/agents", response_model=models.AgentRead, status_code=201)
def create_agent(
    payload: models.AgentCreate,
    session: Session = Depends(get_session),
) -> models.AgentRead:
    return crud.create_agent(session, payload)


@app.get("/agents", response_model=List[models.AgentRead])
def list_agents(session: Session = Depends(get_session)) -> List[models.AgentRead]:
    return crud.list_agents(session)


@app.post("/vouchers", response_model=models.VoucherRead, status_code=201)
def create_voucher(
    payload: models.VoucherCreate,
    session: Session = Depends(get_session),
) -> models.VoucherRead:
    return crud.create_voucher(session, payload)


@app.get("/vouchers", response_model=List[models.VoucherRead])
def list_vouchers(
    status: Optional[models.VoucherStatus] = None,
    session: Session = Depends(get_session),
) -> List[models.VoucherRead]:
    return crud.list_vouchers(session, status_filter=status)


@app.get("/vouchers/{voucher_id}", response_model=models.VoucherWithMovements)
def get_voucher(voucher_id: int, session: Session = Depends(get_session)) -> models.VoucherWithMovements:
    return crud.get_voucher(session, voucher_id)


@app.patch("/vouchers/{voucher_id}", response_model=models.VoucherRead)
def update_voucher(
    voucher_id: int,
    payload: models.VoucherUpdate,
    session: Session = Depends(get_session),
) -> models.VoucherRead:
    return crud.update_voucher(session, voucher_id, payload)


@app.post("/movements", response_model=models.MovementRead, status_code=201)
def create_movement(
    payload: models.MovementCreate,
    session: Session = Depends(get_session),
) -> models.MovementRead:
    return crud.create_movement(session, payload)


@app.get("/movements", response_model=List[models.MovementRead])
def list_movements(
    voucher_id: Optional[int] = None,
    session: Session = Depends(get_session),
) -> List[models.MovementRead]:
    return crud.list_movements(session, voucher_id=voucher_id)


@app.get("/dashboard", response_model=models.DashboardSummary)
def dashboard(session: Session = Depends(get_session)) -> models.DashboardSummary:
    return crud.dashboard_summary(session)
