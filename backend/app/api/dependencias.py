from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

SesionDB = Annotated[Session, Depends(get_db)]
