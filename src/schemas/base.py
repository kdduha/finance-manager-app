from datetime import datetime

from sqlmodel import SQLModel

from src import errors

DELETE_MODEL_RESPONSE = {
    "description": "User successfully deleted",
    "content": {"application/json": {"example": {"message": "string"}}},
}


class BaseSQLModel(SQLModel):

    @staticmethod
    def validate_past_data(date: any, field_name: str) -> None:
        if isinstance(date, datetime):
            # delete info about Time Zone
            date = date.replace(tzinfo=None)
            current_time = datetime.utcnow().replace(tzinfo=None)

            if date > current_time:
                error = errors.ValidationException(
                    errors.ValidationExceptionDetail(
                        loc=["body", field_name],
                        msg="Date should be in the past",
                        type=f"{type(date)}",
                    )
                )
                raise error

    @staticmethod
    def validate_future_date(date: any, field_name: str) -> None:
        if isinstance(date, datetime):
            # delete info about Time Zone
            date = date.replace(tzinfo=None)
            current_time = datetime.utcnow().replace(tzinfo=None)

            if current_time >= date:
                error = errors.ValidationException(
                    errors.ValidationExceptionDetail(
                        loc=["body", field_name],
                        msg="Date should be in the future",
                        type=f"{type(date)}",
                    )
                )
                raise error
