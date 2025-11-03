from PIL import Image
import io, base64

def generate_thumbnails(image_b64: str, sizes=(128, 256)) -> list[str]:
    """
    Crea miniaturas a partir de una imagen en base64.

    Args:
        image_b64: Captura original en base64.
        sizes: Tupla con los tamaños deseados (ancho máximo).

    Returns:
        Lista de miniaturas codificadas en base64.
    """
    if not image_b64:
        return []

    try:
        image_bytes = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        thumbnails = []
        for size in sizes:
            thumb = img.copy()
            thumb.thumbnail((size, size))
            buffer = io.BytesIO()
            thumb.save(buffer, format="JPEG", quality=85)
            thumbnails.append(base64.b64encode(buffer.getvalue()).decode("utf-8"))

        return thumbnails

    except Exception as e:
        print(f"[image_processor] Error generando thumbnails: {e}")
        return []

