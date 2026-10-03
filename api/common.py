from fastapi import HTTPException

from dataset_manager import DatasetError


def http_error(exc: DatasetError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))
