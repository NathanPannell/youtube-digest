"""create video snapshot table

Revision ID: 23c861dc0003
Revises: b04480484d0b
Create Date: 2026-08-04 13:17:02.073103

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "23c861dc0003"
down_revision: Union[str, Sequence[str], None] = "b04480484d0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE video_snapshots(
            video_id VARCHAR(11) NOT NULL REFERENCES videos(video_id),
            snapshot_time TIMESTAMPTZ NOT NULL,
            published_at TIMESTAMPTZ NOT NULL,
            view_count INTEGER,
            like_count INTEGER,
            comment_count INTEGER,
            PRIMARY KEY (video_id, snapshot_time)
        ) 
    """)


def downgrade() -> None:
    op.execute("DROP TABLE video_snapshots")
