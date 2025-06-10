from typing import Annotated

from dependency_injector.wiring import Provide
from fastapi import Depends

from src.infrastructure.di import Container

BigQueryClient = Annotated[
    "BigQueryClient", Depends(Provide[Container.database.bigquery_client])
]

ProcessPDPDataUseCase = Annotated[
    "ProcessPDPDataUseCase", Depends(Provide[Container.use_cases.process_pdp_data])
]
