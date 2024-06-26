from typing import Annotated
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey, Table, Column, Integer

pk = Annotated[int, mapped_column(primary_key=True, index=True)]
date = Annotated[datetime, mapped_column(default=datetime.utcnow)]
str_255 = Annotated[str, 255]
str_500 = Annotated[str, 500]


class Base(DeclarativeBase, AsyncAttrs):
    type_annotation_map = {
        str_255: String(255),
        str_500: String(500)
    }


follow = Table("follow",
               Base.metadata,
               Column("followers_id", Integer, ForeignKey('user.id', ondelete="CASCADE")), # Подписчики (люди которые подписуются на меня)
               Column("following_id", Integer, ForeignKey('user.id', ondelete="CASCADE"))  # Подписки (Люди которых я выбрал себе)
               )


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name: Mapped[str_255]
    api_key: Mapped[str_255]

    followers: Mapped[list["User"] | None] = relationship(  # Подписчики (люди которые выбирают меня)
        "User",
        secondary=follow,
        primaryjoin=id == follow.c.followers_id,
        secondaryjoin=id == follow.c.following_id,
        back_populates="following",
    )
    following: Mapped[list["User"] | None] = relationship(  # Подписки (Люди которых я выбрал себе)
        "User",
        secondary=follow,
        primaryjoin=id == follow.c.following_id,
        secondaryjoin=id == follow.c.followers_id,
        back_populates="followers",
    )

    def __repr__(self):
        return f"User[{self.name}]"


class Like(Base):
    __tablename__ = "Like"

    id: Mapped[pk]
    created_at: Mapped[date]
    name: Mapped[str_255]
    user_id: Mapped[int]
    tweet_id: Mapped[int] = mapped_column(ForeignKey("Tweet.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"Like[{self.name}]"


class Media(Base):
    __tablename__ = "Media"

    id: Mapped[pk]
    link: Mapped[str]
    tweet_id: Mapped[int] = mapped_column(ForeignKey("Tweet.id", ondelete="CASCADE"))

    def __repr__(self):
        return f"Media[{self.link}]"


class Tweet(Base):
    __tablename__ = "Tweet"

    id: Mapped[pk]
    content: Mapped[str_500]
    created_at: Mapped[date]
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    author: Mapped[User] = relationship()
    attachments: Mapped[list[Media] | None] = relationship()
    likes: Mapped[list[Like] | None] = relationship()

    def __repr__(self):
        return f"Tweet[{self.content}]"
