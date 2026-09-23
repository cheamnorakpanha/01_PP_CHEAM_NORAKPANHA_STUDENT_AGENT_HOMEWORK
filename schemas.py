from pydantic import BaseModel, Field


class SearchCourseInput(BaseModel):
    keyword: str = Field(
        ...,
        description="Keyword to search for a course"
    )


class CheckScheduleInput(BaseModel):
    student_id: int = Field(
        ...,
        gt=0,
        description="Positive student ID"
    )


class RegisterCourseInput(BaseModel):
    student_id: int = Field(
        ...,
        gt=0,
        description="Positive student ID"
    )

    course_id: int = Field(
        ...,
        gt=0,
        description="Positive course ID"
    )
