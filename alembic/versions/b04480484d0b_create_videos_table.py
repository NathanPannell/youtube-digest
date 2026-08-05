"""create videos table

Revision ID: b04480484d0b
Revises: 7325fcffd0cc
Create Date: 2026-07-27 17:01:36.813596

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b04480484d0b"
down_revision: Union[str, Sequence[str], None] = "7325fcffd0cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE videos (
            video_id VARCHAR(11) PRIMARY KEY,
            channel_id VARCHAR(24) REFERENCES channels(channel_id),
            published_at TIMESTAMPTZ NOT NULL,
            title VARCHAR(128) NOT NULL,
            duration VARCHAR(11) NOT NULL,
            view_count BIGINT,
            like_count BIGINT,
            comment_count BIGINT
        )
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE videos")
