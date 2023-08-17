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


@pytest.fixture(scope="function")
def resource(request):
    with open(Path("tests", "fixtures", request.param), "r") as json_fixture:
        return json.load(json_fixture)


@pytest.mark.parametrize("resource", ["single_resource_with_id.json"], indirect=True)
def test_it_creates_a_container_from_base_model_with_id(resource):
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
    new_resource = DANJAResource.from_basemodel(basemodel_instance)

    schema = new_resource.model_json_schema()

    # Check schema
    assert(schema == resource)

    # Check resource data
    assert(new_resource.resource == basemodel_instance)


@pytest.mark.parametrize("resource", ["single_resource_without_id.json"], indirect=True)
def test_it_creates_a_container_from_base_model_without_id(resource):
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
    new_resource = DANJAResource.from_basemodel(basemodel_instance)

    schema = new_resource.model_json_schema()

    # Check schema
    assert(schema == resource)

    # Check resource data
    assert(new_resource.resource == basemodel_instance)


@pytest.mark.parametrize("resource", ["multiple_resource_with_id.json"], indirect=True)
def test_it_creates_a_container_list_from_base_model_with_id(resource):
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
    new_resources = DANJAResourceList.from_basemodel_list(basemodel_instances)

    schema = new_resources.model_json_schema()

    # Check schema
    assert(schema == resource)

    # Check resource data
    assert(len(new_resources.resources) == len(basemodel_instances))


@pytest.mark.parametrize("resource", ["multiple_resource_without_id.json"], indirect=True)
def test_it_creates_a_container_list_from_base_model_without_id(resource):
    """
    Test that we can create a JSON:API container for a single resource
    from a pydantic BaseModel instance
    """
    # BaseModel including ID
    basemodel_instances = [
        FixtureTestType(
            name="Stuff!",
            description="This is desc!"
        ),
        FixtureTestType(
            name="More Stuff!",
            description="This is more desc!"
        )
    ]

    # Create the JSON:API container
    new_resources = DANJAResourceList.from_basemodel_list(basemodel_instances)

    schema = new_resources.model_json_schema()

    # Check schema
    assert(schema == resource)

    # Check resource data
    assert(len(new_resources.resources) == len(basemodel_instances))
