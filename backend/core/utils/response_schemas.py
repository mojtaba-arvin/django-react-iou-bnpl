import copy
from typing import Optional, Type, List
from drf_yasg import openapi
from rest_framework import serializers

error_object_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "code": openapi.Schema(type=openapi.TYPE_INTEGER),
        "message": openapi.Schema(type=openapi.TYPE_STRING),
        "field": openapi.Schema(type=openapi.TYPE_STRING),
        "details": openapi.Schema(type=openapi.TYPE_STRING),
    },
    required=["code", "message"]
)

error_schema_inputs = dict(
    type=openapi.TYPE_OBJECT,
    properties={
        "success": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="False if the operation failed"
        ),
        "message": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Error message"
        ),
        "errors": error_object_schema,
        "data": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="Usually an empty object when an error occurs"
        ),
    },
    required=["success", "message", "errors", "data"],
)
api_error_schema = openapi.Schema(**error_schema_inputs)

pagination_object_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    description="Pagination metadata (optional)",
    properties={
        "total_items": openapi.Schema(type=openapi.TYPE_INTEGER, example=100),
        "total_pages": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
        "current_page": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
        "page_size": openapi.Schema(type=openapi.TYPE_INTEGER, example=10),
        "next": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, example=None),
        "previous": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, example=None),
    },
)


def build_success_response_schema(
        data_schema: Optional[openapi.Schema] = None,
        serializer_class: Optional[Type[serializers.Serializer]] = None,
        many: bool = False,
        include_pagination: bool = False  # Optional flag to include pagination
) -> openapi.Schema:
    """Build a success response schema"""

    # If serializer_class is provided, generate schema based on it
    if serializer_class:
        serializer = serializer_class()
        fields = {
            name: openapi.Schema(type=openapi.TYPE_STRING)
            for name in serializer.get_fields()
        }
        item_schema = openapi.Schema(type=openapi.TYPE_OBJECT, properties=fields)
        data_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=item_schema) if many else item_schema

    elif data_schema is None:
        data_schema = openapi.Schema(type=openapi.TYPE_OBJECT)

    # Include pagination only if specified
    properties = {
        "success": openapi.Schema(
            type=openapi.TYPE_BOOLEAN,
            description="True if the operation was successful"
        ),
        "message": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Success message"
        ),
        "data": data_schema,
        "errors": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=error_object_schema,
            description="Array of error objects (usually empty)"
        ),
    }

    if include_pagination:
        properties["pagination"] = pagination_object_schema

    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=properties,
        required=["success", "message", "data", "errors"]
    )


def build_error_schema(
        messages: List[str] = None,
        description: str = "Error message"
) -> openapi.Schema:
    message_schema_inputs = dict(
        type=openapi.TYPE_STRING,
        description=description,
    )
    if messages:
        message_schema_inputs['enum'] = messages

    new_inputs = copy.deepcopy(error_schema_inputs)
    new_inputs['properties']['message'] = openapi.Schema(**message_schema_inputs)
    return openapi.Schema(**new_inputs)
