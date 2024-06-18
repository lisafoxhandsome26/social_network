from database.core import session
from database.models import User, Tweet, Like, Media, follow
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload


async def create_users() -> None:
    if not await check_user(api_key="test"):
        user = User(name="Александр", api_key="test")
        user_2 = User(name="Богдан", api_key="any", followers=[user])
        user.following = [user_2]
        user_3 = User(name="Михаил", api_key="git")
        user_4 = User(name="Виктор", api_key="branch")
        async with session() as sos:
            sos.add_all([user, user_2, user_3, user_4])
            await sos.commit()


async def check_user(api_key: str) -> User:
    stm = select(User).filter_by(api_key=api_key)
    async with session() as sos:
        result = await sos.execute(stm)
        return result.scalars().one_or_none()


async def check_and_get_user(api_key: str) -> User:
    stm = (
        select(User)
        .options(selectinload(User.followers), selectinload(User.following))
        .filter_by(api_key=api_key)
    )
    async with session() as sos:
        result = await sos.execute(stm)
        return result.scalars().one_or_none()


async def get_user_by_id(id_user: int) -> User:
    stm = (
        select(User)
        .options(selectinload(User.followers), selectinload(User.following))
        .filter_by(id=id_user)
    )
    async with session() as sos:
        result = await sos.execute(stm)
        return result.scalars().one_or_none()


async def follow_user(id_following: int, user_me: int):  # Надо как то доработать
    user_following = select(User).filter_by(id=id_following)
    async with session() as sos:
        result = await sos.execute(user_following)
        following_u = result.scalars().first()

        if following_u:
            if following_u.id == user_me:
                return False
            new_follow_entry = follow.insert().values(
                followers_id=user_me, following_id=following_u.id
            )
            await sos.execute(new_follow_entry)
            await sos.commit()
            return True
        return False


async def unfollow_user(id_following: int, user_me: User):
    stm = delete(follow).filter_by(followers_id=id_following, following_id=user_me.id)
    async with session() as sos:
        await sos.execute(stm)
        await sos.commit()
    return True


async def select_tweets() -> list[Tweet]:
    query = select(Tweet).options(
        selectinload(Tweet.author),
        selectinload(Tweet.likes),
        selectinload(Tweet.attachments),
    )
    async with session() as sos:
        result = await sos.execute(query)
        return result.scalars().all()


async def insert_tweet(
    content: str, id_user: int, media_links: list[str] | None
) -> int:
    async with session() as sos:
        async with sos.begin():
            tweet = Tweet(content=content, author_id=id_user)
            sos.add(tweet)
            if media_links:
                list_media = [
                    Media(link=media, tweet_id=tweet.id) for media in media_links
                ]
                tweet.attachments = list_media
                sos.add_all(list_media)
        await sos.refresh(tweet)
        return tweet.id


async def delete_tweet(tweet_id: int, user_id: int):
    stm_media = select(Media.link).filter_by(tweet_id=tweet_id)
    stm_tweet = delete(Tweet).filter_by(id=tweet_id, author_id=user_id)
    async with session() as sos:
        list_media = await sos.execute(stm_media)
        await sos.execute(stm_tweet)
        await sos.commit()
        return list_media.scalars().all()


async def add_like(tweet_id: int, name: str, user_id: int) -> None:
    like = Like(tweet_id=tweet_id, name=name, user_id=user_id)
    async with session() as sos:
        async with sos.begin():
            sos.add(like)
            await sos.commit()


async def remove_like(tweet_id: int, user_id: int) -> None:
    stm = delete(Like).filter_by(tweet_id=tweet_id, user_id=user_id)
    async with session() as sos:
        await sos.execute(stm)
        await sos.commit()