
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Let DRF handle known API exceptions first.
    response = exception_handler(exc, context)

    # Unknown/unhandled exceptions remain normal server errors.
    # Do not fabricate a successful or misleading API response.
    if response is None:
        return None

    original_data = response.data
    status_code = response.status_code

    # Map HTTP status codes to stable, machine-readable codes.
    error_codes = {
        400: "validation_error",
        401: "authentication_error",
        403: "permission_denied",
        404: "not_found",
        405: "method_not_allowed",
        406: "not_acceptable",
        409: "conflict",
        429: "throttled",
    }

    code = error_codes.get(status_code, "request_error")

    # Use DRF's detail message where one exists.
    if isinstance(original_data, dict) and "detail" in original_data:
        message = str(original_data["detail"])
        details = None
    elif status_code == 400:
        message = "The request contains invalid data."
        details = original_data
    else:
        message = "The request could not be completed."
        details = original_data

    response.data = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }

    return response
