from drf_yasg import openapi

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

api_error_schema = openapi.Schema(
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


def build_success_response_schema(data_schema=None, serializer_class=None):
    """Build a success response schema"""
    if serializer_class:
        serializer = serializer_class()
        data_schema = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                name: openapi.Schema(type=openapi.TYPE_STRING)
                for name in serializer.get_fields()
            }
        )
    elif data_schema is None:
        data_schema = openapi.Schema(type=openapi.TYPE_OBJECT)

    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
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
            "pagination": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="Pagination metadata (optional)",
                additional_properties=True
            )
        },
        required=["success", "message", "data", "errors"]
    )