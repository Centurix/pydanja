from typing import Generic, TypeVar, Optional, Dict, Any, List, Union

from pydantic import BaseModel
from pydantic.networks import AnyUrl

from .openapi import danja_openapi

__all__ = [
    "DANJATopLevel",
    "DANJAResource",
    "DANJALink",
    "DANJAError",
    "DANJAErrorList",
    "danja_openapi"
]

ResourceType = TypeVar("ResourceType")


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


class DANJALink(BaseModel):
    """JSON:API Link"""
    href: Union[str, AnyUrl]
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

    @classmethod
    def from_danjaresource(
            cls,
            resource: Union["DANJATopLevel", "DANJAResource"],
    ) -> "DANJAResourceIdentifier":
        values = {
            "type": resource.data.type,
            "id": resource.data.id,
        }

        return DANJAResourceIdentifier(**values)


class DANJARelationship(BaseModel, ResourceResolver):
    """JSON:API Relationship"""
    links: Optional[Dict[str, Union[str, AnyUrl, DANJALink, None]]] = None
    data: DANJAResourceIdentifier
    meta: Optional[Dict[str, Any]] = None

    @classmethod
    def from_basemodel(
            cls,
            resource: ResourceType,
    ) -> "DANJARelationship":
        try:
            resource_name = cls.resolve_resource_name(resource)
            resource_id = cls.resolve_resource_id(resource)
            if not resource_id:
                raise Exception(f"No fields defined in {resource_name}")

            values = {
                "type": resource_name,
                "id": str(object.__getattribute__(resource, resource_id)),
            }

            return DANJARelationship(data=DANJAResourceIdentifier(**values))
        except AttributeError:
            raise Exception(
                f"Resource ID field not found in {resource_name}: {resource_id}"
            )

    @classmethod
    def from_danjaresource(
            cls,
            resource: Union["DANJATopLevel", "DANJAResource"],
    ) -> "DANJARelationship":
        identifier = DANJAResourceIdentifier.from_danjaresource(resource)
        return DANJARelationship(data=identifier)


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


class DANJAResource(BaseModel, Generic[ResourceType]):
    """A single resource. The only JSON:API required field is type"""
    id: Optional[str] = None
    type: str
    lid: Optional[str] = None
    attributes: ResourceType
    relationships: Optional[Dict[str, DANJARelationship]] = None
    links: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class DANJATopLevel(BaseModel, ResourceResolver, Generic[ResourceType]):
    """JSON:API base for a top level resource"""
    data: Union[DANJAResource[ResourceType], List[DANJAResource[ResourceType]]]
    links: Optional[Dict[str, Union[str, DANJALink, None]]] = None
    meta: Optional[Dict[str, Any]] = None
    included: Optional[List[DANJAResource[ResourceType]]] = None

    @property
    def resource(self) -> Union[ResourceType, List[ResourceType]]:
        if isinstance(self.data, List):
            return [data.attributes for data in self.data]
        return self.data.attributes

    @classmethod
    def from_basemodel(
            cls,
            resource: ResourceType,
            resource_name: Optional[str] = None,
            resource_id: Optional[str] = None
    ) -> "DANJATopLevel":
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
                "attributes": resource.model_dump(by_alias=True)
            }

            id_value = object.__getattribute__(resource, resource_id)
            if id_value:
                values["id"] = str(id_value)

            return cls(data=DANJAResource(**values))
        except AttributeError:
            raise Exception(
                f"Resource ID field not found in {resource_name}: {resource_id}"
            )

    @classmethod
    def from_basemodel_list(
            cls,
            resources: List[ResourceType],
            resource_name: Optional[str] = None,
            resource_id: Optional[str] = None
    ) -> "DANJATopLevel":
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

                data: List[DANJAResource] = []
                for sub_resource in resources:
                    values = {
                        "type": resource_name,
                        "lid": None,
                        "attributes": sub_resource.model_dump(by_alias=True)
                    }
                    id_value = object.__getattribute__(sub_resource, resource_id)
                    if id_value:
                        values["id"] = str(id_value)
                    data.append(DANJAResource(**values))
            else:
                data = []

            return cls(data=data)
        except AttributeError:
            raise Exception(
                f"Resource ID field not found in {resource_name}: {resource_id}"
            )
