from app.ingestion.youtube import snapshot_all
import os
from dotenv import load_dotenv


def main():
    load_dotenv()
    max_video_age_days = int(os.environ.get("MAX_VIDEO_AGE_IN_DAYS"))

    snapshot_all(max_video_age_days=max_video_age_days)


if __name__ == "__main__":
    main()
