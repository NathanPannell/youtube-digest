from app.database import get_connection


def create_channel(
    channel_id, title, published_at, url, video_count, uploads_playlist_id
):
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
            video_count = %s
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    channel_id,
                    title,
                    published_at,
                    url,
                    video_count,
                    uploads_playlist_id,
                    video_count,
                ),
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
