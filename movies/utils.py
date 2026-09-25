from urllib.parse import urlparse, parse_qs


def get_youtube_id(url):

    if not url:
        return None

    try:
        url = url.strip()
        parsed = urlparse(url)

        domain = parsed.netloc.lower()

        allowed_domains = {
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
            "www.youtu.be",
        }

        # Only allowed YouTube domains
        if domain not in allowed_domains:
            return None

        # Only HTTPS
        if parsed.scheme != "https":
            return None

        video_id = None

        # https://www.youtube.com/watch?v=VIDEO_ID
        if domain in {
            "youtube.com",
            "www.youtube.com"
        }:

            if parsed.path != "/watch":
                return None

            video_id = parse_qs(
                parsed.query
            ).get("v", [None])[0]

        # https://youtu.be/VIDEO_ID
        elif domain in {
            "youtu.be",
            "www.youtu.be"
        }:

            video_id = parsed.path.strip("/")

        if not video_id:
            return None

        # YouTube Video ID validation
        if len(video_id) != 11:
            return None

        if not all(
            char.isalnum() or char in "-_"
            for char in video_id
        ):
            return None

        return video_id

    except Exception:
        return None