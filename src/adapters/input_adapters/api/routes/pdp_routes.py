from pathlib import Path

from dependency_injector.wiring import inject
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

from src.adapters.input_adapters.api.dependencies import ProcessPDPDataUseCase
from src.application.dto.pdp_dto import PDPRequestDTO, PDPResponseDTO
from src.shared.exceptions import UseCaseException

router = APIRouter(prefix="/pdp")


@router.post("/process", response_model=PDPResponseDTO)
@inject
async def process_pdp_data(
    request: PDPRequestDTO, use_case: ProcessPDPDataUseCase
) -> PDPResponseDTO:
    try:
        logger.info(f"Processing PDP data from reference date{request.reference_date}")

        result = await use_case.execute(request)

        return result

    except UseCaseException as e:
        logger.error(f"Use case error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/download/{filename}")
async def download_excel(filename: str):
    try:
        if "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        file_path = Path("output") / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail="Error downloading file") from e


@router.delete("/cleanup/{filename}")
@inject
async def cleanup_excel(filename: str, background_tasks: BackgroundTasks):
    try:
        if "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        file_path = Path("output") / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        background_tasks.add_task(delete_file, file_path)

        return {"message": "File cleanup scheduled"}

    except Exception as e:
        logger.error(f"Error scheduling cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Error scheduling cleanup") from e


def delete_file(file_path: Path):
    try:
        file_path.unlink()
        logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
