from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


class VoucherStatus(str, Enum):
    borrador = "borrador"
    emitido = "emitido"
    cancelado = "cancelado"


class MovementType(str, Enum):
    ingreso = "ingreso"
    egreso = "egreso"


class AgentBase(SQLModel):
    name: str = Field(index=True)
    email: str | None = Field(default=None, index=True)
    phone: str | None = None
    role: str | None = Field(default=None, description="Rol o puesto del agente")

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if "@" not in value:
            raise ValueError("El email debe contener '@'")
        return value


class Agent(AgentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    movements: List["Movement"] = Relationship(back_populates="agent")


class AgentCreate(AgentBase):
    pass


class AgentRead(AgentBase):
    id: int


class VoucherBase(SQLModel):
    code: str = Field(index=True, unique=True, description="Identificador externo del voucher")
    client_name: str = Field(index=True)
    issue_date: date
    currency: str = Field(default="USD", max_length=3, description="Moneda del voucher")
    total_amount: float = Field(description="Monto total del voucher")
    status: VoucherStatus = Field(default=VoucherStatus.borrador)
    notes: Optional[str] = Field(default=None, description="Comentarios adicionales")


class Voucher(VoucherBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    movements: List["Movement"] = Relationship(back_populates="voucher")


class VoucherCreate(VoucherBase):
    pass


class VoucherUpdate(SQLModel):
    client_name: Optional[str] = None
    issue_date: Optional[date] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[VoucherStatus] = None
    notes: Optional[str] = None


class VoucherRead(VoucherBase):
    id: int


class MovementBase(SQLModel):
    type: MovementType
    amount: float = Field(gt=0, description="Monto del movimiento")
    description: Optional[str] = None
    effective_date: date = Field(default_factory=date.today)


class Movement(MovementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    voucher_id: int = Field(foreign_key="voucher.id")
    agent_id: Optional[int] = Field(default=None, foreign_key="agent.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    voucher: Voucher = Relationship(back_populates="movements")
    agent: Optional[Agent] = Relationship(back_populates="movements")


class MovementCreate(MovementBase):
    voucher_id: int
    agent_id: Optional[int] = None


class MovementRead(MovementBase):
    id: int
    voucher_id: int
    agent_id: Optional[int]
    created_at: datetime


class VoucherWithMovements(VoucherRead):
    movements: List[MovementRead] = Field(default_factory=list)


class DashboardSummary(SQLModel):
    total_vouchers: int
    total_ingresos: float
    total_egresos: float
    saldo_pendiente: float
