from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..schemas.chiller import ScheduleChangeRequest, ScheduleChangeResponse
from ..services.chiller import ChillerService

router = APIRouter()

@router.post("/chiller_sequence_schedule_change")
async def change_chiller_schedule(request: ScheduleChangeRequest) -> ScheduleChangeResponse:
    """
    Endpoint to handle chiller schedule changes with multiple time slots
    """
    try:
        response, status_code = await ChillerService.update_schedule(request)
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump()
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ScheduleChangeResponse(
                success=False,
                message="An unexpected error occurred"
            ).model_dump()
        ) 