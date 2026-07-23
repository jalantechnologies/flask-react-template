import unittest
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from typing import Optional

from bson import ObjectId

from modules.application.base_model import BaseModel


@dataclass
class SampleModel(BaseModel):
    id: Optional[ObjectId | str] = None


class TestBaseModel(unittest.TestCase):
    def test_created_at_defaults_to_now_utc_aware(self) -> None:
        model = SampleModel()

        assert model.created_at is not None
        assert model.created_at.tzinfo is not None
        assert model.created_at.utcoffset() == UTC.utcoffset(model.created_at)

    def test_naive_created_at_comes_back_utc_aware(self) -> None:
        naive = datetime(2024, 1, 1, 12, 0, 0)

        model = SampleModel(created_at=naive)

        assert model.created_at is not None
        assert model.created_at.tzinfo is UTC
        assert model.created_at == naive.replace(tzinfo=UTC)

    def test_naive_updated_at_comes_back_utc_aware(self) -> None:
        naive = datetime(2024, 1, 1, 12, 0, 0)

        model = SampleModel(created_at=datetime.now(UTC), updated_at=naive)

        assert model.updated_at is not None
        assert model.updated_at.tzinfo is UTC
        assert model.updated_at == naive.replace(tzinfo=UTC)

    def test_updated_at_falls_back_to_created_at_when_omitted(self) -> None:
        created = datetime(2024, 3, 1, 8, 30, tzinfo=UTC)

        model = SampleModel(created_at=created)

        assert model.updated_at == created

    def test_aware_timestamps_are_preserved(self) -> None:
        aware = datetime(2024, 5, 1, 6, 0, tzinfo=timezone.utc)

        model = SampleModel(created_at=aware, updated_at=aware)

        assert model.created_at == aware
        assert model.updated_at == aware
