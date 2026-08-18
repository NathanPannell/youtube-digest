import os
import googleapiclient.discovery

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import app.repositories.channels as channel_repo
import app.repositories.videos as video_repo

# HELPER METHODS


def create_youtube_client():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY is not configured")

    client = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    return client


def fetch_channel(client, id=None, handle=None):
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


def fetch_playlist_items(
    client,
    id,
    page_token=None,
    max_results=10_000,
    max_age_days=7,
):
    all_playlist_items = []
    oldest_date_threshold = datetime.now(ZoneInfo("America/Vancouver")) - timedelta(
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

        # If there is a video that's too old, we've gotten everything within range
        # Run a quick filter to trim the ones we don't want
        if (
            len(all_playlist_items) > 1
            and all_playlist_items[-1].get("published_at") < oldest_date_threshold
        ):
            all_playlist_items = [
                pi
                for pi in all_playlist_items
                if pi.get("published_at")
                and pi.get("published_at") > oldest_date_threshold
            ]
            break

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return all_playlist_items


def fetch_videos_stats(client, video_ids):
    all_videos_stats = []

    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i : i + 50]
        request = client.videos().list(
            part="statistics,contentDetails", id=",".join(batch_ids)
        )
        response = request.execute()

        for item in response.get("items", []):
            all_videos_stats.append(
                {
                    "video_id": item["id"],
                    "duration": item["contentDetails"]["duration"],
                    "view_count": item["statistics"].get("viewCount", "0"),
                    "like_count": item["statistics"].get("likeCount", "0"),
                    "comment_count": item["statistics"].get("commentCount", "0"),
                }
            )
    return all_videos_stats


# INGESTION METHODS


def upsert_channel(handle=None, client=None, channel_id=None):
    if client is None:
        client = create_youtube_client()

    channel = fetch_channel(client, handle=handle, id=channel_id)
    print(f"Found channel '{channel["title"]}'")
    channel_repo.create_channel(channel)

    return channel


def snapshot_channel_videos(channel_id, client=None, max_video_age_days=None):
    if client is None:
        client = create_youtube_client()

    if max_video_age_days is None:
        max_video_age_days = os.environ.get("MAX_VIDEO_AGE_DAYS")

    channel = upsert_channel(client=client, channel_id=channel_id)

    playlist_items = fetch_playlist_items(
        client, channel.get("uploads_playlist_id"), max_age_days=max_video_age_days
    )
    print(f"Found {len(playlist_items)} videos in the past {max_video_age_days} days")

    video_ids = [playlist_item.get("video_id") for playlist_item in playlist_items]
    video_stats = fetch_videos_stats(client, video_ids)

    # Merge dictionaries element-wise
    merged = {}
    for item in playlist_items:
        merged[item["video_id"]] = item
    for video in video_stats:
        merged[video["video_id"]] = merged.get(video["video_id"], {}) | video
    videos_list = merged.values()

    video_repo.create_videos(videos_list)


def snapshot_all(max_video_age_days=None):
    client = create_youtube_client()

    all_channels = channel_repo.get_all_channels()
    for channel in all_channels:
        channel_id = channel.get("channel_id")
        snapshot_channel_videos(
            channel_id=channel_id, max_video_age_days=max_video_age_days, client=client
        )
