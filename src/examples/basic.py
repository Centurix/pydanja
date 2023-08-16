from typing import Optional, List, TypeVar, Generic
import json
from pydantic import BaseModel, Field
from pydanja import (
    DANJAResource,
    DANJAResourceList,
    DANJALink
)
"""
Create basic resource containers for single and list resources

DANJASingleResource and DANJAResourceList are containers for other BaseModels

Three types of resources and their resultant JSON schema plus data.
"""


class TestType(BaseModel):
    """Basic stuff"""
    testtype_id: Optional[int] = Field(
        alias="id",
        default=None,
        json_schema_extra={
            "resource_id": True
        }
    )
    name: str
    description: str


# From a BaseModel including ID
resource1 = DANJAResource.from_basemodel(TestType(
    id=1,
    name="Stuff!",
    description="This is desc!"
))
resource1.links = {
    "self": DANJALink(href="http://localhost")
}
print(json.dumps(resource1.model_json_schema(), indent=2))
print(resource1.model_dump_json(indent=2))

# Fetch the original resource model via .resource
original = resource1.resource
print(original)


# From a BaseModel without ID
resource2 = DANJAResource.from_basemodel(TestType(
    name="Stuff!",
    description="This is desc!"
))
print(json.dumps(resource2.model_json_schema(), indent=2))
print(resource2.model_dump_json(indent=2))

# From a list of BaseModels
resource3 = DANJAResourceList.from_basemodel_list([
    TestType(id=1, name="One", description="Desc One"),
    TestType(id=2, name="Two", description="Desc Two"),
    TestType(id=3, name="Three", description="Desc Three"),
    TestType(id=4, name="Four", description="Desc Four"),
])
print(json.dumps(resource3.model_json_schema(), indent=2))
print(resource3.model_dump_json(indent=2))

# Fetch the original list of resource models via .resources
originals = resource3.resources
print(originals)
