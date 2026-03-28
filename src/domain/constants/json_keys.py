class PrescriptionKeys:
    """
    Armazena as chaves mapeadas no JSON de gabarito para Prescrições Médicas.
    """
    MEDICAMENTOS = "medicamentos"
    NOME = "nome"
    APRESENTACAO_DOSAGEM = "apresentacao_dosagem"
    DOSE = "dose"
    FREQUENCIA = "frequencia"
    DURACAO = "duracao"
    QUANTIDADE_TOTAL = "quantidade_total_prescrita"
    VALOR = "valor"
    UNIDADE = "unidade"
    INTERVALO = "intervalo"
    TEXTO_ORIENTACAO = "texto_orientacao"
    USO_CONTINUO = "uso_continuo"


class PillPackKeys:
    """
    Armazena as chaves mapeadas no JSON de gabarito para Cartelas de Comprimidos.
    """
    NOME_MEDICAMENTO = "nome_medicamento"
    COMPONENTES = "componentes"
    PRINCIPIO_ATIVO = "principio_ativo"
    DOSAGEM_VALOR = "dosagem_valor"
    DOSAGEM_UNIDADE = "dosagem_unidade"
    USO = "uso"
    VIAS_ADMINISTRACAO = "vias_administracao"
    RESTRICOES_IDADE = "restricoes_idade"
    INDICACOES = "indicacoes"
    DATA_VALIDADE = "data_validade"
    LOTE = "lote"