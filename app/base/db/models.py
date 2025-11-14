import inspect
import sys

from pydantic import BaseModel
from sqlmodel import SQLModel

from app.brand.db.models import Brand

current_module = sys.modules[__name__]
for name, obj in inspect.getmembers(current_module):
    if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
        obj.model_rebuild()

__all__ = [
    "Brand",
]