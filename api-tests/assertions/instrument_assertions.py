from jsonschema import validate
from schemas.instrument_schema import instrument_schema


def assert_instrument_schema(instrument):
    validate(instance=instrument, schema=instrument_schema)


def assert_instruments_list_schema(instruments):
    assert isinstance(instruments, list)
    assert len(instruments) > 0
    for instrument in instruments:
        assert_instrument_schema(instrument)
