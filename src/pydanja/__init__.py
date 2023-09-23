from typing import Generic, TypeVar, Optional, Dict, Any, List, Union
from pydantic import BaseModel
from .openapi import danja_openapi


__all__ = [
    "DANJASingleResource",
    "DANJAResource",
    "DANJAResourceList",
    "DANJALink",
    "DANJAError",
    "DANJAErrorList",
    "danja_openapi"
]


ResourceType = TypeVar("ResourceType")


class DANJALink(BaseModel):
    """JSON:API Link"""
    href: str
    rel: Optional[str] = None
    describedby: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    hreflang: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class DANJASource(BaseModel):
    """JSON:API Source"""
    pointer: str
    parameter: str
    header: str


class DANJAResourceIdentifier(BaseModel):
    """JSON:API Resource Identifier"""
    type: str
    id: str
    lid: Optional[str] = None


class DANJARelationship(BaseModel):
    """JSON:API Relationship"""
    links: Optional[Dict[str, Union[str, DANJALink, None]]] = None
    data: Optional[Dict[str, Union[DANJAResourceIdentifier, List[DANJAResourceIdentifier], None]]] = None  # noqa: E501
    meta: Optional[Dict[str, Any]] = None


class DANJAError(BaseModel):
    """JSON:API Error object"""
    id: Optional[str] = None
    links: Optional[Dict[str, Union[str, DANJALink, None]]] = None
    status: Optional[str] = None
    code: Optional[str] = None
    title: Optional[str] = None
    detail: Optional[str] = None
    source: Optional[Dict[str, DANJASource]] = None
    meta: Optional[Dict[str, Any]] = None


class DANJAErrorList(BaseModel):
    """JSON:API Error list"""
    errors: List[DANJAError]


class DANJASingleResource(BaseModel, Generic[ResourceType]):
    """A single resource. The only JSON:API required field is type"""
    id: Optional[str] = None
    type: str
    lid: Optional[str] = None
    attributes: ResourceType
    relationships: Optional[Dict[str, DANJARelationship]] = None
    links: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class ResourceResolver():
    @classmethod
    def resolve_resource_name(cls, resource) -> str:
        return str(resource.model_config.get(
            "resource_name",
            resource.__class__.__name__.lower()
        ))

    @classmethod
    def resolve_resource_id(cls, resource) -> Optional[str]:
        for field_name, field in resource.model_fields.items():
            if isinstance(field.json_schema_extra, dict):
                if "resource_id" in field.json_schema_extra:
                    return field_name

        return None



class DANJAResource(BaseModel, ResourceResolver, Generic[ResourceType]):
    """JSON:API base for a single resource"""
    data: DANJASingleResource[ResourceType]
    links: Optional[Dict[str, Union[str, DANJALink, None]]] = None
    meta: Optional[Dict[str, Any]] = None
    included: Optional[List[Dict[str, Any]]] = None

    @property
    def resource(self) -> ResourceType:
        return self.data.attributes

    @classmethod
    def from_basemodel(
        cls,
        resource: ResourceType,
        resource_name: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> "DANJAResource":
        try:
            if not resource_name:
                """
                No resource name supplied, look for one in the model config
                or failing that use the resource class name
                """
                resource_name = cls.resolve_resource_name(resource)

            if not resource_id:
                """
                No resource ID fields supplied, look for one in the model config
                or failing that if there's
                """
                resource_id = cls.resolve_resource_id(resource)
                if not resource_id:
                    raise Exception(f"No fields defined in {resource_name}")

            values = {
                "type": resource_name,
                "lid": None,
                "attributes": resource
            }

            id_value = object.__getattribute__(resource, resource_id)
            if id_value:
                values["id"] = str(id_value)

            return cls(data=DANJASingleResource(**values))
        except AttributeError:
            raise Exception(
                f"Resource ID field not found in {resource_name}: {resource_id}"
            )


class DANJAResourceList(BaseModel, ResourceResolver, Generic[ResourceType]):
    """JSON:API base for a list of resources"""
    data: List[DANJASingleResource[ResourceType]]
    links: Optional[Dict[str, Union[str, DANJALink, None]]] = None
    meta: Optional[Dict[str, Any]] = None
    included: Optional[List[Dict[str, Any]]] = None

    @property
    def resources(self) -> List[ResourceType]:
        return [data.attributes for data in self.data]

    @classmethod
    def from_basemodel_list(
        cls,
        resources: List[ResourceType],
        resource_name: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> "DANJAResourceList":
        try:
            if len(resources) > 0:
                resource = resources[0]

                if not resource_name:
                    """
                    No resource name supplied, look for one in the model config
                    or failing that use the resource class name
                    """
                    resource_name = cls.resolve_resource_name(resource)

                if not resource_id:
                    """
                    No resource ID fields supplied, look for one in the model config
                    or failing that if there's
                    """
                    resource_id = cls.resolve_resource_id(resource)
                    if not resource_id:
                        raise Exception(f"No fields defined in {resource_name}")
            else:
                # If there's no resources to examine, the ID and name must be supplied
                if not resource_name:
                    raise Exception(
                        "No resources included, cannot derive the resource name"
                    )

                if not resource_id:
                    raise Exception(
                        "No resources included, cannot derive the resournce ID"
                    )

            data: List[DANJASingleResource] = []
            for sub_resource in resources:
                values = {
                    "type": resource_name,
                    "lid": None,
                    "attributes": sub_resource
                }
                id_value = object.__getattribute__(sub_resource, resource_id)
                if id_value:
                    values["id"] = str(id_value)
                data.append(DANJASingleResource(**values))

            return cls(data=data)
        except AttributeError:
            raise Exception(
                f"Resource ID field not found in {resource_name}: {resource_id}"
            )
