from pydantic import BaseModel, Field 

class OriginalText(BaseModel):
    keyword: str = Field(...)
    # keywordCount: str = Field(...)
    specialCharacters: str = Field(...)
    # originalText: str = Field(...)


