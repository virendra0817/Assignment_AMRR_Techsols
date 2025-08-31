Start the app: uvicorn app.main:app --reload
Open Swagger UI: http://127.0.0.1:8000/docs
Endpoints

GET /users — list users with balance

POST /wallet/{user_id} — body: { "amount": 50.0, "operation": "add" } or "operation": "set"

GET /transactions/{user_id} — list transactions for that user

live demo link :
