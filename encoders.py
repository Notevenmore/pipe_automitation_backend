from fastapi.encoders import jsonable_encoder
from typing import Any, List

def custom_jsonable_encoder(
    obj: Any,
    include=None,
    exclude=None,
    by_alias=False,
    exclude_unset=False,
    exclude_defaults=False,
    exclude_none=False,
    custom_encoder=None,
    sqlalchemy_safe=True,
):
    errors: List[Exception] = []
    try:
        if isinstance(obj, list):
            keys = ["ps", "pd", "l", "d", "Q"]
            data = []
            for sublist in obj:
                if isinstance(sublist, (list, tuple)) and len(sublist) == len(keys):
                    data.append(dict(zip(keys, sublist)))
                else:
                    raise ValueError(f"Invalid sublist: {sublist}")
        elif hasattr(obj, "__dict__"):
            data = vars(obj)
        else: 
            data = obj
    except Exception as e:
        errors.append(e)
        try:
            data = obj 
        except Exception as e:
            errors.append(e)
            raise ValueError(f"Failed to encode obj: {obj}. Errors: {errors}") from e

    return jsonable_encoder(
        data,
        include=include,
        exclude=exclude,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )
