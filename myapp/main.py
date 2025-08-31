from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session
from .db import engine, get_session
from . import crud
from .models import User, Wallet
from pydantic import BaseModel
import os 
import uvicorn 
app = FastAPI(title="Wallet API")

# Create DB tables on startup
@app.on_event("startup")
def on_startup():
    crud.create_tables(engine)
    # create some sample users if none exist
    with Session(engine) as s:
        if s.exec("SELECT COUNT(*) FROM user").one()[0] == 0:
            u1 = User(name="Alice", email="alice@example.com", phone="+911234567890")
            u2 = User(name="Bob", email="bob@example.com", phone="+919876543210")
            s.add_all([u1, u2])
            s.commit()

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

# Endpoints
@app.get("/users")
def list_users(session: Session = Depends(get_session)):
    return crud.get_all_users(session)

class WalletUpdate(BaseModel):
    amount: float
    operation: str  # 'add' or 'set'
    description: str | None = None

@app.post("/wallet/{user_id}")
def update_wallet(user_id: int, body: WalletUpdate, session: Session = Depends(get_session)):
    result, err = crud.update_wallet(session, user_id, body.amount, body.operation, body.description)
    if err == "user_not_found":
        raise HTTPException(status_code=404, detail="User not found")
    if err == "invalid_operation":
        raise HTTPException(status_code=400, detail="Invalid operation. Use 'add' or 'set'.")
    return result

@app.get("/transactions/{user_id}")
def fetch_transactions(user_id: int, session: Session = Depends(get_session)):
    txs = crud.get_transactions_for_user(session, user_id)
    return {"user_id": user_id, "transactions": txs}
if __name__ == "__main__":
    
    port = int(os.environ.get("PORT" , 8000))
    uvicorn.run (app , host ="0.0.0.0",port = port )
