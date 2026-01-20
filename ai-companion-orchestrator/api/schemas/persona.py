from pydantic import BaseModel
from typing import List, Optional

class PersonaResponse(BaseModel):
    id: str
    name: str
    description: str
    version: str
    tags: List[str]
