![build workflow](https://github.com/Centurix/pydanja/actions/workflows/python-app.yml/badge.svg)
![pypi](https://img.shields.io/pypi/v/pydanja)
![licence](https://img.shields.io/github/license/Centurix/pydanja.svg)
![status](https://img.shields.io/pypi/status/pydanja)
![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)

# PyDANJA

**PyDAN**<sub>tic</sub> **J**<sub>SON</sub>**A**<sub>PI</sub>


[JSON:API (or JSONAPI)](https://jsonapi.org/format/) Suport for [Pydantic](https://docs.pydantic.dev/latest/)

Output [JSONAPI](https://jsonapi.org/format/) from your [FastAPI](https://fastapi.tiangolo.com/) or [PyDantic](https://docs.pydantic.dev/latest/) based application with very little code.

This is a series of classes that can be included into your [Pydantic](https://docs.pydantic.dev/latest/) project that act as a container format for outputting and verifying [JSON:API](https://jsonapi.org/format/) compliant content.

This library makes use of BaseModel generics to contain either a single resource or a list of resources as further BaseModels.

## Installation

`pip install pydanja`

## Requirements

This will support the oldest non-EOL Python (3.9 as of the writing of this document)

## Usage

With pydantic

```
from pydanja import DANJAResource


class TestType(BaseModel):
    """A simple Pydantic BaseModel"""
    # We use an extra resource_id to indicate the ID for JSON:API
    testtype_id: Optional[int] = Field(
        alias="id",
        default=None,
        json_schema_extra={
            "resource_id": True
        }
    )
    name: str
    description: str


resource_container = DANJAResource.from_basemodel(TestType(
    id=1,
    name="Stuff!",
    description="This is desc!"
))
print(resource_container.model_dump_json(indent=2))

# The BaseModel contained resource can be acquired by
resource = resource_container.resource
```

This basic example shows a [Pydantic](https://docs.pydantic.dev/latest/) BaseModel being contained within a `DANJAResource` object. The `model_dump_json` will output [JSON:API](https://jsonapi.org/format/):

```
{
  "data": {
    "id": "1",
    "type": "testtype",
    "lid": null,
    "attributes": {
      "testtype_id": 1,
      "name": "Stuff!",
      "description": "This is desc!"
    },
    "relationships": null,
    "links": null,
    "meta": null
  },
  "links": null,
  "meta": null,
  "included": null
}
```

Note that all [JSON:API](https://jsonapi.org/format/) fields are included in the output of the model dump. If you are using an API framework like [FastAPI](https://fastapi.tiangolo.com/), you use the `response_model_exclude_none` to suppress fields with no values.

### FastAPI example

```
from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict
from fastapi import FastAPI
from pydanja import DANJAResource, DANJAResourceList, DANJAError, danja_openapi
from fastapi.openapi.utils import get_openapi


app = FastAPI()


# Optional: Clear up the OpenAPI documentation by de-cluttering schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="FastAPI",
        version="2.5.0",
        summary="FastAPI",
        description="FastAPI",
        routes=app.routes,
    )

    app.openapi_schema = danja_openapi(openapi_schema)

    return app.openapi_schema

app.openapi = custom_openapi



# Example BaseModel
class TestType(BaseModel):
    # If we use ID, then we must alias it to avoid clashes with Python
    testtype_id: Optional[int] = Field(
        alias="id",
        default=None,
        json_schema_extra={
            "resource_id": True
        }
    )
    name: str
    description: str


@app.post("/", response_model_exclude_none=True)
async def test_func(payload: DANJAResource[TestType]) -> Union[DANJAResource[TestType], DANJAError]:
    """
    payload will be verified correctly for inbound JSON:API content
    The Union includes a reference to the JSON:API error object that this could throw
    """
    res = TestType(
        id=1,
        name="Stuff!",
        description="This is description!"
    )
    return DANJAResource.from_basemodel(res)

@app.get("/", response_model_exclude_none=True)
async def test_get() -> Union[DANJAResourceList[TestType], DANJAError]:
    values = [
        TestType(id=1, name="One", description="Desc One"),
        TestType(id=2, name="Two", description="Desc Two"),
        TestType(id=3, name="Three", description="Desc Three"),
        TestType(id=4, name="Four", description="Desc Four"),
    ]
    return DANJAResourceList.from_basemodel_list(values)
```

This library supports:

* Single resources (`DANJAResource`)
* Lists of resources (`DANJAResourceList`)
* Error objects (`DANJAErrorList`/`DANJAError`)
* Link objects (`DANJALink`)

There are more examples, including [FastAPI](https://fastapi.tiangolo.com/) code in the `src/examples` directory.


### Contributing

This project uses [PDM](https://pdm.fming.dev/latest/) for dependency and virtual environment management.

It aims to use the lowest supported Python version (3.9 as of the writing of this document)

There are currently three build steps in the actions workflow:

* Unit test
* Linting
* Type checking

These can be run through PDM by using:

* `pdm run lint`
* `pdm run test`
* `pdm run typecheck`
* `pdm run all`
