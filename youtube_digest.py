import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build
from dotenv import load_dotenv


import app.channels.repository as channels
import app.videos.repository as videos
import argparse

load_dotenv()


def get_channel_info(client, id=None, handle=None):
    if (id is None) == (handle is None):
        raise ValueError("Provide exactly one of id or handle")

    request = client.channels().list(
        part="snippet,statistics,contentDetails",
        id=id,
        forHandle=handle,
    )
    response = request.execute()

    items = response.get("items", [])
    if len(items) != 1:
        raise LookupError(f"Expected one channel, found {len(items)}")

    item = items[0]
    channel = {
        "channel_id": item["id"],
        "title": item["snippet"]["title"],
        "published_at": item["snippet"]["publishedAt"],
        "url": item["snippet"]["customUrl"],
        "video_count": item["statistics"].get("videoCount", "0"),
        "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
    }
    return channel


def get_playlist_items(client, id, page_token=None, max_results=25, max_age_days=7):
    all_playlist_items = []
    oldest_published_at = datetime.now(ZoneInfo("America/Vancouver")) - timedelta(
        days=max_age_days
    )

    while len(all_playlist_items) < max_results:
        request = client.playlistItems().list(
            part="snippet,contentDetails",
            maxResults=min(25, max_results - len(all_playlist_items)),
            playlistId=id,
            pageToken=page_token,
        )
        response = request.execute()

        playlist_items = response.get("items", [])
        all_playlist_items.extend(
            [
                {
                    "published_at": datetime.fromisoformat(
                        pi["snippet"]["publishedAt"]
                    ),
                    "channel_id": pi["snippet"]["channelId"],
                    "title": pi["snippet"]["title"],
                    "video_id": pi["contentDetails"]["videoId"],
                }
                for pi in playlist_items
            ]
        )

        if (
            len(all_playlist_items) > 1
            and all_playlist_items[-1].get("published_at") < oldest_published_at
        ):
            all_playlist_items = [
                pi
                for pi in all_playlist_items
                if pi.get("published_at")
                and pi.get("published_at") > oldest_published_at
            ]
            break

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_playlist_items


def get_videos_stats(client, video_ids):
    all_stats = []

    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i : i + 50]
        request = client.videos().list(
            part="statistics,contentDetails", id=",".join(batch_ids)
        )
        response = request.execute()

        for item in response.get("items", []):
            all_stats.append(
                {
                    "video_id": item["id"],
                    "duration": item["contentDetails"]["duration"],
                    "view_count": item["statistics"].get("viewCount", "0"),
                    "like_count": item["statistics"].get("likeCount", "0"),
                    "comment_count": item["statistics"].get("commentCount", "0"),
                }
            )
    return all_stats


def main():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY is not configured")
    client = build("youtube", "v3", developerKey=api_key)

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--handle")
    parser.add_argument("-d", "--days", default=7, type=int)
    args = parser.parse_args()

    channel = get_channel_info(client, handle=args.handle)
    print(f"Found channel {channel["title"]}")
    channels.create_channel(channel)

    playlist_items = get_playlist_items(
        client, channel["uploads_playlist_id"], max_age_days=args.days, max_results=1000
    )
    print(f"Found {len(playlist_items)} videos in the past {args.days} days")

    video_ids = [playlist_item.get("video_id") for playlist_item in playlist_items]
    video_stats = get_videos_stats(client, video_ids)

    merged = {}
    for item in playlist_items:
        merged[item["video_id"]] = item
    for video in video_stats:
        merged[video["video_id"]] = merged.get(video["video_id"], {}) | video

    videos_list = merged.values()
    videos.create_videos(videos_list)


if __name__ == "__main__":
    main()
