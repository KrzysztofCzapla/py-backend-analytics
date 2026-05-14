class TestFastAPIMiddleware:
    def test_smoke(self, completely_mocked_db, test_client):
        response = test_client.get("/my-endpoint")
        assert response.json() == {"msg": "my_message"}
        completely_mocked_db.insert_request_info.assert_awaited_once()
