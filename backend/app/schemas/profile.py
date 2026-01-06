from pydantic import BaseModel, Field

class ProfileSetupRequest(BaseModel):
    cf_handle: str = Field(..., min_length=2, max_length=30)
