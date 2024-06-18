"""Create tables

Revision ID: 15855a8c379b
Revises: 
Create Date: 2024-06-04 12:47:24.059422

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "15855a8c379b"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("api_key", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "Tweet",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Tweet_id"), "Tweet", ["id"], unique=False)
    op.create_table(
        "follow",
        sa.Column("followers_id", sa.Integer(), nullable=True),
        sa.Column("following_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["followers_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["following_id"], ["user.id"], ondelete="CASCADE"),
    )
    op.create_table(
        "Like",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tweet_id"], ["Tweet.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Like_id"), "Like", ["id"], unique=False)
    op.create_table(
        "Media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("link", sa.String(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["tweet_id"], ["Tweet.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Media_id"), "Media", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_Media_id"), table_name="Media")
    op.drop_table("Media")
    op.drop_index(op.f("ix_Like_id"), table_name="Like")
    op.drop_table("Like")
    op.drop_table("follow")
    op.drop_index(op.f("ix_Tweet_id"), table_name="Tweet")
    op.drop_table("Tweet")
    op.drop_table("user")
    # ### end Alembic commands ###