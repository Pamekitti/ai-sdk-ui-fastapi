import random
import asyncio
from typing import Tuple

from ..schemas.chiller import ScheduleChangeRequest, ScheduleChangeResponse

class ChillerService:
    """Service class for handling chiller operations"""
    
    @staticmethod
    async def update_schedule(request: ScheduleChangeRequest) -> Tuple[ScheduleChangeResponse, int]:
        """
        Update chiller schedule
        
        Args:
            request: The schedule change request
            
        Returns:
            Tuple of (response, status_code)
        """
        # Simulate processing time
        await asyncio.sleep(1)
        
        # Randomly succeed or fail for testing purposes
        if random.random() < 0.8:  # 80% success rate
            return (
                ScheduleChangeResponse(
                    success=True,
                    message=f"Successfully updated schedule for {request.chiller_id.replace('chiller_', 'CH-')}",
                    data={
                        "chiller_id": request.chiller_id,
                        "new_schedule": request.new_schedule
                    }
                ),
                200
            )
        
        # Simulate various error scenarios
        error_cases = [
            ("Schedule conflict detected", 409),
            ("Chiller is currently in maintenance mode", 400),
            ("Invalid time format", 400),
            ("Database connection error", 503)
        ]
        error_msg, status_code = random.choice(error_cases)
        
        return (
            ScheduleChangeResponse(
                success=False,
                message=error_msg
            ),
            status_code
        ) 