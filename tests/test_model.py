import pytest
from pydantic import ValidationError

from pydanja import DANJAError, DANJASource


def test_error_with_source():
    DANJAError.model_validate({"source": {"pointer": "/"}})
    with pytest.raises(ValidationError) as exc:
        DANJAError(source={"str": DANJASource(pointer="/")}).model_dump()
    errors = exc.value.errors()
    assert len(errors) == 1
    error = errors[0]
    assert error["type"] == "extra_forbidden"
    assert error["loc"] == ("source", "str")
