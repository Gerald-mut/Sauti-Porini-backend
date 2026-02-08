import requests
import json

class SimpleSupabase:
    def __init__(self, url: str, key: str):
        self.base_url = f"{url}/rest/v1"
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }

    def insert(self, table: str, data: dict):
        resp = requests.post(f"{self.base_url}/{table}", headers=self.headers, json=data)
        if resp.status_code >= 400:
            raise Exception(f"Supabase Insert Error ({resp.status_code}): {resp.text}")
        return resp.json()

    def update(self, table: str, data: dict, filters: dict):
        # Construct query string from filters
        # Simple implementation: supports only eq (equals) for now as used in the project
        query_params = "&".join([f"{k}=eq.{v}" for k, v in filters.items()])
        url = f"{self.base_url}/{table}?{query_params}"
        
        resp = requests.patch(url, headers=self.headers, json=data)
        if resp.status_code >= 400:
            raise Exception(f"Supabase Update Error ({resp.status_code}): {resp.text}")
        return resp.json()

    def select(self, table: str, columns: str = "*", filters: dict = None, order: str = None, limit: int = None):
        params = {"select": columns}
        if filters:
            for k, v in filters.items():
                params[k] = f"eq.{v}"
        
        if order:
            # order format: "column.desc" or "column.asc"
            col, direction = order.split(".")
            params["order"] = f"{col}.{direction}"
            
        if limit:
            # Supabase uses Range header or limit param (PostgREST)
            # PostgREST uses limit in newer versions, usually works
            params["limit"] = limit

        resp = requests.get(f"{self.base_url}/{table}", headers=self.headers, params=params)
        if resp.status_code >= 400:
            raise Exception(f"Supabase Select Error ({resp.status_code}): {resp.text}")
        return resp.json()
