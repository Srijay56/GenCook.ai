"""Test the actual SDK request/response boundary without external requests."""

import json

import httpx
import pytest
from openai import OpenAI

from gencook.backend.recipes import RecipeService
from gencook.config import Settings


@pytest.fixture
def service_factory():
    services = []

    def create(content, finish_reason="stop"):
        requests = []

        def handle(request):
            requests.append(json.loads(request.content))
            return httpx.Response(
                200,
                json={
                    "id": "test-completion",
                    "object": "chat.completion",
                    "created": 0,
                    "model": "test-model",
                    "choices": [
                        {
                            "index": 0,
                            "finish_reason": finish_reason,
                            "message": {"role": "assistant", "content": content},
                        }
                    ],
                },
            )

        client = OpenAI(
            api_key="test-only",
            max_retries=0,
            http_client=httpx.Client(transport=httpx.MockTransport(handle)),
        )
        service = RecipeService(Settings(model="test-model"), client=client)
        services.append(service)
        return service, requests

    yield create
    for service in services:
        service.close()


def test_three_ideas_use_configured_model_and_json_mode(service_factory):
    content = json.dumps(
        {
            "recipes": [
                {"title": title, "description": "A quick meal"}
                for title in ["Rice bowl", "Soup", "Stir fry"]
            ]
        }
    )
    service, requests = service_factory(content)
    ideas = service.generate_ideas([" rice ", "beans"])
    assert ideas == [f"{title} — A quick meal" for title in ["Rice bowl", "Soup", "Stir fry"]]
    assert requests[0]["model"] == "test-model"
    assert requests[0]["response_format"] == {"type": "json_object"}
    assert "rice, beans" in requests[0]["messages"][1]["content"]


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        "null",
        "[]",
        "{}",
        '{"recipes": []}',
        '{"recipes": [1, 2, 3]}',
        json.dumps({"recipes": [{"title": "", "description": "Meal"}] * 3}),
        json.dumps({"recipes": [{"title": "Meal", "description": 1}] * 3}),
    ],
)
def test_malformed_ideas_show_a_useful_error(service_factory, content):
    service, _ = service_factory(content)
    with pytest.raises(ValueError, match="expected format"):
        service.generate_ideas(["rice"])


@pytest.mark.parametrize("content,reason", [(None, "stop"), (" ", "stop"), ("Partial", "length")])
def test_empty_or_incomplete_guides_are_rejected(service_factory, content, reason):
    service, _ = service_factory(content, reason)
    with pytest.raises(ValueError):
        service.generate_guide("Soup")


def test_guide_uses_selected_recipe(service_factory):
    service, requests = service_factory("  1. Cook rice.\n2. Add beans.  ")
    assert service.generate_guide("Rice bowl") == "1. Cook rice.\n2. Add beans."
    assert "Rice bowl" in requests[0]["messages"][1]["content"]
    assert "response_format" not in requests[0]


def test_missing_key_is_reported_before_creating_client():
    service = RecipeService(Settings())
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        service.generate_ideas(["rice"])
    assert service._client is None


def test_empty_inputs_never_call_api(service_factory):
    service, requests = service_factory("unused")
    with pytest.raises(ValueError, match="ingredients"):
        service.generate_ideas([" "])
    with pytest.raises(ValueError, match="Select"):
        service.generate_guide("")
    assert requests == []
