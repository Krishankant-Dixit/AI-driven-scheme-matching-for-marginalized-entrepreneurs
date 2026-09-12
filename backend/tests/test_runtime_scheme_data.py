from datetime import date

from app.utils.scheme_data import load_runtime_scheme_seed


class FakeSchemes:
    def __init__(self, documents):
        self.documents = documents

    def find(self, _query):
        return self.documents


class FakeDatabase:
    def __init__(self, documents):
        self.schemes = FakeSchemes(documents)

    def __getitem__(self, name):
        assert name == "schemes"
        return self.schemes


def test_runtime_scheme_loader_accepts_mongo_id_and_overlays_seed():
    document = {
        "_id": "mongo-only-id",
        "scheme_id": "PMEGP",
        "name": "Managed PMEGP",
        "short_name": "PMEGP",
        "description": "Managed scheme record",
        "official_source": "Official source",
        "official_source_url": "https://example.gov.in/pmeg p".replace(" ", ""),
        "source_type": "OFFICIAL_PORTAL",
        "last_verified": date.today().isoformat(),
        "version": "2.0.0",
        "active": True,
    }
    schemes = load_runtime_scheme_seed(FakeDatabase([document])).schemes
    pmegp = next(scheme for scheme in schemes if scheme.scheme_id == "PMEGP")
    assert pmegp.name == "Managed PMEGP"
    assert pmegp.version == "2.0.0"