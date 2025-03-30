from typing import TypeVar

from pydantic import BaseModel, ValidationError

from skynet_backend.websockets_api.utils.errors import EventDataValidationError


PydanticObjectT = TypeVar("PydanticObjectT", bound=BaseModel)


def validate_and_get_event_data(
    event_data, pydantic_model_type: type[PydanticObjectT]
) -> PydanticObjectT:
    if isinstance(event_data, dict):
        try:
            return pydantic_model_type.model_validate(event_data)
        except ValidationError as validation_error:
            raise EventDataValidationError(str(validation_error)) from validation_error
    else:
        raise EventDataValidationError("Event data must be a JSON object ({ ... })")
