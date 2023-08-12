from typing import Generic, TypeVar, Optional, Dict, Any, List, Union
from pydantic import BaseModel


__all__ = [
    "DANJASingleResource",
    "DANJAResource",
    "DANJAResourceList",
    "DANJALink",
    "DANJAError",
    "DANJAErrorList"
]


ResourceType = TypeVar("ResourceType", bound=BaseModel)


class DANJASingleResource(BaseModel, Generic[ResourceType]):
    """
    A single resource. The only JSON:API required field is type
    """
    id: Optional[str] = None
    type: str
    lid: Optional[str] = None
    attributes: ResourceType
    relationships: Optional[Dict[str, Any]] = None
    links: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class DANJAResource(BaseModel, Generic[ResourceType]):
    """
    JSONAPI base for a single resource
    """
    data: DANJASingleResource[ResourceType]
    links: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    included: Optional[List[Dict[str, Any]]] = None

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
                resource_name = str(resource.model_config.get(
                    "resource_name",
                    resource.__class__.__name__.lower()
                ))

            if not resource_id:
                """
                No resource ID fields supplied, look for one in the model config
                or failing that if there's
                """
                resource_id = str(resource.model_config.get("resource_id"))
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


class DANJAResourceList(BaseModel, Generic[ResourceType]):
    """
    JSONAPI base for a list of resources
    """
    data: List[DANJASingleResource[ResourceType]]
    links: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    included: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def from_basemodel(
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
                    resource_name = str(resource.model_config.get(
                        "resource_name",
                        resource.__class__.__name__.lower()
                    ))

                if not resource_id:
                    """
                    No resource ID fields supplied, look for one in the model config
                    or failing that if there's
                    """
                    resource_id = str(resource.model_config.get("resource_id"))
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
            for resource in resources:
                values = {
                    "type": resource_name,
                    "lid": None,
                    "attributes": resource
                }
                id_value = object.__getattribute__(resource, resource_id)
                if id_value:
                    values["id"] = str(id_value)
                data.append(DANJASingleResource(**values))

            return cls(data=data)
        except AttributeError:
            raise Exception(
                f"Resource ID field not found in {resource_name}: {resource_id}"
            )


class DANJALink(BaseModel):
    href: str
    rel: Optional[str]
    describedby: Optional[str]
    title: Optional[str]
    type: Optional[str]
    hreflang: Optional[str]
    meta: Optional[Dict[str, Any]]


class DANJAError(BaseModel):
    id: Optional[str]
    links: Optional[Dict[str, Union[str, DANJALink, None]]]
    status: Optional[str]
    code: Optional[str]
    title: Optional[str]
    detail: Optional[str]
    source: Optional[Dict[str, Any]]
    meta: Optional[Dict[str, Any]]


class DANJAErrorList(BaseModel):
    errors: List[DANJAError]
