from maxminddb import Reader

from py_backend_analytics.extraction.geo_lookup import IpCountryLookup


class TestIpCountryLookup:
    def test_returns_country(self):
        ip_country_lookup = IpCountryLookup()
        assert ip_country_lookup.get_country("1.1.1.1") == "Australia"
        # this needs to be mocked
        assert not isinstance(ip_country_lookup._db, Reader)

    def test_returns_none_for_unknown_ip(self):
        ip_country_lookup = IpCountryLookup()
        assert ip_country_lookup.get_country("127.0.0.1") is None
        # this needs to be mocked
        assert not isinstance(ip_country_lookup._db, Reader)
