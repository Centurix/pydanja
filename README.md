# PyDANJA

[JSON:API](https://jsonapi.org/format/) Suport for [Pydantic](https://docs.pydantic.dev/latest/)

This is a series of classes that can be included into your [Pydantic](https://docs.pydantic.dev/latest/) project that act as a container format for outputting and verifying [JSON:API](https://jsonapi.org/format/) compliant content.

This library makes use of BaseModel generics to contain either a single resource or a list of resources as further BaseModels.

## Installation

`pip install pydanja`

## Requirements

This will support the oldest non-EOL Python (3.8 as of the writing of this document)

## Usage

With pydantic

```
from pydanja import DANJAResource


class TestType(BaseModel):
    # A simple Pydantic BaseModel
    testtype_id: Optional[int] = Field(alias="id", default=None)
    name: str
    description: str

    class Config:
        """
        This is extra configuration to mark which field is to be
        used as the resource ID
        """
        resource_id: str = "testtype_id"


resource = DANJAResource.from_basemodel(TestType(
    id=1,
    name="Stuff!",
    description="This is desc!"
))
print(resource.model_dump_json(indent=2))

# The BaseModel contained resource can be acquired by
contained_resource = resource.data
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
from pydantic import BaseModel, Field
from fastapi import FastAPI
from pydanja import DANJAResource, DANJAResourceList, DANJAError


app = FastAPI()


# Example BaseModel
class TestType(BaseModel):
    # If we use ID, then we must alias it to avoid clashes with Python
    testtype_id: Optional[int] = Field(alias="id", default=None)
    name: str
    description: str

    class Config:
        # Declare the resource ID field name
        resource_id: str = "testtype_id"


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
    return DANJAResourceList.from_basemodel(values)
```

This library supports:

* Single resources (`DANJAResource`)
* Lists of resources (`DANJAResourceList`)
* Error objects (`DANJAErrorList`/`DANJAError`)
* Link objects (`DANJALink`)

There are more examples, including [FastAPI](https://fastapi.tiangolo.com/) code in the `src/examples` directory.


### Future Enhancements

* At the moment, the schema output from FastAPI includes the intermediary objects needed for the heirarchy in JSON:API, these should be suppressed
* The type names in the API output also include the full canonical generic class names and the contained class name, this should reduce to just the contained class name