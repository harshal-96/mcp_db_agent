from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    cases = db.query(models.Case).all()
    clients = db.query(models.Client).all()
    lawyers = db.query(models.Lawyer).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cases": cases,
        "clients": clients,
        "lawyers": lawyers
    })

@app.post("/add_case")
def add_case(
    title: str = Form(...),
    description: str = Form(...),
    client_id: int = Form(...),
    lawyer_id: int = Form(...),
    db: Session = Depends(get_db)
):
    case = models.Case(title=title, description=description, client_id=client_id, lawyer_id=lawyer_id)
    db.add(case)
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/add_client")
def add_client(name: str = Form(...), contact: str = Form(...), db: Session = Depends(get_db)):
    db.add(models.Client(name=name, contact=contact))
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/add_lawyer")
def add_lawyer(name: str = Form(...), specialization: str = Form(...), db: Session = Depends(get_db)):
    db.add(models.Lawyer(name=name, specialization=specialization))
    db.commit()
    return RedirectResponse("/", status_code=303)
