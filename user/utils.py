import requests
import tempfile

from django.core import files


def download_file_from_url(url):
    # Stream the image from the url
    try:
        request = requests.get(url, stream=True)
    except requests.exceptions.RequestException as e:
        # TODO: log error here
        return None

    if request.status_code != requests.codes.ok:
        # TODO: log error here
        return None
    # Determine file extension from content type
    content_type = request.headers.get('content-type')
    if content_type == 'image/jpeg':
        file_extension = '.jpg'
    elif content_type == 'image/png':
        file_extension = '.png'
    else:
        # Default to .jpg if content type is unknown
        file_extension = '.jpg'
    # Create a temporary file
    lf = tempfile.NamedTemporaryFile(suffix=file_extension)

    # Read the streamed image in sections
    for block in request.iter_content(1024 * 8):
        if not block:
            break
        lf.write(block)

    lf.flush()

    img_file = files.File(lf)

    return img_file
