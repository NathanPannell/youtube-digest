from app.database import get_connection


def video_dict_to_tuple(video):
    return (
        video["video_id"],
        video["channel_id"],
        video["published_at"],
        video["title"],
        video["duration"],
        video["view_count"],
        video["like_count"],
        video["comment_count"],
    )


def create_videos(videos):
    query = """
        INSERT INTO videos (
            video_id,
            channel_id,
            published_at,
            title,
            duration,
            view_count,
            like_count,
            comment_count
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)

        ON CONFLICT (video_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            view_count = EXCLUDED.view_count,
            like_count = EXCLUDED.like_count,
            comment_count = EXCLUDED.comment_count
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.executemany(query, [video_dict_to_tuple(v) for v in videos])


def get_video(video_id):

    query = """
        SELECT 
            video_id,
            channel_id,
            published_at,
            title,
            duration,
            view_count,
            like_count,
            comment_count
        FROM videos 
        WHERE video_id = %s
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (video_id,),
            )

            video = cursor.fetchone()

        if video is None:
            raise LookupError(f"Unable to find video with video_id = {video_id}")

        return video
