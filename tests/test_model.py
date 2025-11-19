from typing import Optional, Union

import pytest
from pydantic import ValidationError

from pydanja import DANJAError, DANJARelationship, DANJAResourceIdentifier, DANJASource


def test_error_with_source():
    DANJAError.model_validate({"source": {"pointer": "/"}})
    with pytest.raises(ValidationError) as exc:
        DANJAError(source={"str": DANJASource(pointer="/")}).model_dump()
    errors = exc.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ("source", "str")


@pytest.mark.parametrize(
    "data",
    [
        None,
        [],
        [DANJAResourceIdentifier(type="type", id="id"), DANJAResourceIdentifier(type="type2", id="id2")],
        DANJAResourceIdentifier(type="type3", id="id3"),
    ],
)
def test_relationship_data_good(data: Optional[Union[list[DANJAResourceIdentifier], DANJAResourceIdentifier]]) -> None:
    """Validation passes on correct values."""
    DANJARelationship.model_validate({"data": data})
