from typing import Any
import dpath


def danja_openapi(openapi_schema: dict[str, Any]) -> dict[str, Any]:
    """
    This is an optional function that will assist in de-cluttering the OpenAPI
    schema space. This function will de-reference and flatten a lot of the
    DANJA namespace while leaving non-DANJA classes alone.
    """
    
    # Get all referenced schemas
    ref_schemas = set([
        result[1][21:]
        for result in dpath.search(openapi_schema, "paths/**/$ref", yielded=True)
    ])

    # Resolve all schema references
    ex_schemas = {}
    for key, value in openapi_schema.get("components", {}).get("schemas", {}).items():
        # Flatten and add to the schemas
        for result in dpath.search(value, "/**/$ref", yielded=True):
            parent, _, _ = result[0].rpartition("/")
            dpath.set(value, parent, dpath.get(openapi_schema, result[1][1:]))
        
        if key in ref_schemas:
            ex_schemas[key] = value

    # Rename the DANJA objects
    # DANJAErrorList -> Error_List
    # DANJAResourceList_model -> model_List
    # DANJAResource_model -> model
    rn_schemas = {}
    for key in ex_schemas:
        old_key = f"#/components/schemas/{key}"
        # Find the key in the paths and rename the key and reference
        if key.startswith("DANJAResource_"):
            new_key = key.replace("DANJAResource_", "")
            # Find all path references to the old key
            for result in dpath.search(
                openapi_schema,
                "paths|**|$ref",
                yielded=True,
                separator="|"
            ):
                if result[1] == old_key:
                    # Rename to the new key
                    dpath.set(
                        openapi_schema,
                        result[0],
                        f"#/components/schemas/{new_key[:-1]}",
                        separator="|"
                    )

            rn_schemas[new_key[:-1]] = ex_schemas[key]
        elif key.startswith("DANJAResourceList_"):
            new_key = key.replace("DANJAResourceList_", "")
            # Find all path references to the old key
            for result in dpath.search(
                openapi_schema,
                "paths|**|$ref",
                yielded=True,
                separator="|"
            ):
                if result[1] == old_key:
                    # Rename to the new key
                    dpath.set(
                        openapi_schema,
                        result[0],
                        f"#/components/schemas/{new_key}List",
                        separator="|"
                    )

            rn_schemas[f"{new_key}List"] = ex_schemas[key]
        elif key == "DANJAErrorList":
            new_key = "Error_List"
            # Find all path references to the old key
            for result in dpath.search(
                openapi_schema,
                "paths|**|$ref",
                yielded=True,
                separator="|"
            ):
                if result[1] == old_key:
                    # Rename to the new key
                    dpath.set(
                        openapi_schema,
                        result[0],
                        f"#/components/schemas/{new_key}",
                        separator="|"
                    )

            rn_schemas[new_key] = ex_schemas[key]
        else:
            # Don't rename
            rn_schemas[key] = ex_schemas[key]

    openapi_schema["components"]["schemas"] = rn_schemas

    return openapi_schema
