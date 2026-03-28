from typing import Dict, Any, Optional
from src.domain.constants.json_keys import PrescriptionKeys as Keys
from src.domain.use_cases.evaluation.evaluators import (
    EvaluateTextSimilarityUseCase,
    EvaluateExactMatchUseCase,
    EvaluateListGreedyMatchingUseCase
)


class EvaluateSinglePrescriptionUseCase:
    """
    Avalia a acurácia de uma única prescrição médica comparando o resultado gerado com o gabarito.
    """

    def __init__(
            self,
            text_evaluator: EvaluateTextSimilarityUseCase,
            exact_evaluator: EvaluateExactMatchUseCase,
            list_evaluator: EvaluateListGreedyMatchingUseCase
    ):
        self.text_evaluator = text_evaluator
        self.exact_evaluator = exact_evaluator
        self.list_evaluator = list_evaluator

    def execute(self, expected: Dict[str, Any], predicted: Dict[str, Any]) -> float:
        """
        Avalia o documento completo da prescrição focando na lista de medicamentos.

        Args:
            expected (Dict[str, Any]): O JSON de gabarito esperado.
            predicted (Dict[str, Any]): O JSON gerado pela LLM.

        Returns:
            float: A pontuação de similaridade (de 0.0 a 1.0).
        """
        expected_meds = expected.get(Keys.MEDICAMENTOS, [])
        predicted_meds = predicted.get(Keys.MEDICAMENTOS, [])

        return self.list_evaluator.execute(expected_meds, predicted_meds, self._evaluate_medicamento_item)

    def _evaluate_medicamento_item(self, expected_item: Dict[str, Any], predicted_item: Dict[str, Any]) -> float:
        """
        Aplica os pesos de negócio para cada propriedade de um medicamento.
        """
        weights = self._get_medicamento_weights()

        nome_score = self.text_evaluator.execute(expected_item.get(Keys.NOME), predicted_item.get(Keys.NOME))
        dosagem_score = self._evaluate_composite_field(
            expected_item.get(Keys.APRESENTACAO_DOSAGEM),
            predicted_item.get(Keys.APRESENTACAO_DOSAGEM)
        )
        dose_score = self._evaluate_composite_field(expected_item.get(Keys.DOSE), predicted_item.get(Keys.DOSE))
        frequencia_score = self._evaluate_frequencia_field(
            expected_item.get(Keys.FREQUENCIA),
            predicted_item.get(Keys.FREQUENCIA)
        )
        duracao_score = self._evaluate_duracao_field(expected_item.get(Keys.DURACAO), predicted_item.get(Keys.DURACAO))
        qtd_total_score = self._evaluate_composite_field(
            expected_item.get(Keys.QUANTIDADE_TOTAL),
            predicted_item.get(Keys.QUANTIDADE_TOTAL)
        )

        final_score = (
                (nome_score * weights["nome"]) +
                (dosagem_score * weights["apresentacao_dosagem"]) +
                (dose_score * weights["dose"]) +
                (frequencia_score * weights["frequencia"]) +
                (duracao_score * weights["duracao"]) +
                (qtd_total_score * weights["quantidade_total_prescrita"])
        )

        return final_score

    def _get_medicamento_weights(self) -> Dict[str, float]:
        """
        Define a importância de cada atributo na composição da nota final do medicamento.
        A soma de todos os pesos deve resultar em 1.0.
        """
        return {
            "nome": 0.40,
            "apresentacao_dosagem": 0.15,
            "dose": 0.15,
            "frequencia": 0.15,
            "duracao": 0.10,
            "quantidade_total_prescrita": 0.05
        }

    def _evaluate_composite_field(self, expected: Optional[Dict[str, Any]],
                                  predicted: Optional[Dict[str, Any]]) -> float:
        """
        Avalia campos compostos por valor (exato) e unidade (aproximado).
        """
        if not expected and not predicted:
            return 1.0
        if not expected or not predicted:
            return 0.0

        valor_score = self.exact_evaluator.execute(expected.get(Keys.VALOR), predicted.get(Keys.VALOR))
        unidade_score = self.text_evaluator.execute(expected.get(Keys.UNIDADE), predicted.get(Keys.UNIDADE))

        return (valor_score * 0.7) + (unidade_score * 0.3)

    def _evaluate_frequencia_field(self, expected: Optional[Dict[str, Any]],
                                   predicted: Optional[Dict[str, Any]]) -> float:
        """
        Avalia o campo de frequência, considerando intervalo numérico e textos de orientação.
        """
        if not expected and not predicted:
            return 1.0
        if not expected or not predicted:
            return 0.0

        intervalo_score = self.exact_evaluator.execute(expected.get(Keys.INTERVALO), predicted.get(Keys.INTERVALO))
        unidade_score = self.text_evaluator.execute(expected.get(Keys.UNIDADE), predicted.get(Keys.UNIDADE))
        texto_score = self.text_evaluator.execute(expected.get(Keys.TEXTO_ORIENTACAO),
                                                  predicted.get(Keys.TEXTO_ORIENTACAO))

        return (intervalo_score * 0.4) + (unidade_score * 0.2) + (texto_score * 0.4)

    def _evaluate_duracao_field(self, expected: Optional[Dict[str, Any]], predicted: Optional[Dict[str, Any]]) -> float:
        """
        Avalia o campo de duração, considerando a flag de uso contínuo com alta precisão.
        """
        if not expected and not predicted:
            return 1.0
        if not expected or not predicted:
            return 0.0

        valor_score = self.exact_evaluator.execute(expected.get(Keys.VALOR), predicted.get(Keys.VALOR))
        unidade_score = self.text_evaluator.execute(expected.get(Keys.UNIDADE), predicted.get(Keys.UNIDADE))
        uso_continuo_score = self.exact_evaluator.execute(expected.get(Keys.USO_CONTINUO),
                                                          predicted.get(Keys.USO_CONTINUO))

        return (valor_score * 0.4) + (unidade_score * 0.2) + (uso_continuo_score * 0.4)