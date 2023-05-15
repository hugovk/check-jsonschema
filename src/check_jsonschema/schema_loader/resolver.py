from __future__ import annotations

import pathlib
import typing as t
import urllib.parse

import referencing
import requests
from referencing.jsonschema import DRAFT202012

from ..parsers import ParserSet
from ..utils import filename2path


def make_reference_registry(
    parsers: ParserSet, schema_uri: str | None, schema: dict
) -> referencing.Registry:
    schema_resource = referencing.Resource.from_contents(
        schema, default_specification=DRAFT202012
    )
    registry = referencing.Registry(
        retrieve=create_retrieve_callable(parsers, schema_uri)
    ).with_resource(schema_uri, schema_resource)

    id_attribute = schema.get("$id")
    if id_attribute is not None:
        registry = registry.with_resource(id_attribute, schema_resource)

    return registry


def create_retrieve_callable(
    parser_set: ParserSet, schema_uri: str | None
) -> t.Callable[[str], referencing.Resource]:
    def get_local_file(uri: str):
        path = pathlib.Path(uri)
        if not path.is_absolute():
            if schema_uri is None:
                raise referencing.exceptions.Unretrievable(
                    f"Cannot retrieve schema reference data for '{uri}' from "
                    "local filesystem. "
                    "The path appears relative, but there is no known local base path."
                )
            schema_path = filename2path(schema_uri)
            path = schema_path.parent / path
        return parser_set.parse_file(path, "json")

    def retrieve_reference(uri: str) -> referencing.Resource:
        scheme = urllib.parse.urlsplit(uri).scheme
        if scheme in ("http", "https"):
            data = requests.get(uri, stream=True)
            parsed_object = parser_set.parse_data_with_path(data.raw, uri, "json")
        else:
            parsed_object = get_local_file(uri)

        return referencing.Resource.from_contents(
            parsed_object, default_specification=DRAFT202012
        )

    return retrieve_reference
