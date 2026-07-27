import os

from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


def get_channel(client, id=None, handle=None):
    if (id is None) == (handle is None):
        raise ValueError("Provide exactly one of id or handle")

    request = client.channels().list(
        part="contentDetails",
        id=id,
        forHandle=handle,
    )
    response = request.execute()

    items = response.get("items", [])
    if len(items) != 1:
        raise LookupError(f"Expected one channel, found {len(items)}")

    return items[0]


def get_playlist_items(client, id, page_token=None, max_results=25):
    videos = []

    while len(videos) < max_results:
        request = client.playlistItems().list(
            part="contentDetails",
            maxResults=min(25, max_results - len(videos)),
            playlistId=id,
            pageToken=page_token,
        )
        response = request.execute()
        videos += response.get("items", [])

        page_token = response.get("nextPageToken")
        if not page_token:
            break
    return videos


def get_videos_stats(client, video_ids):
    all_stats = []

    # Process in batches of 50
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i : i + 50]
        request = client.videos().list(
            part="snippet,statistics,contentDetails", id=",".join(batch_ids)
        )
        response = request.execute()

        for item in response.get("items", []):
            all_stats.append(
                {
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "publishedAt": item["snippet"]["publishedAt"],
                    "duration": item["contentDetails"]["duration"],
                    "viewCount": item["statistics"].get("viewCount", "0"),
                    "likeCount": item["statistics"].get("likeCount", "0"),
                    "commentCount": item["statistics"].get("commentCount", "0"),
                }
            )
    return all_stats


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY is not configured")
    client = build("youtube", "v3", developerKey=api_key)

    channel = get_channel(client, handle="@TED")
    assert channel is not None

    uploads_playlist_id = (
        channel.get("contentDetails").get("relatedPlaylists").get("uploads")
    )

    videos = get_playlist_items(client, uploads_playlist_id, max_results=1)

    video_ids = [video.get("contentDetails").get("videoId") for video in videos]
    stats = get_videos_stats(client, video_ids)
    print(stats)
    print(len(stats))


if __name__ == "__main__":
    main()
