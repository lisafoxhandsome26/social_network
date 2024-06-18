from os import path, remove

import pytest

from config.settings import env
from database import dao
from test_data import tweets_1, tweets_2, check_likes, data_user, data_user_by_id
from serializers import serializer
from PIL import Image
from io import BytesIO
from pathlib import Path

from tests.conftest import conn_db


class TestGetUsers:
    """Набор тестов для получения пользователей"""

    @pytest.mark.parametrize(
        "key, result", [("bit", data_user), ("bitter", {"result": False})]
    )
    async def test_get_user_profile(self, ac, key, result):
        """Тест для получения профиля пользователя"""
        response = await ac.get("api/users/me", headers={"api-key": key})
        assert response.status_code == 200
        assert response.json() == result

    @pytest.mark.parametrize(
        "key, user_id, result",
        [
            ("bit", 2, data_user_by_id),
            ("bit", 25, {"result": False}),
            ("bitter", 2, {"result": False}),
        ],
    )
    async def test_get_profile_another_user(self, ac, key, user_id, result):
        """Тест для получения пользователя по его id"""
        response = await ac.get(f"api/users/{user_id}", headers={"api-key": key})
        assert response.status_code == 200
        assert response.json() == result


class TestRoutersTweets:
    """Набор тестов для проверки Твитов"""

    @pytest.mark.parametrize(
        "key, result",
        [
            ("bit", {"result": True, "tweets": []}),
            ("biter", {"result": False}),
        ],
    )
    async def test_list_tweets(self, ac, key, result):
        """Тест для получения спика Твитов"""
        response = await ac.get("api/tweets", headers={"api-key": key})
        assert response.status_code == 200
        assert response.json() == result

    @pytest.mark.parametrize(
        "text, key, media, tweet, result, result_db",
        [
            (
                "some content",
                "bit",
                ["/link/to/image.JPEG"],
                1,
                {"result": True, "tweet_id": 1},
                tweets_1,
            ),
            (
                "some content 2",
                "bit",
                None,
                2,
                {"result": True, "tweet_id": 2},
                tweets_2,
            ),
            ("some content 3", "bitse", None, 3, {"result": False}, tweets_2),
        ],
    )
    async def test_add_tweet(self, ac, text, key, media, tweet, result, result_db):
        """Тест для добавления Твита"""
        response = await ac.post(
            "api/tweets",
            headers={"api-key": key},
            json={"tweet_data": text, "tweet_media_ids": media},
        )
        tweets = await dao.select_tweets()
        result_ser = serializer(tweets)
        assert response.json() == result
        assert result_ser == result_db

    @pytest.mark.parametrize(
        "key, file, result", [("bit", "txt", False), ("bit", "JPEG", True)]
    )
    async def test_medias(self, ac, key, file, result):
        """Тест для отправки изображения"""
        filename = f"new_image.{file}"
        if file == "JPEG":
            img = Image.new("RGB", (10, 10), color="orange")
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format="JPEG")
            file_content = img_byte_arr.getvalue()
            files = {"file": (filename, file_content, "image/JPEG")}
        else:
            file_content = b"Hello, world!"
            files = {"file": (filename, file_content, "text/plain")}

        response = await ac.post("api/medias", headers={"api-key": key}, files=files)
        file_location = path.join(env.DIR_IMAGES, "_".join([key, filename]))
        if file == "JPEG":
            saved_image_path = Path(file_location)
            with open(saved_image_path, "rb") as f:
                saved_image_data = f.read()
                assert saved_image_data == file_content
                assert saved_image_path.exists()
            remove(file_location)
        assert response.status_code == 200
        assert response.json()["result"] == result

    @pytest.mark.parametrize(
        "key, tweet_id, result, result_db",
        [
            ("bit", 1, {"result": True}, check_likes),
            ("biter", 1, {"result": False}, check_likes),
        ],
    )
    async def test_add_like_tweet(self, ac, key, tweet_id, result, result_db):
        """Тест для отправки лайка"""
        response = await ac.post(
            f"api/tweets/{tweet_id}/likes", headers={"api-key": key}
        )
        tweets = await dao.select_tweets()
        result_ser = serializer(tweets)
        assert response.json() == result
        assert result_ser[0] == result_db[0]

    @pytest.mark.parametrize(
        "key, tweet_id, result, result_db",
        [
            ("bit", 1, {"result": True}, tweets_1),
            ("biter", 1, {"result": False}, tweets_1),
        ],
    )
    async def test_delete_like_tweet(self, ac, key, tweet_id, result, result_db):
        """Тест для удаления лайка"""
        response = await ac.delete(
            f"api/tweets/{tweet_id}/likes", headers={"api-key": key}
        )
        tweets = await dao.select_tweets()
        result_ser = serializer(tweets)
        assert response.json() == result
        assert result_ser[0] == result_db[0]

    @pytest.mark.parametrize(
        "key, tweet_id, result, result_db",
        [
            ("bit", 1, {"result": True}, [tweets_2[1]]),
            ("bit", 2, {"result": True}, []),
            ("biter", 1, {"result": False}, []),
        ],
    )
    async def test_delete_tweet_by_user(self, ac, key, tweet_id, result, result_db):
        """Тест для удаления твита"""
        response = await ac.delete(f"api/tweets/{tweet_id}", headers={"api-key": key})
        tweets = await dao.select_tweets()
        result_ser = serializer(tweets)
        assert response.json() == result
        assert result_ser == result_db


class TestRoutersFollow:
    """Набор тестов проверяющих подписку и отписку пользователей"""

    @pytest.mark.parametrize(
        "key, user_id, result, result_db",
        [
            ("bit", 4, {"result": True}, [{4, "Екатерина"}]),
            ("tigr", 3, {"result": False}, []),
            ("tigritz", 25, {"result": False}, []),
        ],
    )
    async def test_follow(self, ac, key, user_id, result, result_db):
        """Тест для подписки пользователей"""
        response = await ac.delete(
            f"api/users/{user_id}/follow", headers={"api-key": key}
        )
        check_data = await dao.check_and_get_user(api_key=key)
        if check_data:
            assert [{col.id, col.name} for col in check_data.followers] == result_db
        assert response.status_code == 200
        assert response.json() == result

    @pytest.mark.parametrize(
        "key, user_id, result, result_db",
        [
            ("bit", 4, {"result": True}, [{2, "Алина"}]),
            ("bit", 2, {"result": True}, []),
            ("bit", 25, {"result": True}, []),
        ],
    )
    async def test_unfollow(self, ac, key, user_id, result, result_db):
        """Тест для отписки пользователей"""
        response = await ac.delete(
            f"api/tweets/{user_id}/follow", headers={"api-key": key}
        )
        check_data = await dao.check_and_get_user(api_key=key)
        if check_data:
            assert [{col.id, col.name} for col in check_data.following] == result_db
        assert response.status_code == 200
        assert response.json() == result
