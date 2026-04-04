import os

import streamlit_authenticator as stauth

from src.data.local.answer_key_local_data_source import DuckDBAnswerKeyLocalDataSource
from src.data.providers.token_provider import OIDCTokenProvider
from src.data.database_migrator import DatabaseMigrator
from src.data.local.connection_factory import FileBasedDuckDBConnectionFactory
from src.data.local.execution_local_data_source import DuckDBExecutionLocalDataSource
from src.data.local.sync_local_data_source import DuckDBSyncLocalDataSource
from src.data.queries.query_manager import QueryManager
from src.data.remote.auth_interceptor import OIDCAuth
from src.data.remote.http_client import HttpxHttpClient
from src.data.remote.remote_datasource import ExecutionRemoteDataSource
from src.data.repositories import ExecutionRepository, AnswerKeyRepository
from src.domain.use_cases.answer_key_use_cases import ManageAnswerKeyUseCase, GetAnswerKeysUseCase
from src.domain.use_cases.calculate_prescription_accuracy_use_case import CalculatePrescriptionAccuracyUseCase
from src.domain.use_cases.calculate_pill_pack_accuracy_use_case import CalculatePillPackAccuracyUseCase
from src.domain.use_cases.database_migrations_use_case import RunDatabaseMigrationsUseCase
from src.domain.use_cases.evaluation.calculate_processing_time_use_case import CalculateProcessingTimeUseCase
from src.domain.use_cases.evaluation.evaluate_single_prescription_use_case import EvaluateSinglePrescriptionUseCase
from src.domain.use_cases.evaluation.evaluators import (
    EvaluateTextSimilarityUseCase,
    EvaluateExactMatchUseCase,
    EvaluateListGreedyMatchingUseCase
)
from src.domain.use_cases.get_evaluated_pill_packs_use_case import GetEvaluatedPillPacksUseCase
from src.domain.use_cases.get_evaluated_prescriptions_use_case import GetEvaluatedPrescriptionsUseCase
from src.domain.use_cases.get_image_use_case import GetImageUseCase
from src.domain.use_cases.get_pill_packs_analytics_use_case import GetPillPacksAnalyticsUseCase
from src.domain.use_cases.get_prescriptions_analytics_use_case import GetPrescriptionsAnalyticsUseCase
from src.domain.use_cases.sync_executions_use_case import SyncExecutionsUseCase
from src.presentation.auth.auth_manager import StreamlitAuthManager
from src.presentation.view_models.answer_keys_view_model import AnswerKeysViewModel
from src.presentation.view_models.pill_packs_analytics_view_model import PillPacksAnalyticsViewModel
from src.presentation.view_models.prescriptions_analytics_view_model import PrescriptionsAnalyticsViewModel
from src.presentation.view_models.prescriptions_view_model import PrescriptionsViewModel
from src.presentation.view_models.pill_packs_view_model import PillPacksViewModel
from dependency_injector import containers, providers

def _build_auth_credentials() -> dict:
    """
    Constrói o dicionário de credenciais a partir das variáveis de ambiente.
    """
    auth_username = os.getenv("AUTH_USERNAME", "admin")
    auth_password = os.getenv("AUTH_PASSWORD", "admin")

    hashed_password = stauth.Hasher([auth_password]).generate()[0]

    return {
        "usernames": {
            auth_username: {
                "email": "admin@example.com",
                "name": "Administrador",
                "password": hashed_password
            }
        }
    }

class ApplicationContainer(containers.DeclarativeContainer):
    """
    Container de injeção de dependências da aplicação.
    """

    config = providers.Configuration()

    connection_factory = providers.Singleton(
        FileBasedDuckDBConnectionFactory,
        db_path=config.db_path
    )

    query_manager = providers.Singleton(
        QueryManager,
        queries_dir=config.queries_dir
    )

    migrator = providers.Factory(
        DatabaseMigrator,
        connection_factory=connection_factory,
        migrations_dir=config.migrations_dir,
        query_manager=query_manager
    )

    run_database_migrations_use_case = providers.Factory(
        RunDatabaseMigrationsUseCase,
        migrator=migrator
    )

    token_provider = providers.Factory(
        OIDCTokenProvider,
        audience=config.oidc_audience
    )

    auth_interceptor = providers.Factory(
        OIDCAuth,
        token_provider=token_provider
    )

    http_client = providers.Singleton(HttpxHttpClient)

    text_evaluator = providers.Singleton(EvaluateTextSimilarityUseCase)
    exact_evaluator = providers.Singleton(EvaluateExactMatchUseCase)
    list_evaluator = providers.Singleton(EvaluateListGreedyMatchingUseCase)

    prescription_sync_local_ds = providers.Factory(
        DuckDBSyncLocalDataSource,
        connection_factory=connection_factory,
        query_manager=query_manager,
        execution_type="prescription"
    )

    prescription_execution_local_ds = providers.Factory(
        DuckDBExecutionLocalDataSource,
        connection_factory=connection_factory,
        query_manager=query_manager,
        execution_type="prescription"
    )

    answer_key_local_ds = providers.Factory(
        DuckDBAnswerKeyLocalDataSource,
        connection_factory=connection_factory,
        query_manager=query_manager
    )

    prescription_remote_ds = providers.Factory(
        ExecutionRemoteDataSource,
        http_client=http_client,
        base_url=config.api_base_url,
        auth_interceptor=auth_interceptor,
        execution_context="prescription"
    )

    prescription_repository = providers.Factory(
        ExecutionRepository,
        sync_local_ds=prescription_sync_local_ds,
        execution_local_ds=prescription_execution_local_ds,
        remote_ds=prescription_remote_ds
    )

    answer_key_repository = providers.Factory(
        AnswerKeyRepository,
        local_ds=answer_key_local_ds
    )

    pill_pack_sync_local_ds = providers.Factory(
        DuckDBSyncLocalDataSource,
        connection_factory=connection_factory,
        query_manager=query_manager,
        execution_type="pillpack"
    )

    pill_pack_execution_local_ds = providers.Factory(
        DuckDBExecutionLocalDataSource,
        connection_factory=connection_factory,
        query_manager=query_manager,
        execution_type="pillpack"
    )

    pill_pack_remote_ds = providers.Factory(
        ExecutionRemoteDataSource,
        http_client=http_client,
        base_url=config.api_base_url,
        auth_interceptor=auth_interceptor,
        execution_context="pillpack"
    )

    pill_pack_repository = providers.Factory(
        ExecutionRepository,
        sync_local_ds=pill_pack_sync_local_ds,
        execution_local_ds=pill_pack_execution_local_ds,
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
        answer_key_repository=answer_key_repository,
        single_evaluator=evaluate_single_prescription_use_case
    )

    calculate_pill_pack_accuracy_use_case = providers.Factory(
        CalculatePillPackAccuracyUseCase,
        repository=pill_pack_repository,
        answer_key_repository=answer_key_repository,
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

    get_evaluated_prescriptions_use_case = providers.Factory(
        GetEvaluatedPrescriptionsUseCase,
        repository=prescription_repository,
        answer_key_repository=answer_key_repository,
        single_evaluator=evaluate_single_prescription_use_case
    )

    get_evaluated_pill_packs_use_case = providers.Factory(
        GetEvaluatedPillPacksUseCase,
        repository=pill_pack_repository,
        answer_key_repository=answer_key_repository,
        accuracy_use_case=calculate_pill_pack_accuracy_use_case
    )

    get_prescriptions_analytics_use_case = providers.Factory(
        GetPrescriptionsAnalyticsUseCase,
        repository=prescription_repository,
        single_accuracy_use_case=evaluate_single_prescription_use_case,
        answer_key_repository=answer_key_repository
    )

    get_pill_packs_analytics_use_case = providers.Factory(
        GetPillPacksAnalyticsUseCase,
        repository=pill_pack_repository,
        accuracy_use_case=calculate_pill_pack_accuracy_use_case,
        answer_key_repository=answer_key_repository
    )

    manage_answer_key_use_case = providers.Factory(
        ManageAnswerKeyUseCase,
        repository=answer_key_repository
    )

    get_answer_keys_use_case = providers.Factory(
        GetAnswerKeysUseCase,
        repository=answer_key_repository
    )

    prescriptions_view_model = providers.Factory(
        PrescriptionsViewModel,
        repository=prescription_repository,
        sync_use_case=sync_prescription_executions_use_case,
        accuracy_use_case=calculate_prescription_accuracy_use_case,
        calc_time_use_case=calculate_processing_time_use_case,
        get_image_use_case=get_image_use_case,
        get_evaluated_use_case=get_evaluated_prescriptions_use_case
    )

    pill_packs_view_model = providers.Factory(
        PillPacksViewModel,
        repository=pill_pack_repository,
        sync_use_case=sync_pill_pack_executions_use_case,
        accuracy_use_case=calculate_pill_pack_accuracy_use_case,
        calc_time_use_case=calculate_processing_time_use_case,
        get_image_use_case=get_image_use_case,
        get_evaluated_use_case=get_evaluated_pill_packs_use_case
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

    answer_keys_view_model = providers.Factory(
        AnswerKeysViewModel,
        manage_use_case=manage_answer_key_use_case,
        get_use_case=get_answer_keys_use_case,
        prescription_repository=prescription_repository,
        pill_pack_repository=pill_pack_repository,
        get_image_use_case=get_image_use_case
    )

    auth_manager = providers.Factory(
        StreamlitAuthManager,
        credentials=_build_auth_credentials(),
        cookie_name=os.getenv("AUTH_COOKIE_NAME", "dashboard_cookie"),
        cookie_key=os.getenv("AUTH_COOKIE_KEY", "dashboard_key"),
        cookie_expiry_days=30
    )