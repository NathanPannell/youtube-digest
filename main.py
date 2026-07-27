import os

from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


def get_channel(client, id=None, handle=None):
    assert id is not None or handle is not None

    request = client.channels().list(
        part="snippet,contentDetails,statistics",
        id=id,
        forHandle=(handle if id is None else None),
    )
    response = request.execute()

    num_matches = response.get("pageInfo").get("totalResults")
    assert num_matches == 1

    return response.get("items")[0]


def get_playlist_items(client, id, page_token=None, num_results=25):
    videos = []

    while len(videos) < num_results:
        request = client.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=min(25, num_results - len(videos)),
            playlistId=id,
            pageToken=page_token,
        )
        response = request.execute()

        page_token = response.get("nextPageToken")
        videos += response.get("items")
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
                    "viewCount": item["statistics"].get("viewCount", 0),
                    "likeCount": item["statistics"].get("likeCount", 0),
                    "commentCount": item["statistics"].get("commentCount", 0),
                }
            )
    return all_stats


def main():
    client = build("youtube", "v3", developerKey=os.getenv("key"))

    channel = get_channel(client, handle="@TED")
    assert channel is not None

    uploads_playlist_id = (
        channel.get("contentDetails").get("relatedPlaylists").get("uploads")
    )

    videos = get_playlist_items(client, uploads_playlist_id)

    videos = get_playlist_items(client, uploads_playlist_id, num_results=1)

    video_ids = [video.get("contentDetails").get("videoId") for video in videos]
    stats = get_videos_stats(client, video_ids)
    print(stats)
    print(len(stats))


if __name__ == "__main__":
    main()
