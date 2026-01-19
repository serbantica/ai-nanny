import httpx

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def get_health(self):
        try:
            return httpx.get(f"{self.base_url}/health")
        except httpx.RequestError:
            return None

    # Add other API methods here as needed
