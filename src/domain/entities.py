from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class ExecutionType(str, Enum):
    """
    Define o tipo de dado principal que foi submetido para processamento na LLM.
    """
    IMAGE = "IMAGE"
    TEXT = "TEXT"

@dataclass
class Execution:
    """
    Representa a entidade de negócio de uma execução da LLM.
    """
    id: str
    execution_type: str
    processing_type: ExecutionType
    input_text: Optional[str]
    input_tokens: int
    output_tokens: int
    result: Optional[str]
    success: bool
    start_date: datetime
    end_date: datetime
    storage_image_path: Optional[str]
    prompt: str
    client_processor_version: str

@dataclass
class ExecutionFilter:
    """
    Objeto de valor responsável por encapsular os parâmetros de filtragem de execuções.
    """
    prompt: Optional[str] = None
    processing_type: Optional[ExecutionType] = None
    client_processor_version: Optional[str] = None

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

@dataclass
class EvaluatedExecution:
    """
    Representa uma execução avaliada contendo a entidade original,
    o gabarito associado e a nota de acurácia.
    """
    execution: Execution
    expected_data: dict
    accuracy_score: float