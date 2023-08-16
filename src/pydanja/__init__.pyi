from typing import Generic, TypeVar, Optional, Dict, Any, List, Union
from pydantic import BaseModel


__all__: List[str]


ResourceType = TypeVar("ResourceType", bound=BaseModel)


class DANJALink(BaseModel):
    href: str
    rel: Optional[str]
    describedby: Optional[str]
    title: Optional[str]
    type: Optional[str]
    hreflang: Optional[str]
    meta: Optional[Dict[str, Any]]


class DANJASource(BaseModel):
    pointer: str
    parameter: str
    header: str


class DANJAResourceIdentifier(BaseModel):
    type: str
    id: str
    lid: Optional[str]


class DANJARelationship(BaseModel):
    links: Optional[Dict[str, Union[str, DANJALink, None]]]
    data: Optional[Dict[str, Union[DANJAResourceIdentifier, List[DANJAResourceIdentifier], None]]]
    meta: Optional[Dict[str, Any]]


class DANJAError(BaseModel):
    id: Optional[str] = None
    links: Optional[Dict[str, Union[str, DANJALink, None]]]
    status: Optional[str]
    code: Optional[str]
    title: Optional[str]
    detail: Optional[str]
    source: Optional[Dict[str, DANJASource]]
    meta: Optional[Dict[str, Any]]


class DANJAErrorList(BaseModel):
    errors: List[DANJAError]


class DANJASingleResource(BaseModel, Generic[ResourceType]):
    id: Optional[str]
    type: str
    lid: Optional[str]
    attributes: ResourceType
    relationships: Optional[Dict[str, DANJARelationship]]
    links: Optional[Dict[str, Any]]
    meta: Optional[Dict[str, Any]]


class DANJAResource(BaseModel, Generic[ResourceType]):
    data: DANJASingleResource[ResourceType]
    links: Optional[Dict[str, Union[str, DANJALink, None]]]
    meta: Optional[Dict[str, Any]]
    included: Optional[List[Dict[str, Any]]]

    @property
    def resource(self) -> ResourceType: ...

    @classmethod
    def from_basemodel(
        cls,
        resource: ResourceType,
        resource_name: Optional[str],
        resource_id: Optional[str]
    ) -> "DANJAResource": ...


class DANJAResourceList(BaseModel, Generic[ResourceType]):
    data: List[DANJASingleResource[ResourceType]]
    links: Optional[Dict[str, Union[str, DANJALink, None]]]
    meta: Optional[Dict[str, Any]]
    included: Optional[List[Dict[str, Any]]]

    @property
    def resources(self) -> List[ResourceType]: ...

    @classmethod
    def from_basemodel_list(
        cls,
        resources: List[ResourceType],
        resource_name: Optional[str],
        resource_id: Optional[str]
    ) -> "DANJAResourceList": ...
