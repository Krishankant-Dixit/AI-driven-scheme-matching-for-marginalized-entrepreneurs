import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.schemas.scheme import RuleSeed, SchemeRecord, SchemeSeed

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIRECTORY = PROJECT_ROOT / "data"

ModelType = TypeVar("ModelType", bound=BaseModel)


def _load_json(path: Path, model_type: type[ModelType]) -> ModelType:
    with path.open(encoding="utf-8") as data_file:
        return model_type.model_validate(json.load(data_file))


def load_scheme_seed(path: Path | None = None) -> SchemeSeed:
    seed = _load_json(path or DATA_DIRECTORY / "schemes.json", SchemeSeed)
    scheme_ids = [scheme.scheme_id for scheme in seed.schemes]
    if len(scheme_ids) != len(set(scheme_ids)):
        raise ValueError("scheme_id values must be unique")
    return seed


def load_rule_seed(path: Path | None = None) -> RuleSeed:
    seed = _load_json(path or DATA_DIRECTORY / "rules.json", RuleSeed)
    return seed


def load_runtime_scheme_seed(database=None) -> SchemeSeed:
    """Load JSON seeds and overlay validated admin-managed Mongo records."""
    seed = load_scheme_seed()
    if database is None:
        return seed
    managed = [
        SchemeRecord.model_validate({key: value for key, value in document.items() if key != "_id"})
        for document in database["schemes"].find({})
    ]
    if not managed:
        return seed
    by_id = {scheme.scheme_id: scheme for scheme in seed.schemes}
    by_id.update({scheme.scheme_id: scheme for scheme in managed})
    return SchemeSeed(schemes=list(by_id.values()))
