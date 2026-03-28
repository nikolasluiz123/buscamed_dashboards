from typing import Any, List, Callable, Optional
from rapidfuzz import fuzz


class EvaluateTextSimilarityUseCase:
    """
    Avalia a similaridade entre duas strings utilizando a distância de Levenshtein.
    Retorna uma pontuação normalizada entre 0.0 e 1.0.
    """

    def execute(self, expected: Optional[str], predicted: Optional[str]) -> float:
        if not expected and not predicted:
            return 1.0
        if not expected or not predicted:
            return 0.0

        score = fuzz.ratio(str(expected).lower(), str(predicted).lower())
        return score / 100.0


class EvaluateExactMatchUseCase:
    """
    Avalia se dois valores são estritamente iguais.
    Pode ser utilizado para numéricos, booleanos ou strings que exigem exatidão.
    """

    def execute(self, expected: Any, predicted: Any) -> float:
        if expected == predicted:
            return 1.0
        return 0.0


class EvaluateListGreedyMatchingUseCase:
    """
    Compara duas listas buscando a melhor combinação possível entre seus itens,
    independentemente da ordem em que foram apresentados.
    """

    def execute(self, expected_list: List[Any], predicted_list: List[Any],
                evaluation_func: Callable[[Any, Any], float]) -> float:
        if not expected_list and not predicted_list:
            return 1.0
        if not expected_list or not predicted_list:
            return 0.0

        total_score = 0.0
        matched_predicted_indices = set()

        for expected_item in expected_list:
            best_score = 0.0
            best_index = -1

            for index, predicted_item in enumerate(predicted_list):
                if index in matched_predicted_indices:
                    continue

                current_score = evaluation_func(expected_item, predicted_item)

                if current_score > best_score:
                    best_score = current_score
                    best_index = index

            if best_index != -1:
                matched_predicted_indices.add(best_index)
                total_score += best_score

        return total_score / len(expected_list)