from typing import TypeVar

from pydantic import BaseModel, ValidationError

from skynet_backend.websockets_api.utils.errors import EventDataValidationError


PydanticObjectT = TypeVar("PydanticObjectT", bound=BaseModel)


def validate_event_data(
    raw_data: str, pydantic_model_type: type[PydanticObjectT]
) -> PydanticObjectT:
    try:
        return pydantic_model_type.model_validate_json(raw_data)
    except ValidationError as validation_error:
        raise EventDataValidationError(str(validation_error)) from validation_error
