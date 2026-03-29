# src/di/container.py
from dependency_injector import containers, providers

from src.data.database_migrator import DatabaseMigrator
from src.data.file.file_reader import LocalFileReader
from src.data.local.local_data_source import PrescriptionLocalDataSource, PillPackLocalDataSource
from src.data.remote.http_client import HttpxHttpClient
from src.data.remote.remote_datasource import PrescriptionRemoteDataSource, PillPackRemoteDataSource
from src.data.repositories import ExecutionRepository
from src.domain.calculate_prescription_accuracy_use_case import CalculatePrescriptionAccuracyUseCase
from src.domain.use_cases.calculate_pill_pack_accuracy_use_case import CalculatePillPackAccuracyUseCase
from src.domain.use_cases.database_migrations_use_case import RunDatabaseMigrationsUseCase
from src.domain.use_cases.evaluation.calculate_processing_time_use_case import CalculateProcessingTimeUseCase
from src.domain.use_cases.evaluation.evaluate_single_prescription_use_case import EvaluateSinglePrescriptionUseCase
from src.domain.use_cases.evaluation.evaluators import (
    EvaluateTextSimilarityUseCase,
    EvaluateExactMatchUseCase,
    EvaluateListGreedyMatchingUseCase
)
from src.domain.use_cases.get_image_use_case import GetImageUseCase
from src.domain.use_cases.get_pill_packs_analytics_use_case import GetPillPacksAnalyticsUseCase
from src.domain.use_cases.get_prescriptions_analytics_use_case import GetPrescriptionsAnalyticsUseCase
from src.domain.use_cases.sync_executions_use_case import SyncExecutionsUseCase
from src.presentation.view_models.pill_packs_analytics_view_model import PillPacksAnalyticsViewModel
from src.presentation.view_models.prescriptions_analytics_view_model import PrescriptionsAnalyticsViewModel
from src.presentation.view_models.prescriptions_view_model import PrescriptionsViewModel
from src.presentation.view_models.pill_packs_view_model import PillPacksViewModel


class ApplicationContainer(containers.DeclarativeContainer):
    """
    Container de injeção de dependências da aplicação.
    """

    config = providers.Configuration()

    migrator = providers.Factory(
        DatabaseMigrator,
        db_path=config.db_path
    )

    run_database_migrations_use_case = providers.Factory(
        RunDatabaseMigrationsUseCase,
        migrator=migrator
    )

    http_client = providers.Singleton(HttpxHttpClient)
    file_reader = providers.Singleton(LocalFileReader)

    text_evaluator = providers.Singleton(EvaluateTextSimilarityUseCase)
    exact_evaluator = providers.Singleton(EvaluateExactMatchUseCase)
    list_evaluator = providers.Singleton(EvaluateListGreedyMatchingUseCase)

    prescription_local_ds = providers.Factory(
        PrescriptionLocalDataSource,
        db_path=config.db_path
    )

    prescription_remote_ds = providers.Factory(
        PrescriptionRemoteDataSource,
        http_client=http_client,
        base_url=config.api_base_url,
        audience=config.oidc_audience
    )

    prescription_repository = providers.Factory(
        ExecutionRepository,
        local_ds=prescription_local_ds,
        remote_ds=prescription_remote_ds
    )

    pill_pack_local_ds = providers.Factory(
        PillPackLocalDataSource,
        db_path=config.db_path
    )

    pill_pack_remote_ds = providers.Factory(
        PillPackRemoteDataSource,
        http_client=http_client,
        base_url=config.api_base_url,
        audience=config.oidc_audience
    )

    pill_pack_repository = providers.Factory(
        ExecutionRepository,
        local_ds=pill_pack_local_ds,
        remote_ds=pill_pack_remote_ds
    )

    sync_prescription_executions_use_case = providers.Factory(
        SyncExecutionsUseCase,
        repository=prescription_repository
    )

    sync_pill_pack_executions_use_case = providers.Factory(
        SyncExecutionsUseCase,
        repository=pill_pack_repository
    )

    evaluate_single_prescription_use_case = providers.Factory(
        EvaluateSinglePrescriptionUseCase,
        text_evaluator=text_evaluator,
        exact_evaluator=exact_evaluator,
        list_evaluator=list_evaluator
    )

    calculate_prescription_accuracy_use_case = providers.Factory(
        CalculatePrescriptionAccuracyUseCase,
        repository=prescription_repository,
        file_reader=file_reader,
        answer_key_path=config.prescription_answer_key_path,
        single_evaluator=evaluate_single_prescription_use_case
    )

    calculate_pill_pack_accuracy_use_case = providers.Factory(
        CalculatePillPackAccuracyUseCase,
        repository=pill_pack_repository,
        file_reader=file_reader,
        answer_key_path=config.pill_pack_answer_key_path,
        text_evaluator=text_evaluator,
        exact_evaluator=exact_evaluator,
        list_evaluator=list_evaluator
    )

    calculate_processing_time_use_case = providers.Factory(
        CalculateProcessingTimeUseCase
    )

    get_image_use_case = providers.Factory(
        GetImageUseCase,
        prescription_repository=prescription_repository,
        pill_pack_repository=pill_pack_repository
    )

    prescriptions_view_model = providers.Factory(
        PrescriptionsViewModel,
        repository=prescription_repository,
        sync_use_case=sync_prescription_executions_use_case,
        accuracy_use_case=calculate_prescription_accuracy_use_case,
        calc_time_use_case=calculate_processing_time_use_case,
        get_image_use_case=get_image_use_case,
        single_accuracy_use_case=evaluate_single_prescription_use_case,
        answer_key_path=config.prescription_answer_key_path
    )

    pill_packs_view_model = providers.Factory(
        PillPacksViewModel,
        repository=pill_pack_repository,
        sync_use_case=sync_pill_pack_executions_use_case,
        accuracy_use_case=calculate_pill_pack_accuracy_use_case,
        calc_time_use_case=calculate_processing_time_use_case,
        get_image_use_case=get_image_use_case,
        answer_key_path=config.pill_pack_answer_key_path
    )

    get_prescriptions_analytics_use_case = providers.Factory(
        GetPrescriptionsAnalyticsUseCase,
        repository=prescription_repository,
        single_accuracy_use_case=evaluate_single_prescription_use_case,
        answer_key_path=config.prescription_answer_key_path
    )

    get_pill_packs_analytics_use_case = providers.Factory(
        GetPillPacksAnalyticsUseCase,
        repository=pill_pack_repository,
        accuracy_use_case=calculate_pill_pack_accuracy_use_case,
        answer_key_path=config.pill_pack_answer_key_path
    )

    prescriptions_analytics_view_model = providers.Factory(
        PrescriptionsAnalyticsViewModel,
        analytics_use_case=get_prescriptions_analytics_use_case,
        repository=prescription_repository
    )

    pill_packs_analytics_view_model = providers.Factory(
        PillPacksAnalyticsViewModel,
        analytics_use_case=get_pill_packs_analytics_use_case,
        repository=pill_pack_repository
    )