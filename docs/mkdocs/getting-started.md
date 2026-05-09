# Getting started

## Installation

```bash
pip install pydanja
```

Requires **Python 3.10+** and **Pydantic v2** (see `pyproject.toml` on the repository for the declared minimum versions).

## Minimal example

Define a Pydantic model, mark which field should map to the JSON:API resource id (via `json_schema_extra`), then wrap it with `DANJAResource`:

```python
from typing import Optional

from pydantic import BaseModel, Field
from pydanja import DANJAResource


class Article(BaseModel):
    article_id: Optional[int] = Field(
        alias="id",
        default=None,
        json_schema_extra={"resource_id": True},
    )
    title: str


doc = DANJAResource.from_basemodel(
    Article(id=1, title="Hello JSON:API"),
)
print(doc.model_dump_json(indent=2))
```

You can read the wrapped model back via `doc.resource`.

## Lists

Use `DANJAResourceList.from_basemodel_list([...])` for collection documents. Access inner models with `.resources`.

## Related reading

- [API reference](api-reference.md) — all exported types and `danja_openapi`
- [FastAPI](fastapi.md) — response models and OpenAPI helpers
