import pytest
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from app.core.response import Ok, Created, BadRequest, Unauthorized, InternalServerError, Forbidden, NotFound


def test_ok_response():
    response = Ok(data={"id": 1}, message="OK").json()
    assert isinstance(response, JSONResponse)
    assert response.status_code == 200
    assert response.body == b'{"status":"success","message":"OK","data":{"id":1}}'

def test_created_response():
    response = Created(data={"id": 1}).json()
    assert isinstance(response, JSONResponse)
    assert response.status_code == 201
    assert response.body == b'{"status":"success","data":{"id":1}}'

def test_not_found_response():
    with pytest.raises(HTTPException) as exc_info:
        NotFound(message="Not Found").http_exception()

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == {"status":"error","message":"Not Found"}

def test_forbidden_response():
    with pytest.raises(HTTPException) as exc_info:
        Forbidden(message="Forbidden").http_exception()

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == {"status":"error","message":"Forbidden"}

def test_bad_request_response():
    with pytest.raises(HTTPException) as exc_info:
        BadRequest(message="Invalid input", errors={"field": "Invalid value"}).http_exception()

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {"status":"error","message":"Invalid input","errors":{"field":"Invalid value"}}

def test_unauthorized_response():
    with pytest.raises(HTTPException) as exc_info:
        Unauthorized(message="Unauthorized").http_exception()

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {"status":"error","message":"Unauthorized"}

def test_internal_server_error_response():
    with pytest.raises(HTTPException) as exc_info:
        InternalServerError(error="Internal Server Error").http_exception()

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == {"status": "error", "message": "Internal Server Error"}