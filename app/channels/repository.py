from app.database import get_connection


def channel_dict_to_tuple(channel):
    return (
        channel["channel_id"],
        channel["title"],
        channel["published_at"],
        channel["url"],
        channel["video_count"],
        channel["uploads_playlist_id"],
    )


def create_channel(channel):
    query = """
        INSERT INTO channels (
            channel_id, 
            title, 
            published_at, 
            url, 
            video_count, 
            uploads_playlist_id
        )
        VALUES (%s, %s, %s, %s, %s, %s)

        ON CONFLICT (channel_id)
        DO UPDATE SET
            video_count = EXCLUDED.video_count
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                channel_dict_to_tuple(channel),
            )


def get_channel(channel_id):

    query = """
        SELECT 
            channel_id, 
            title, 
            published_at, 
            url, 
            video_count, 
            uploads_playlist_id,
            tracked_at
        FROM channels 
        WHERE channel_id = %s
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (channel_id,),
            )

            channel = cursor.fetchone()

        if channel is None:
            raise LookupError(f"Unable to find channel with channel_id = {channel_id}")

        return channel


def get_all_channels():
    query = """
            SELECT 
                channel_id, 
                title, 
                published_at, 
                url, 
                video_count, 
                uploads_playlist_id,
                tracked_at
            FROM channels
        """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
            )

            channels = cursor.fetchall()

        if channels is []:
            raise LookupError(f"Unable to find any channels")

        return channels
