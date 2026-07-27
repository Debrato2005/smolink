from app.utils.snowflake import SnowflakeGenerator


def test_next_id_returns_integer() -> None:
    generator = SnowflakeGenerator(worker_id=1)

    assert isinstance(generator.next_id(), int)


def test_next_ids_are_unique() -> None:
    generator = SnowflakeGenerator(worker_id=1)

    ids = [generator.next_id() for _ in range(100)]

    assert len(ids) == len(set(ids))


def test_next_ids_sort_in_creation_order() -> None:
    generator = SnowflakeGenerator(worker_id=1)

    ids = [generator.next_id() for _ in range(100)]

    assert ids == sorted(ids)
    