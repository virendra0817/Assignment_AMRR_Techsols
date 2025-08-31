from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str

    wallet: Optional["Wallet"] = Relationship(back_populates="user")


class Wallet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    balance: float = 0.0

    user: Optional[User] = Relationship(back_populates="wallet")
    transactions: List["Transaction"] = Relationship(back_populates="wallet")


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="wallet.id")
    amount: float
    type: str  # 'credit' or 'debit' or 'set'
    description: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    balance_after: float = 0.0

    wallet: Optional[Wallet] = Relationship(back_populates="transactions")
