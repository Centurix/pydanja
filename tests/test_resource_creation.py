import pytest
import json
from typing import Optional
from pathlib import Path
from pydanja import DANJAResource, DANJAResourceList
from pydantic import BaseModel, Field


class FixtureTestType(BaseModel):
    """
    A test type for Pydantic and pydanja
    """
    # If we use ID, then we must alias it to avoid clashes with Python
    fixture_testtype_id: Optional[int] = Field(
        alias="id",
        default=None,
        json_schema_extra={
            "resource_id": True
        }
    )
    name: str
    description: str


@pytest.fixture
def single_resource_with_id():
    with open(
        Path("tests", "fixtures", "single_resource_with_id.json"), "r"
    ) as json_fixture:
        return json.load(json_fixture)


@pytest.fixture
def single_resource_without_id():
    with open(
        Path("tests", "fixtures", "single_resource_without_id.json"), "r"
    ) as json_fixture:
        return json.load(json_fixture)


@pytest.fixture
def multiple_resource_with_id():
    with open(
        Path("tests", "fixtures", "multiple_resource_with_id.json"), "r"
    ) as json_fixture:
        return json.load(json_fixture)


def test_it_creates_a_container_from_base_model_with_id(single_resource_with_id):
    """
    Test that we can create a JSON:API container for a single resource
    from a pydantic BaseModel instance
    """
    # BaseModel including ID
    basemodel_instance = FixtureTestType(
        id=1,
        name="Stuff!",
        description="This is desc!"
    )

    # Create the JSON:API container
    resource = DANJAResource.from_basemodel(basemodel_instance)

    schema = resource.model_json_schema()

    # Check schema
    assert(schema == single_resource_with_id)

    # Check resource data
    assert(resource.data.attributes == basemodel_instance)

def test_it_creates_a_container_from_base_model_without_id(single_resource_without_id):
    """
    Test that we can create a JSON:API container for a single resource
    from a pydantic BaseModel instance
    """
    # BaseModel without ID
    basemodel_instance = FixtureTestType(
        name="Stuff!",
        description="This is desc!"
    )

    # Create the JSON:API container
    resource = DANJAResource.from_basemodel(basemodel_instance)

    schema = resource.model_json_schema()

    # Check schema
    assert(schema == single_resource_without_id)

    # Check resource data
    assert(resource.data.attributes == basemodel_instance)

def test_it_creates_a_container_list_from_base_model_with_id(multiple_resource_with_id):
    """
    Test that we can create a JSON:API container for a single resource
    from a pydantic BaseModel instance
    """
    # BaseModel including ID
    basemodel_instances = [
        FixtureTestType(
            id=1,
            name="Stuff!",
            description="This is desc!"
        ),
        FixtureTestType(
            id=2,
            name="More Stuff!",
            description="This is more desc!"
        )
    ]

    # Create the JSON:API container
    resource = DANJAResourceList.from_basemodel_list(basemodel_instances)

    # schema = resource.model_json_schema()

    # Check schema
    # assert(schema == multiple_resource_with_id)

    # Check resource data
    assert(len(resource.data) == len(basemodel_instances))
