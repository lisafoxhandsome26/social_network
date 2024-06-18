import pytest

from database import dao
from test_data import tweets_1, tweets_2, check_likes
from tests.serializers import serializer_follow, serializer
from conftest import conn_db


@pytest.mark.parametrize(
    "user, result",
    [
        (5, [5, "Александр", "test"]),
        (6, [6, "Богдан", "any"]),
        (7, [7, "Михаил", "git"]),
        (8, [8, "Виктор", "branch"]),
    ],
)
async def test_create_users(user, result):
    """Тест для создания пользователей"""
    await dao.create_users()
    data = await dao.get_user_by_id(id_user=user)
    if data:
        assert data.id == result[0]
        assert data.name == result[1]
        assert data.api_key == result[2]
    else:
        assert data is None


class TestCheckUsers:
    """Набор тестов проверяющих получение пользователя"""

    @pytest.mark.parametrize(
        "key, result", [("reises", None), ("rise", [2, "Алина", "rise"])]
    )
    async def test_check_user(self, key, result):
        """Тест для получения пользователя"""
        data = await dao.check_user(api_key=key)
        if data:
            assert data.id == result[0]
            assert data.name == result[1]
            assert data.api_key == result[2]
        else:
            assert data is result

    @pytest.mark.parametrize(
        "key, result",
        [
            ("bitse", None),
            ("bit", [1, "Марина", "bit", [{"id": 2, "name": "Алина"}], []]),
        ],
    )
    async def test_check_and_get_user(self, key, result):
        """Тест для получения пользователя по его Api-key и подгрузки всех его подписчиков"""
        data = await dao.check_and_get_user(api_key=key)
        if data:
            result_follow = serializer_follow(
                following=data.following, followers=data.followers
            )
            assert data.id == result[0]
            assert data.name == result[1]
            assert data.api_key == result[2]
            assert result_follow[0] == result[3]
            assert result_follow[1] == result[4]
        else:
            assert data is result

    @pytest.mark.parametrize(
        "user, result", [(25, None), (3, [3, "Анастасия", "tigr", [], []])]
    )
    async def test_get_user_by_id(self, user, result):
        """Тест для получения пользователя по его id и подгрузки всех его подписчиков"""
        data = await dao.get_user_by_id(id_user=user)
        if data:
            result_follow = serializer_follow(
                following=data.following, followers=data.followers
            )
            assert data.id == result[0]
            assert data.name == result[1]
            assert data.api_key == result[2]
            assert result_follow[0] == result[3]
            assert result_follow[1] == result[4]
        else:
            assert data is result


class TestFollowUsers:
    """Набор тестов проверяющих подписку и отписку пользователей"""

    @pytest.mark.parametrize(
        "following, user, result",
        [(4, 1, [{4, "Екатерина"}]), (3, 3, False), (25, 3, False)],
    )
    async def test_follow_user(self, following, user, result):
        """Тест для подписки пользователей"""
        data = await dao.follow_user(id_following=following, user_me=user)
        check_data = await dao.get_user_by_id(id_user=user)
        if data:
            assert data is True
            assert [{col.id, col.name} for col in check_data.followers] == result
        else:
            assert data is False

    @pytest.mark.parametrize(
        "following, user_id, result",
        [
            ("bit", 4, [{2, "Алина"}]),
            ("bit", 2, []),
            ("bit", 25, []),
        ],
    )
    async def test_unfollow_user(self, following, user_id, result):
        """Тест для отписки пользователей"""
        user = await dao.check_and_get_user(api_key=following)
        data = await dao.unfollow_user(id_following=user_id, user_me=user)
        check_data = await dao.check_and_get_user(api_key=following)
        assert data is True
        assert [{col.id, col.name} for col in check_data.following] == result


class TestTweets:
    """Набор тестов для проверки Твитов"""

    async def test_select_tweets(self):
        """Тест для получения Твитов"""
        tweets = await dao.select_tweets()
        data = serializer(tweets)
        assert data == []

    @pytest.mark.parametrize(
        "text, id_user, media, tweet, result",
        [
            ("some content", 1, ["/link/to/image.JPEG"], 1, tweets_1),
            ("some content 2", 1, None, 2, tweets_2),
        ],
    )
    async def test_insert_tweet(self, text, id_user, media, tweet, result):
        """Тест для добавления Твита"""
        tweet_id = await dao.insert_tweet(
            content=text, id_user=id_user, media_links=media
        )
        tweets = await dao.select_tweets()
        data = serializer(tweets)
        assert tweet_id == tweet
        assert data == result

    async def test_add_like(self):
        """Тест для добавления Лайка"""
        await dao.add_like(tweet_id=1, name="Марина", user_id=1)
        tweets = await dao.select_tweets()
        data = serializer(tweets)
        assert data[:1] == check_likes

    async def test_remove_like(self):
        """Тест для удаления Лайка"""
        await dao.remove_like(tweet_id=1, user_id=1)
        tweets = await dao.select_tweets()
        data = serializer(tweets)
        assert data[0] == tweets_1[0]

    @pytest.mark.parametrize(
        "tweet_id, user_id, result",
        [(1, 1, ["/link/to/image.JPEG"]), (2, 2, []), (25, 25, [])],
    )
    async def test_delete_tweet(self, tweet_id, user_id, result):
        """Тест для удаления Твита"""
        data = await dao.delete_tweet(tweet_id=tweet_id, user_id=user_id)
        assert data == result

    async def test_clean_database(self):
        await conn_db()
