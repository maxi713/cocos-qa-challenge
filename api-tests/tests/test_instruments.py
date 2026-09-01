import pytest
from assertions.common_assertions import assert_unique_field
from assertions.instrument_assertions import assert_instruments_list_schema


@pytest.fixture(scope="session")
def first_instrument(instruments_service):
    return instruments_service.get_instruments().body[0]


@pytest.fixture
def nonexistent_ticker(instruments_service):
    all_tickers = [i["ticker"] for i in instruments_service.get_instruments().body]
    assert "AAAA" not in all_tickers

    return "AAAA"


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


@pytest.mark.regression
def test_instruments_response_content_type(instruments_service):
    response = instruments_service.get_instruments()

    assert "application/json" in response.headers["Content-Type"]


@pytest.mark.regression
def test_get_instruments_does_not_require_candidate_id(instruments_service):
    response = instruments_service.get_instruments(headers={"X-Candidate-Id": None})

    assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.parametrize("tier", ["off", "OFF", "Off", "oFf"])
def test_bugs_tier_header_is_case_insensitive(instruments_service, tier):
    response = instruments_service.get_instruments(headers={"X-Enable-Bugs": tier})

    assert response.status_code == 200


@pytest.mark.negative
@pytest.mark.parametrize(
    "bugs_tier_header", [None, "nightmare"], ids=["missing", "invalid"]
)
def test_get_instruments_with_invalid_bugs_tier(instruments_service, bugs_tier_header):
    response = instruments_service.get_instruments(
        headers={"X-Enable-Bugs": bugs_tier_header}
    )

    assert response.status_code == 400
    assert response.body["error"] == "X-Enable-Bugs must be off, easy, medium, or hard"


@pytest.mark.negative
def test_unsupported_method_on_instruments(api_client):
    response = api_client.post("/instruments")

    assert response.status_code == 404


@pytest.mark.regression
def test_get_specific_ticker(instruments_service, first_instrument):
    response = instruments_service.search(first_instrument["ticker"])

    assert response.status_code == 200
    assert_instruments_list_schema(response.body)
    assert len(response.body) == 1
    assert response.body[0] == first_instrument


@pytest.mark.regression
def test_get_instrument_with_lowercase(instruments_service, first_instrument):
    response = instruments_service.search(first_instrument["ticker"].lower())

    assert response.status_code == 200
    assert response.body[0]["ticker"] == first_instrument["ticker"]


@pytest.mark.regression
def test_get_instrument_with_partial_ticker(instruments_service, first_instrument):
    ticker = first_instrument["ticker"]
    partial_ticker = [ticker[i : i + 2] for i in range(len(ticker) - 1)]

    for t in partial_ticker:
        response = instruments_service.search(t)
        assert response.status_code == 200
        assert len(response.body) > 0


@pytest.mark.regression
def test_search_results_have_no_duplicates(instruments_service, first_instrument):
    partial_query = first_instrument["ticker"][:2]

    response = instruments_service.search(partial_query)

    assert response.status_code == 200
    assert_unique_field(response.body, "id")
    assert_unique_field(response.body, "ticker")


@pytest.mark.regression
def test_get_instrument_without_candidate_id(instruments_service, first_instrument):
    response = instruments_service.search(
        first_instrument["ticker"], headers={"X-Candidate-Id": None}
    )

    assert response.status_code == 200
    assert response.body[0]["ticker"] == first_instrument["ticker"]


@pytest.mark.negative
@pytest.mark.parametrize("tier", [None, "TEST"])
def test_get_instrument_with_invalid_bugs(instruments_service, tier):
    response = instruments_service.search("", headers={"X-Enable-Bugs": tier})

    assert response.status_code == 400


@pytest.mark.regression
def test_get_instrument_with_name(instruments_service, first_instrument):
    response = instruments_service.search(first_instrument["name"])

    assert response.status_code == 200
    assert response.body == []


@pytest.mark.regression
def test_get_instrument_with_non_existent_ticker(instruments_service, nonexistent_ticker):
    response = instruments_service.search(nonexistent_ticker)

    assert response.status_code == 200
    assert response.body == []


@pytest.mark.regression
def test_get_instrument_with_special_character(instruments_service):
    response = instruments_service.search("*")

    assert response.status_code == 200
    assert response.body == []


@pytest.mark.regression
def test_get_instrument_with_empty_value(instruments_service):
    response = instruments_service.search("")

    assert response.status_code == 200
    assert len(response.body) > 0


@pytest.mark.regression
def test_get_instrument_without_query_param(instruments_service):
    response = instruments_service.search(None)

    assert response.status_code == 200
    assert len(response.body) > 0


@pytest.mark.regression
def test_search_matches_instruments(instruments_service):
    instruments_by_id = {i["id"]: i for i in instruments_service.get_instruments().body}
    search_by_id = {i["id"]: i for i in instruments_service.search("").body}

    assert instruments_by_id == search_by_id
