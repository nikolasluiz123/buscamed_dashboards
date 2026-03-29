import json
import os
from typing import Dict, Any, List, Optional

from src.data.repositories import ExecutionRepository
from src.data.file.file_reader import FileReader
from src.domain.constants.json_keys import PillPackKeys as Keys
from src.domain.entities import ExecutionFilter
from src.domain.use_cases.evaluation.evaluators import (
    EvaluateTextSimilarityUseCase,
    EvaluateExactMatchUseCase,
    EvaluateListGreedyMatchingUseCase
)


class CalculatePillPackAccuracyUseCase:
    """
    Calcula a acurácia das execuções de Cartelas de Comprimidos.
    """

    def __init__(
            self,
            repository: ExecutionRepository,
            file_reader: FileReader,
            answer_key_path: str,
            text_evaluator: EvaluateTextSimilarityUseCase,
            exact_evaluator: EvaluateExactMatchUseCase,
            list_evaluator: EvaluateListGreedyMatchingUseCase
    ):
        self.repository = repository
        self.file_reader = file_reader
        self.answer_key_path = answer_key_path
        self.text_evaluator = text_evaluator
        self.exact_evaluator = exact_evaluator
        self.list_evaluator = list_evaluator

    def execute(self, filters: Optional[ExecutionFilter] = None) -> float:
        """
        Calcula a média de acurácia de todas as execuções válidas no banco de dados.
        """
        executions = self.repository.get_all_executions(filters)
        answer_key_data = self.file_reader.load_json(self.answer_key_path)

        total_score = 0.0
        valid_executions = 0

        for execution in executions:
            if not execution.result:
                continue

            if execution.storage_image_path:
                execution_id = self._extract_id_from_path(execution.storage_image_path)
            else:
                execution_id = execution.id

            if execution_id not in answer_key_data:
                continue

            try:
                predicted_json = json.loads(execution.result)
                expected_json = answer_key_data[execution_id]

                execution_score = self._evaluate_pill_pack(expected_json, predicted_json)
                total_score += execution_score
                valid_executions += 1

            except json.JSONDecodeError:
                continue

        return (total_score / valid_executions * 100) if valid_executions > 0 else 0.0

    def _extract_id_from_path(self, storage_image_path: str) -> str:
        """
        Extrai o identificador do arquivo a partir do caminho completo do storage.
        """
        file_name = os.path.basename(storage_image_path)
        return os.path.splitext(file_name)[0]

    def _evaluate_pill_pack(self, expected: Dict[str, Any], predicted: Dict[str, Any]) -> float:
        """
        Avalia o documento completo da cartela de comprimidos aplicando os pesos raiz.
        """
        weights = self._get_root_weights()

        nome_score = self.text_evaluator.execute(expected.get(Keys.NOME_MEDICAMENTO),
                                                 predicted.get(Keys.NOME_MEDICAMENTO))
        componentes_score = self._evaluate_componentes_list(expected.get(Keys.COMPONENTES, []),
                                                            predicted.get(Keys.COMPONENTES, []))
        uso_score = self._evaluate_uso_field(expected.get(Keys.USO), predicted.get(Keys.USO))
        indicacoes_score = self.list_evaluator.execute(expected.get(Keys.INDICACOES, []),
                                                       predicted.get(Keys.INDICACOES, []), self.text_evaluator.execute)
        validade_score = self.exact_evaluator.execute(expected.get(Keys.DATA_VALIDADE),
                                                      predicted.get(Keys.DATA_VALIDADE))
        lote_score = self.exact_evaluator.execute(expected.get(Keys.LOTE), predicted.get(Keys.LOTE))

        final_score = (
                (nome_score * weights["nome_medicamento"]) +
                (componentes_score * weights["componentes"]) +
                (uso_score * weights["uso"]) +
                (indicacoes_score * weights["indicacoes"]) +
                (validade_score * weights["data_validade"]) +
                (lote_score * weights["lote"])
        )

        return final_score

    def _get_root_weights(self) -> Dict[str, float]:
        """
        Define a importância de cada atributo principal na composição da nota final da cartela.
        A soma de todos os pesos deve resultar em 1.0.
        """
        return {
            "nome_medicamento": 0.30,
            "componentes": 0.40,
            "uso": 0.10,
            "indicacoes": 0.10,
            "data_validade": 0.05,
            "lote": 0.05
        }

    def _evaluate_componentes_list(self, expected_list: List[Any], predicted_list: List[Any]) -> float:
        """
        Avalia a lista de princípios ativos e dosagens da cartela.
        """
        return self.list_evaluator.execute(expected_list, predicted_list, self._evaluate_single_componente)

    def _evaluate_single_componente(self, expected: Dict[str, Any], predicted: Dict[str, Any]) -> float:
        """
        Avalia individualmente um objeto de componente da cartela.
        """
        principio_score = self.text_evaluator.execute(expected.get(Keys.PRINCIPIO_ATIVO),
                                                      predicted.get(Keys.PRINCIPIO_ATIVO))
        valor_score = self.exact_evaluator.execute(expected.get(Keys.DOSAGEM_VALOR), predicted.get(Keys.DOSAGEM_VALOR))
        unidade_score = self.text_evaluator.execute(expected.get(Keys.DOSAGEM_UNIDADE),
                                                    predicted.get(Keys.DOSAGEM_UNIDADE))

        return (principio_score * 0.6) + (valor_score * 0.3) + (unidade_score * 0.1)

    def _evaluate_uso_field(self, expected: Optional[Dict[str, Any]], predicted: Optional[Dict[str, Any]]) -> float:
        """
        Avalia as listas internas do objeto de uso, como vias de administração e restrições.
        """
        if not expected and not predicted:
            return 1.0
        if not expected or not predicted:
            return 0.0

        vias_score = self.list_evaluator.execute(
            expected.get(Keys.VIAS_ADMINISTRACAO, []),
            predicted.get(Keys.VIAS_ADMINISTRACAO, []),
            self.text_evaluator.execute
        )

        restricoes_score = self.list_evaluator.execute(
            expected.get(Keys.RESTRICOES_IDADE, []),
            predicted.get(Keys.RESTRICOES_IDADE, []),
            self.text_evaluator.execute
        )

        return (vias_score * 0.5) + (restricoes_score * 0.5)