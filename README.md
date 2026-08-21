# Task Manager

A simple REST API for managing personal tasks, built with FastAPI. Includes JWT-based authentication, so each user only has access to their own tasks.

## Technologies

- Python
- FastAPI
- SQLAlchemy (+ SQLite)
- Pydantic
- python-jose (JWT)
- passlib + bcrypt

## Features

- CRUD operations for tasks (create, read, update, delete)
- JWT-based authentication (register/login)
- Data isolation — each user can only see and manage their own tasks

## Start

1. Clone the repository

2. Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with:
```
SECRET_KEY=your-secret-key-here
```

5. Run the server:
```
uvicorn main:app --reload
```

6. Open the interactive docs at `http://127.0.0.1:8000/docs`

## Endpoints

| Method | Path | Description | Auth required |
|--------|------|--------------|----------------|
| POST | /users | Register a new user | No |
| POST | /login | Log in, receive a JWT token | No |
| GET | /tasks | List your own tasks | Yes |
| GET | /tasks/{id} | Get a single task | Yes |
| POST | /tasks | Create a new task | Yes |
| PATCH | /tasks/{id} | Toggle task status | Yes |
| DELETE | /tasks/{id} | Delete a task | Yes |
