def test_read_main(client):
    response = client.get("/v2/")
    assert response.status_code == 200
    assert response.json() == {"message": "OCI Registry API V2"}
