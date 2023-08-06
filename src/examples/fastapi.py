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
