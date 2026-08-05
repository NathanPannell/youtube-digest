"""add stored trigger for video snapshots

Revision ID: e6c916d1797d
Revises: 23c861dc0003
Create Date: 2026-08-04 18:19:47.389831

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e6c916d1797d"
down_revision: Union[str, Sequence[str], None] = "23c861dc0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION snapshot_video_stats()
        RETURNS TRIGGER AS $$
            DECLARE
                time_since_last_snapshot NUMERIC;
                age_in_seconds NUMERIC;

            BEGIN
                time_since_last_snapshot := EXTRACT(EPOCH FROM (NOW() - (
                    SELECT 
                        COALESCE(MAX(snapshot_time), to_timestamp(0)) 
                    FROM video_snapshots 
                    WHERE video_id = NEW.video_id)
                ));

                age_in_seconds := EXTRACT(EPOCH FROM (NOW() - NEW.published_at));

                IF time_since_last_snapshot >= age_in_seconds/2 THEN
                    INSERT INTO video_snapshots(
                        video_id,
                        snapshot_time,
                        published_at,
                        view_count,
                        like_count,
                        comment_count,
                        age_in_seconds
                    )
                    VALUES (
                        NEW.video_id,
                        NOW(),
                        NEW.published_at,
                        NEW.view_count,
                        NEW.like_count,
                        NEW.comment_count,
                        age_in_seconds
                    );
                END IF;

                RETURN NEW;
            END;
        $$ LANGUAGE plpgsql
    """)

    op.execute("""
        CREATE TRIGGER trg_snapshot_video_stats
        AFTER UPDATE ON videos
        FOR EACH ROW
        EXECUTE FUNCTION snapshot_video_stats()
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER trg_snapshot_video_stats ON videos")
    op.execute("DROP FUNCTION snapshot_video_stats")
