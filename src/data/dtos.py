from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.domain.entities import Execution


class LLMExecutionDTO(BaseModel):
    """
    Data Transfer Object para a resposta da API.
    """
    id: Optional[str] = None
    inputTokens: int
    outputTokens: int
    result: Optional[str] = None
    success: bool
    startDate: str
    endDate: str
    storageImagePath: Optional[str] = None
    prompt: str

    def to_domain(self, execution_type: str) -> Execution:
        """
        Converte o DTO na entidade de domínio.
        """
        return Execution(
            id=self.id or "",
            execution_type=execution_type,
            input_tokens=self.inputTokens,
            output_tokens=self.outputTokens,
            result=self.result,
            success=self.success,
            start_date=datetime.fromisoformat(self.startDate.replace("Z", "+00:00")),
            end_date=datetime.fromisoformat(self.endDate.replace("Z", "+00:00")),
            storage_image_path=self.storageImagePath,
            prompt=self.prompt
        )