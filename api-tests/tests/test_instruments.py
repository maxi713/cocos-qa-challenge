import pytest
from assertions.instrument_assertions import (
    assert_instruments_list_schema,
    assert_unique_field,
)


@pytest.mark.smoke
def test_get_instruments_returns_a_non_empty_list(instruments_service):
    response = instruments_service.get_instruments()

    assert response.status_code == 200
    assert isinstance(response.body, list)
    assert len(response.body) > 0


@pytest.mark.regression
def test_each_instrument_matches_schema(instruments_service):
    response = instruments_service.get_instruments()

    assert response.status_code == 200
    assert_instruments_list_schema(response.body)


@pytest.mark.regression
def test_instrument_tickers_are_unique(instruments_service):
    response = instruments_service.get_instruments()

    assert_unique_field(response.body, "ticker")


@pytest.mark.regression
def test_instrument_ids_are_unique(instruments_service):
    response = instruments_service.get_instruments()

    assert_unique_field(response.body, "id")


@pytest.mark.negative
def test_get_instruments_without_bugs_tier_header(instruments_service):
    response = instruments_service.get_instruments(headers={"X-Enable-Bugs": None})

    assert response.status_code == 400


@pytest.mark.negative
def test_get_instruments_with_invalid_bugs_tier_header(instruments_service):
    response = instruments_service.get_instruments(
        headers={"X-Enable-Bugs": "nightmare"}
    )

    assert response.status_code == 400


@pytest.mark.regression
@pytest.mark.parametrize("tier", ["off", "OFF", "Off", "oFf"])
def test_bugs_tier_header_is_case_insensitive(instruments_service, tier):
    response = instruments_service.get_instruments(headers={"X-Enable-Bugs": tier})

    assert response.status_code == 200


@pytest.mark.regression
def test_get_instruments_does_not_require_candidate_id(instruments_service):
    response = instruments_service.get_instruments(headers={"X-Candidate-Id": None})

    assert response.status_code == 200


@pytest.mark.regression
def test_search_result_matches_the_instrument_in_the_full_list(instruments_service):
    all_instruments = instruments_service.get_instruments().body
    target = all_instruments[0]

    search_response = instruments_service.search(target["ticker"])

    assert search_response.status_code == 200
    matches = [i for i in search_response.body if i["ticker"] == target["ticker"]]
    assert len(matches) == 1
    assert matches[0] == target


@pytest.mark.negative
def test_unsupported_method_on_instruments(api_client):
    response = api_client.post("/instruments")

    assert response.status_code == 404


@pytest.mark.regression
def test_instruments_response_content_type(instruments_service):
    response = instruments_service.get_instruments()

    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.regression
def test_get_specific_ticker(instruments_service):
    response_instruments = instruments_service.get_instruments()
    target = response_instruments.body[0]
    response = instruments_service.search(target["ticker"])

    assert response.status_code == 200
    assert_instruments_list_schema(response.body)
    assert len(response.body) == 1
    assert response.body[0] == target


@pytest.mark.regression
def test_get_instrument_with_lowercase(instruments_service):
    response_instruments = instruments_service.get_instruments()
    response = instruments_service.search(
        response_instruments.body[0]["ticker"].lower()
    )

    assert response.status_code == 200
    assert response_instruments.body[0]["ticker"] == response.body[0]["ticker"]


@pytest.mark.regression
def test_get_instrument_with_partial_ticker(instruments_service):
    response_instruments = instruments_service.get_instruments()
    ticker = response_instruments.body[0]["ticker"]
    partial_ticker = [ticker[i : i + 2] for i in range(len(ticker) - 1)]

    for t in partial_ticker:
        response = instruments_service.search(t)
        assert response.status_code == 200
        assert len(response.body) > 0


@pytest.mark.regression
def test_get_instrument_with_name(instruments_service):
    response_instruments = instruments_service.get_instruments()
    response = instruments_service.search(response_instruments.body[0]["name"])

    assert response.status_code == 200
    assert response.body == []


@pytest.mark.regression
def test_get_instrument_with_non_existent_ticker(instruments_service):
    response = instruments_service.search("AAAA")

    assert response.status_code == 200
    assert response.body == []


@pytest.mark.regression
def test_get_instrument_with_empty_value(instruments_service):
    response = instruments_service.search("")

    assert response.status_code == 200
    assert len(response.body) > 0


@pytest.mark.regression
def test_get_instrument_with_special_character(instruments_service):
    response = instruments_service.search("*")

    assert response.status_code == 200
    assert response.body == []


@pytest.mark.regression
def test_get_instrument_without_candidate_id(instruments_service):
    ticker = instruments_service.get_instruments().body[0]["ticker"]

    response = instruments_service.search(ticker, headers={"X-Candidate-Id": None})

    assert response.status_code == 200
    assert response.body[0]["ticker"] == ticker


@pytest.mark.negative
@pytest.mark.parametrize("tier", [None, "TEST"])
def test_get_instrument_with_invalid_bugs(instruments_service, tier):
    response = instruments_service.search("", headers={"X-Enable-Bugs": tier})

    assert response.status_code == 400


@pytest.mark.regression
def test_get_instrument_without_query_param(instruments_service):
    response = instruments_service.search(None)

    assert response.status_code == 200
    assert len(response.body) > 0


@pytest.mark.regression
def test_search_results_have_no_duplicates(instruments_service):
    ticker = instruments_service.get_instruments().body[0]["ticker"]
    partial_query = ticker[:2]

    response = instruments_service.search(partial_query)

    assert response.status_code == 200
    assert_unique_field(response.body, "id")
    assert_unique_field(response.body, "ticker")


@pytest.mark.regression
def test_search_matches_instruments(instruments_service):
    instruments_by_id = {i["id"]: i for i in instruments_service.get_instruments().body}
    search_by_id = {i["id"]: i for i in instruments_service.search("").body}

    assert instruments_by_id == search_by_id
