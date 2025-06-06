from datetime import date
from pathlib import Path

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.application.use_cases.process_pdp_data import ProcessPDPDataUseCase
from src.infrastructure.di.container import Container
from src.shared.exceptions import UseCaseException

router = APIRouter(prefix="/pdp")


@router.post("/process", response_model=PDPResponseDTO)
@inject
async def process_pdp_data(
    start_date: date,
    end_date: date,
    include_call_data: bool = True,
    generate_heatmap: bool = True,
    use_case: ProcessPDPDataUseCase = Depends(
        Provide[Container.use_cases.process_pdp_data]
    ),
) -> PDPResponseDTO:
    """
    Process PDP data for a date range

    - **start_date**: Start date for data extraction
    - **end_date**: End date for data extraction
    - **service_type**: Filter by service type (MOVIL/FIJA)
    - **portfolio**: Filter by portfolio
    - **include_call_data**: Whether to enrich with call API data
    - **generate_heatmap**: Whether to generate heatmap in Excel
    """
    try:
        logger.info(f"Processing PDP data from {start_date} to {end_date}")

        # Validate dates
        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="Start date must be before or equal to end date"
            )

        # Create request DTO
        request = PDPRequestDTO(
            start_date=start_date,
            end_date=end_date,
            include_call_data=include_call_data,
            generate_heatmap=generate_heatmap,
        )

        # Execute use case
        result = await use_case.execute(request)

        return result

    except UseCaseException as e:
        logger.error(f"Use case error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/download/{filename}")
async def download_excel(filename: str):
    """Download generated Excel file"""
    try:
        # Validate filename to prevent path traversal
        if "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Construct file path
        file_path = Path("output") / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading file")


@router.delete("/cleanup/{filename}")
@inject
async def cleanup_excel(filename: str, background_tasks: BackgroundTasks):
    """Delete generated Excel file after download"""
    try:
        # Validate filename
        if "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        file_path = Path("output") / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Delete file in background
        background_tasks.add_task(delete_file, file_path)

        return {"message": "File cleanup scheduled"}

    except Exception as e:
        logger.error(f"Error scheduling cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error scheduling cleanup")


def delete_file(file_path: Path):
    """Delete file from filesystem"""
    try:
        file_path.unlink()
        logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
