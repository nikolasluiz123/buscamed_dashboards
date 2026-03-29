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
    prompt: str

@dataclass
class ExecutionFilter:
    """
    Objeto de valor responsável por encapsular os parâmetros de filtragem de execuções.
    """
    prompt: Optional[str] = None

@dataclass
class ExecutionAnalyticsResult:
    """
    Representa o resultado analítico processado de uma execução.
    """
    execution_id: str
    start_date: datetime
    input_tokens: int
    output_tokens: int
    processing_time_seconds: float
    accuracy_percentage: float