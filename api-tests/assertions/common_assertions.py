def assert_unique_field(items, field):
    values = [item[field] for item in items]
    assert len(values) == len(set(values)), f"Duplicate values found for '{field}'"
