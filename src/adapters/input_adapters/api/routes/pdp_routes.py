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
        file_path = _validate_and_get_file_path(filename, "download")

        logger.info(f"Serving file: {filename}")
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error downloading file {filename}: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail="Error downloading file") from e


@router.delete("/cleanup/{filename}")
@inject
async def cleanup_excel(filename: str, background_tasks: BackgroundTasks):
    try:
        file_path = _validate_and_get_file_path(filename, "cleanup")

        background_tasks.add_task(delete_file, file_path)

        logger.info(f"Cleanup task scheduled successfully for: {filename}")
        return {"message": "File cleanup scheduled", "filename": filename}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error scheduling cleanup for {filename}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Error scheduling cleanup") from e


def delete_file(file_path: Path):
    try:
        file_size = file_path.stat().st_size / 1024  # KB
        filename = file_path.name

        file_path.unlink()
        logger.info(f"Successfully deleted file: {filename} (Size: {file_size:.2f} KB)")

    except FileNotFoundError:
        logger.warning(f"File already deleted or not found: {file_path}")
    except PermissionError as e:
        logger.error(f"Permission denied deleting file {file_path}: {str(e)}")
    except Exception as e:
        logger.error(
            f"Unexpected error deleting file {file_path}: {str(e)}", exc_info=True
        )


def _validate_and_get_file_path(filename: str, operation: str) -> Path:
    logger.info(f"{operation} request received for file: {filename}")

    if "/" in filename or "\\" in filename:
        logger.warning(f"Invalid filename attempted for {operation}: {filename}")
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = Path("output") / filename

    if not file_path.exists():
        logger.warning(f"File not found for {operation}: {filename}")
        raise HTTPException(status_code=404, detail="File not found")

    file_size = file_path.stat().st_size / 1024
    logger.info(f"File found: {filename} (Size: {file_size:.2f} KB)")

    return file_path
