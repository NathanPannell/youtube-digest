"""create channels table

Revision ID: 7325fcffd0cc
Revises:
Create Date: 2026-07-27 13:03:53.172555

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7325fcffd0cc"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE channels (
            channel_id VARCHAR(24) PRIMARY KEY,
            title VARCHAR(64) NOT NULL,
            published_at TIMESTAMP NOT NULL,
            url VARCHAR(64) NOT NULL,
            video_count INT NOT NULL,
            uploads_playlist_id VARCHAR(24) NOT NULL,
            tracked_at TIMESTAMP NOT NULL DEFAULT now()
        )
        """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE channels")
