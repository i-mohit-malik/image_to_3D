import os
import time
from typing import Any, Dict, Optional

import requests


class TripoClient:
    """A small client for the Tripo 3D REST API.

    This class is intentionally small and focused on a single responsibility:
    talking to the Tripo API and returning structured results.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        output_dir: str,
        session: Optional[requests.Session] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.output_dir = output_dir
        self._session = session or requests.Session()

    def _auth_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _get_file_type(self, path: str) -> str:
        _, ext = os.path.splitext(path)
        return ext.lstrip(".").lower() or "jpg"

    def upload_image(self, image_path: str) -> str:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_path, "rb") as f:
            res = self._session.post(
                f"{self.base_url}/upload/sts",
                headers=self._auth_headers(),
                files={"file": f},
            )

        payload = res.json()
        if res.status_code != 200 or payload.get("code") != 0:
            raise RuntimeError(f"Image upload failed ({res.status_code}): {payload}")

        token = payload.get("data", {}).get("image_token")
        if not token:
            raise RuntimeError(f"Upload response missing image_token: {payload}")

        return token

    def create_task(self, image_token: str, file_type: str) -> str:
        payload = {
            "type": "image_to_model",
            "file": {"type": file_type, "file_token": image_token},
        }

        res = self._session.post(
            f"{self.base_url}/task",
            headers={**self._auth_headers(), "Content-Type": "application/json"},
            json=payload,
        )

        payload = res.json()
        if res.status_code != 200 or payload.get("code") != 0:
            raise RuntimeError(f"Task creation failed ({res.status_code}): {payload}")

        task_id = payload.get("data", {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"Missing task_id in task response: {payload}")

        return task_id

    def generate_from_image(self, image_path: str) -> str:
        """Upload an image, create a task, and return the task ID."""
        token = self.upload_image(image_path)
        file_type = self._get_file_type(image_path)
        return self.create_task(token, file_type)

    def _find_url(self, value: Any) -> Optional[str]:
        if isinstance(value, str) and value.startswith("http"):
            return value
        if isinstance(value, dict):
            for v in value.values():
                found = self._find_url(v)
                if found:
                    return found
        return None

    def poll_task(self, task_id: str, poll_interval: float = 5.0, max_retries: int = 20) -> str:
        retries = 0
        while True:
            res = self._session.get(
                f"{self.base_url}/task/{task_id}",
                headers=self._auth_headers(),
                timeout=20,
            )

            # Try to parse JSON; if it's not JSON, treat it as a transient error.
            try:
                payload = res.json()
            except ValueError:
                payload = None

            if res.status_code >= 500 or payload is None:
                retries += 1
                if retries > max_retries:
                    raise RuntimeError(
                        f"Unable to fetch task status (HTTP {res.status_code}): {res.text}"
                    )

                print(
                    f"⚠️  Transient status error (HTTP {res.status_code}) - retrying in {min(poll_interval * (2 ** (retries - 1)), 30):.0f}s... ({retries}/{max_retries})"
                )
                time.sleep(min(poll_interval * (2 ** (retries - 1)), 30))
                continue

            if res.status_code != 200 or payload.get("code") != 0:
                raise RuntimeError(f"Status request failed ({res.status_code}): {payload}")

            data = payload.get("data", {})
            status = data.get("status")

            print(f"🔄 Status: {status}")

            if status == "success":
                output = data.get("output") or {}
                model_url = self._find_url(output)
                if not model_url:
                    raise RuntimeError(f"No model URL in output: {output}")
                return model_url

            if status in ["failed", "cancelled", "banned", "expired"]:
                raise RuntimeError(f"Task ended with status '{status}': {data}")

            time.sleep(poll_interval)

    def download_model(self, url: str, output_name: str) -> str:
        os.makedirs(self.output_dir, exist_ok=True)

        if not output_name.lower().endswith(".glb"):
            output_name = os.path.splitext(output_name)[0] + ".glb"

        output_path = os.path.join(self.output_dir, output_name)

        res = self._session.get(url)
        if res.status_code != 200:
            raise RuntimeError(f"Download failed: HTTP {res.status_code}")

        with open(output_path, "wb") as f:
            f.write(res.content)

        return os.path.abspath(output_path)
