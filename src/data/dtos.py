from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.domain.entities import Execution, ExecutionType


class LLMExecutionDTO(BaseModel):
    """
    Data Transfer Object para a resposta e envio da API.
    """
    id: Optional[str] = None
    type: str
    inputText: Optional[str] = None
    inputTokens: int
    outputTokens: int
    result: Optional[str] = None
    success: bool
    startDate: datetime
    endDate: datetime
    storageImagePath: Optional[str] = None
    prompt: Optional[str] = None
    clientProcessorVersion: str

    def to_domain(self, execution_type: str) -> Execution:
        """
        Converte o DTO na entidade de domínio.
        """
        return Execution(
            id=self.id or "",
            execution_type=execution_type,
            processing_type=ExecutionType(self.type),
            input_text=self.inputText,
            input_tokens=self.inputTokens,
            output_tokens=self.outputTokens,
            result=self.result,
            success=self.success,
            start_date=self.startDate,
            end_date=self.endDate,
            storage_image_path=self.storageImagePath,
            prompt=self.prompt or "",
            client_processor_version=self.clientProcessorVersion
        )