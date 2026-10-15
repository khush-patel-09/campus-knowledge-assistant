from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )
    department: str | None = None
    academic_year: str | None = None
    document_type: str | None = None


class SourceResponse(BaseModel):
    reference: int
    title: str
    page_number: int | None = None
    section_title: str | None = None
    source_url: str | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]