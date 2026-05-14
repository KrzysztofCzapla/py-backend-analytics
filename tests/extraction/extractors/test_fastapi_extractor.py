from types import SimpleNamespace

from py_backend_analytics.extraction.extractors.fastapi_extractor import (
    FastAPIExtractor,
)


class TestFastAPIExtractor:
    def test_extractor(self):
        extractor = FastAPIExtractor()
        request_no_routes = SimpleNamespace(
            url=SimpleNamespace(path="/mypath"),
            client=SimpleNamespace(host="myhost"),
            headers={"referer": "google.com"},
            app=SimpleNamespace(router=SimpleNamespace(routes=[])),
        )
        output = extractor.extract(request_no_routes)
        assert output.source == "google.com"
        assert output.page == "/mypath"
        assert output.location is None
