from pydantic import BaseModel
from typing import Optional

class DatasetMetrics(BaseModel):
    total: int
    wrong_initial: int = 0
    accuracy_initial: float = None
    wrong_current: int = 0
    accuracy_current: float = None
    download_url: Optional[str] = None

class PatchRowRequest(BaseModel):
    fixed_category: str