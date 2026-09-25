from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import Base, engine
from pydantic import BaseModel
from database import get_db

import models

Base.metadata.create_all(bind=engine)

app = FastAPI()

class TodoCreate(BaseModel):
    title: str

class TodoUpdate(BaseModel):
    title: str
    completed: bool

@app.get("/")
def home():
    return {"message": "Todo API is running"}

@app.post("/todos")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = models.Todo(
        title = todo.title
    )

    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)

    return new_todo

@app.get("/todos")
def get_todos(db: Session = Depends(get_db)):
    statement = select(models.Todo)

    todos = db.scalars(statement).all()

    return todos

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int, db: Session = Depends(get_db)):

    statement = select(models.Todo).where(models.Todo.id == todo_id)
    todo = db.scalar(statement)
    if todo:
        return todo
    else:
        raise HTTPException(status_code=404, detail="ToDo Not Found")

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, update: TodoUpdate, db: Session = Depends(get_db)):
    statement = select(models.Todo).where(models.Todo.id == todo_id)
    todo = db.scalar(statement)

    if todo:
        todo.title = update.title
        todo.completed = update.completed
        db.commit()
        db.refresh(todo)

        return todo

    else:
        raise HTTPException(status_code=404, detail="Todo Not Found")

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    statement = select(models.Todo).where(models.Todo.id == todo_id)
    todo = db.scalar(statement)

    if not todo:
        raise HTTPException(status_code=404, detail="Todo not Found")
    
    db.delete(todo)
    db.commit()
    return {
        "message": "Todo deleted successfully",
        "deleted_id": todo_id
    }
