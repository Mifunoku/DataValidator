from pydantic import BaseModel
from typing import Optional

class DatasetMetrics(BaseModel):
    total: int
    wrong_initial: int
    accuracy_initial: float
    wrong_current: Optional[int] = None
    accuracy_current: Optional[float] = None
    download_url: Optional[str] = None

class PatchRowRequest(BaseModel):
    fixed_category: str

class DataRow(BaseModel):
    id: str
    product_text: str
    model_category: str
    fixed_category: Optional[str] = None
