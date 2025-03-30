from typing import TypeVar

from pydantic import BaseModel, ValidationError

from skynet_backend.websockets_api.utils.errors import EventDataValidationError


PydanticObjectT = TypeVar("PydanticObjectT", bound=BaseModel)


def validate_event_data(
    event_data: str | dict, pydantic_model_type: type[PydanticObjectT]
) -> PydanticObjectT:
    try:
        if isinstance(event_data, dict):
            return pydantic_model_type.model_validate(event_data)
        elif isinstance(event_data, str):
            return pydantic_model_type.model_validate_json(event_data)
    except ValidationError as validation_error:
        raise EventDataValidationError(str(validation_error)) from validation_error
