import os

from config import INPUT_IMAGE_PATH, API_KEY, BASE_URL, OUTPUT_DIR
from tripo_client import TripoClient


def main() -> None:
    assert API_KEY, "TRIPO_API_KEY is required in .env"

    client = TripoClient(api_key=API_KEY, base_url=BASE_URL, output_dir=OUTPUT_DIR)

    image_path = INPUT_IMAGE_PATH

    task_id = client.generate_from_image(image_path)
    model_url = client.poll_task(task_id)

    input_basename = os.path.splitext(os.path.basename(image_path))[0]
    output_path = client.download_model(model_url, input_basename)

    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
