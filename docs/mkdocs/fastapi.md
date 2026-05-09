# FastAPI

PyDANJA types work well as FastAPI `response_model` / body types: annotate handlers with `DANJAResource[YourModel]` or `DANJAResourceList[YourModel]` so inbound JSON:API payloads are validated.

## Response shaping

Use FastAPI’s model exclusion helpers so empty JSON:API members do not clutter responses, for example `response_model_exclude_none=True` on routes.

## OpenAPI schema cleanup

Large generic models can make OpenAPI noisy. The library provides `danja_openapi` to simplify schema names for DANJA-related components after you build the base OpenAPI dict (see the project README and `src/examples/fastapi.py`).

## Example code

Runnable examples live under `src/examples/` in the repository — start with `fastapi.py` alongside `basic.py` for non-framework usage.
