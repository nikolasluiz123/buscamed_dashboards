from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Execution:
    """
    Representa a entidade de negócio de uma execução da LLM.
    """
    id: str
    execution_type: str
    input_tokens: int
    output_tokens: int
    result: Optional[str]
    success: bool
    start_date: datetime
    end_date: datetime
    storage_image_path: Optional[str]