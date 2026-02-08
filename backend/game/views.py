from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import town
from . import db


def _require_user(request):
    town.ensure_schema()
    user_id, created = town.get_or_create_user(request.session)
    return user_id, created


@api_view(["GET"])
@ensure_csrf_cookie
def get_or_create_user(request):
    user_id, created = _require_user(request)
    data = town.user_data(user_id)
    if not data:
        return Response({"error_code": "user_lookup_failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return Response(data, status=code)


@api_view(["POST"])
def add_points(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return Response({"error_code": "no_session"}, status=status.HTTP_401_UNAUTHORIZED)

    amount = request.data.get("amount", 1)
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return Response({"error_code": "amount_not_integer"}, status=status.HTTP_400_BAD_REQUEST)

    if amount < 1:
        return Response({"error_code": "amount_must_be_positive"}, status=status.HTTP_400_BAD_REQUEST)

    town.ensure_schema()
    rows = db.execute("UPDATE players SET points = points + %s WHERE user_id = %s", [amount, user_id])
    if rows == 0:
        return Response({"error_code": "user_not_found"}, status=status.HTTP_404_NOT_FOUND)

    data = town.user_data(user_id)
    return Response(data)


@api_view(["GET"])
@ensure_csrf_cookie
def get_town(request):
    user_id, _ = _require_user(request)
    snapshot = town.get_town_snapshot(user_id)
    return Response(snapshot)


@api_view(["POST"])
def trigger_town_event(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return Response({"error_code": "no_session"}, status=status.HTTP_401_UNAUTHORIZED)

    event_id = request.data.get("event_id")
    payload = request.data.get("payload") or {}
    version = request.data.get("version")

    if not event_id:
        return Response({"error_code": "event_id_required"}, status=status.HTTP_400_BAD_REQUEST)

    town.ensure_schema()
    http_status, body = town.apply_event(user_id, event_id, payload, version)
    return Response(body, status=http_status)
