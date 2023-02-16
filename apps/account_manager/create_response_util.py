import json

from django.utils.translation import gettext as _
from rest_framework.renderers import BaseRenderer, JSONRenderer

from rest_framework.response import Response


HTTP_CODE_TO_RENDER = {
    "200": "Success",
    "400": "Failed",
    "401": "Authentication Failed",
    "426": "Version Mismatch",
    "429": "Too many requests",
    "500": "Internal server error",
}


def create_response_data(
    status,
    message,
    data=dict(),
    errors=dict()
):
    try:
        if status != 200:
            # empty dict or a string?
            if isinstance(errors, str):
                # standardise errors
                errors = {"non_field_errors": [str(_(errors))]}

            if errors is None or isinstance(errors, dict) and len(errors) == 0:
                errors = {"non_field_errors": [str(_(message))]}

            if (
                isinstance(errors, dict)
                and errors.get("non_field_errors", [""])[0] in []
            ):
                try:
                    for key, values in errors.items():
                        error = [value[:] for value in values]
                    error[:] = [_(x) for x in error]
                    errors = dict(zip(list(errors.keys()), error))
                except Exception as e:
                    pass
            else:
                try:
                    if isinstance(errors, dict):
                        errors = dict(zip(list(errors.keys()), errors.values()))
                except Exception as e:
                    pass

        message = (
            message if isinstance(message, bool) or message is None else _(message)
        )
        return Response(
            {
                "status_code": status,
                "message": message,
                "data": data,
                "errors": errors,
            },
            status=status
        )
    except Exception as e:
        message = (
            message if isinstance(message, bool) or message is None else _(message)
        )
        return Response(
            {
                "status_code": status,
                "message": message,
                "data": data,
                "errors": errors
            },
            status=status
        )


class ApiRenderer(JSONRenderer):

    def render(self, data, accepted_media_type='application/json', renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = {
          "status": "success",
          "code": status_code,
          "data": data,
          "message": None
        }

        if not str(status_code).startswith('2'):
            response["status"] = "error"
            response["data"] = None
            try:
                response["message"] = data["detail"]
            except KeyError:
                response["data"] = data

        return super(ApiRenderer, self).render(response, accepted_media_type, renderer_context)


