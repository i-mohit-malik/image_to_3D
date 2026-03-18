import os
import time
import requests

from config import *


# 🔷 Headers (used for all Tripo API requests)
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
}


def _mask_api_key(key: str) -> str:
    """Mask most of the API key for safe logging."""

    if not key or len(key) < 10:
        return key
    return f"{key[:6]}...{key[-4:]}"


def _ensure_api_key():
    if not API_KEY or "xxxx" in API_KEY or API_KEY.startswith("msy-"):
        raise RuntimeError(
            "The API_KEY in src/config.py looks like a placeholder.\n"
            "Please replace it with your real Tripo API key."
        )

    # Provide a little more help when an invalid key is configured.
    if API_KEY and not API_KEY.startswith(("tsk_", "tcli_")):
        print(
            "⚠️  Warning: Your TRIPO_API_KEY does not look like a typical Tripo key (tsk_/tcli_)."
            " If you continue to see authentication failures, double-check your key."
        )


def _get_file_type_from_path(path: str) -> str:
    _, ext = os.path.splitext(path)
    return ext.lstrip(".").lower() or "jpg"


# 🔷 Step 1: Upload Image & Create Task
def generate_from_image(image_path: str):
    _ensure_api_key()

    print(f"\n📤 Uploading image: {image_path}")

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"❌ Image not found: {image_path}")

    with open(image_path, "rb") as f:
        upload_res = requests.post(
            f"{BASE_URL}/upload/sts",
            headers=HEADERS,
            files={"file": f},
        )

    try:
        upload_payload = upload_res.json()
    except ValueError:
        raise RuntimeError(f"Invalid JSON upload response ({upload_res.status_code}): {upload_res.text}")

    if upload_res.status_code != 200 or upload_payload.get("code") != 0:
        error_hint = ""
        if upload_res.status_code == 401 or upload_payload.get("code") == 1002:
            masked = _mask_api_key(API_KEY) if API_KEY else "<missing>"
            error_hint = (
                "\n\nHint: Authentication failed. "
                f"The request used API key: {masked}\n"
                "Make sure TRIPO_API_KEY in your .env is valid, not expired, and matches the key from your Tripo dashboard."
            )

        raise RuntimeError(
            f"Image upload failed ({upload_res.status_code}): {upload_payload}{error_hint}"
        )

    image_token = upload_payload.get("data", {}).get("image_token")
    if not image_token:
        raise RuntimeError(f"Image upload did not return image_token: {upload_payload}")

    print(f"✅ Uploaded (image_token={image_token})")

    file_type = _get_file_type_from_path(image_path)
    payload = {
        "type": "image_to_model",
        "file": {
            "type": file_type,
            "file_token": image_token,
        },
        # Optional: add generation parameters here (model_version, face_limit, etc.)
    }

    res = requests.post(
        f"{BASE_URL}/task",
        headers={**HEADERS, "Content-Type": "application/json"},
        json=payload,
    )

    try:
        task_resp = res.json()
    except ValueError:
        raise RuntimeError(f"Invalid JSON task response ({res.status_code}): {res.text}")

    if res.status_code != 200 or task_resp.get("code") != 0:
        raise RuntimeError(f"Task creation failed ({res.status_code}): {task_resp}")

    task_id = task_resp.get("data", {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"Task creation response missing task_id: {task_resp}")

    print(f"✅ Task Created: {task_id}")
    return task_id


# 🔷 Step 2: Check Status
def check_status(task_id: str, poll_interval: float = 5.0) -> str:
    print("\n⏳ Checking status...")

    while True:
        res = requests.get(
            f"{BASE_URL}/task/{task_id}",
            headers=HEADERS,
        )

        try:
            status_payload = res.json()
        except ValueError:
            raise RuntimeError(f"Invalid JSON status response ({res.status_code}): {res.text}")

        if res.status_code != 200 or status_payload.get("code") != 0:
            raise RuntimeError(f"Status request failed ({res.status_code}): {status_payload}")

        data = status_payload.get("data", {})
        status = data.get("status")
        print(f"🔄 Status: {status}")

        if status == "success":
            output = data.get("output") or {}

            # Output field structure can vary across versions. We try to find a downloadable URL.
            def _find_url_in(value):
                if isinstance(value, str) and value.startswith("http"):
                    return value
                if isinstance(value, dict):
                    for v in value.values():
                        url = _find_url_in(v)
                        if url:
                            return url
                return None

            # Try common output fields, then fallback to scanning everything.
            candidates = [
                output.get("model"),
                output.get("model_url"),
                output.get("pbr_model"),
                output.get("base_model"),
                output.get("generated_image"),
                output.get("rendered_image"),
                output.get("result"),
            ]

            model_url = None
            for candidate in candidates:
                model_url = _find_url_in(candidate)
                if model_url:
                    break

            if not model_url:
                # fallback scan all output fields
                for v in output.values():
                    model_url = _find_url_in(v)
                    if model_url:
                        break

            if not model_url:
                raise RuntimeError(f"No model URL in output: {output}")

            print("✅ Generation completed! URL found:", model_url)
            return model_url

        if status in ["failed", "cancelled", "banned", "expired"]:
            raise RuntimeError(f"Task ended with status '{status}': {data}")

        time.sleep(poll_interval)


# 🔷 Step 3: Download Model
def download_model(url, output_name: str):
    print("\n📥 Downloading model...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Keep the output file name consistent with the input image name.
    # Replace extension with .glb since the model is a glTF binary.
    if not output_name.lower().endswith(".glb"):
        output_name = os.path.splitext(output_name)[0] + ".glb"

    file_path = os.path.join(OUTPUT_DIR, output_name)

    res = requests.get(url)

    if res.status_code != 200:
        raise RuntimeError("❌ Download failed")

    with open(file_path, "wb") as f:
        f.write(res.content)

    print(f"✅ File saved at: {file_path}")
    return file_path


# 🔷 Main
if __name__ == "__main__":
    image_path = r"C:\Omniverse\Mohit\Image_to_3D\input_images\images.jpg"

    try:
        task_id = generate_from_image(image_path)
        model_url = check_status(task_id)

        input_basename = os.path.splitext(os.path.basename(image_path))[0]
        file_path = download_model(model_url, input_basename)

        print("\n🎉 DONE! Model ready.")

    except Exception as e:
        print("\n🚨 ERROR:", str(e))