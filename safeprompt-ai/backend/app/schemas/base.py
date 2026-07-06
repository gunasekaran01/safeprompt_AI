"""
Shared Pydantic base schema.

New schemas (profiles, and future ones) extend CamelCaseModel so their
JSON representation matches JS/frontend naming conventions (camelCase)
while the Python code stays idiomatic snake_case. Existing schemas from
earlier milestones (e.g. schemas/analysis.py) are left as-is to avoid
changing an already-shipped, tested API contract without cause.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
