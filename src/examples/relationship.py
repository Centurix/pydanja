from typing import Optional

from pydantic import BaseModel
from pydantic import Field

from pydanja import DANJARelationship
from pydanja import DANJATopLevel


class Author(BaseModel):
    id: Optional[str] = Field(
        json_schema_extra={
            "resource_id": True
        }
    )
    name: str

    def from_basemodel(self):
        return DANJATopLevel.from_basemodel(self)


class Article(BaseModel):
    id: Optional[str] = Field(
        json_schema_extra={
            "resource_id": True
        }
    )
    title: str
    author: Author

    def from_basemodel(self):
        toplevel = DANJATopLevel.from_basemodel(self)
        toplevel_author = self.author.from_basemodel()
        rel = DANJARelationship.from_danjaresource(toplevel_author)

        # replaces pop key by relationship (
        toplevel.resource.pop('author')
        toplevel.data.relationships = {
            'author': rel
        }

        # set top level resource in included
        toplevel.included = {"author": toplevel_author}
        return toplevel


if __name__ == '__main__':
    author = Author(id='0', name="Shakespeare")
    article = Article(id='0', title="Romeo is dead", author=author)

    toplevel_article = article.from_basemodel()
    print(toplevel_article.model_dump())
