from sqlmodel import Session, select
from .models import User, Wallet, Transaction


def create_tables(engine):
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)


def get_all_users(session: Session):
    stmt = select(User)
    users = session.exec(stmt).all()
    results = []
    for u in users:
        wallet = session.exec(select(Wallet).where(Wallet.user_id == u.id)).first()
        balance = wallet.balance if wallet else 0.0
        results.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "balance": balance,
        })
    return results


def update_wallet(session: Session, user_id: int, amount: float, operation: str, description: str | None = None):
    user = session.get(User, user_id)
    if not user:
        return None, "user_not_found"

    wallet = session.exec(select(Wallet).where(Wallet.user_id == user_id)).first()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        session.add(wallet)
        session.commit()
        session.refresh(wallet)

    if operation == "add":
        new_balance = wallet.balance + amount
        tx_type = "credit" if amount >= 0 else "debit"
    elif operation == "set":
        new_balance = amount
        tx_type = "set"
    else:
        return None, "invalid_operation"

    # create transaction
    tx = Transaction(
        wallet_id=wallet.id,
        amount=amount,
        type=tx_type,
        description=description or "",
        balance_after=new_balance
    )
    wallet.balance = new_balance

    session.add(tx)
    session.add(wallet)
    session.commit()
    session.refresh(wallet)

    return {"wallet_id": wallet.id, "balance": wallet.balance, "transaction_id": tx.id}, None


def get_transactions_for_user(session: Session, user_id: int):
    wallet = session.exec(select(Wallet).where(Wallet.user_id == user_id)).first()
    if not wallet:
        return []

    txs = session.exec(
        select(Transaction).where(Transaction.wallet_id == wallet.id).order_by(Transaction.timestamp.desc())
    ).all()

    return [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "description": t.description,
            "timestamp": t.timestamp.isoformat(),
            "balance_after": t.balance_after,
        }
        for t in txs
    ]
