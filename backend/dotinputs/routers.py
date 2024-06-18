from os import makedirs, path, remove
from typing import Annotated

from fastapi import APIRouter, Header, Body, UploadFile

from schemases.schemases import TweetSchema, UserSchema
from config.settings import env
from database import dao


router = APIRouter(prefix="/api")
makedirs(env.DIR_IMAGES, exist_ok=True)


@router.get("/tweets")
async def list_tweets(api_key: Annotated[str | None, Header()]):
    """Получение списка Твитов"""
    user = await dao.check_user(api_key)
    if user:
        orm_obj = await dao.select_tweets()
        data = [
            TweetSchema.model_validate(obj, from_attributes=True).dict()
            for obj in orm_obj
        ]
        return {"result": True, "tweets": data}
    return {"result": False}


@router.post("/tweets")
async def add_tweet(api_key: Annotated[str | None, Header()], data=Body()):
    """Добавление Твита"""
    user = await dao.check_user(api_key)

    if user:
        tweet_data: str = data.get("tweet_data")
        tweet_media_ids: list[str] | None = data.get("tweet_media_ids")
        tweet_id = await dao.insert_tweet(
            content=tweet_data, id_user=user.id, media_links=tweet_media_ids
        )
        return {"result": True, "tweet_id": tweet_id}
    return {"result": False}


@router.post("/medias")
async def add_medias(api_key: Annotated[str | None, Header()], file: UploadFile):
    """Сохранение изображений"""
    user = await dao.check_user(api_key)
    if user:
        if not file.filename.split(".")[1] in ["JPEG", "png", "JPG"]:
            return {"result": False}
        file_location = path.join(env.DIR_IMAGES, "_".join([api_key, file.filename]))
        with open(file_location, "wb") as f:
            f.write(await file.read())

        return {"result": True, "media_id": file_location}
    return {"result": False}


@router.post("/tweets/{tweet_id}/likes")
async def add_like_tweet(api_key: Annotated[str | None, Header()], tweet_id: int):
    """Добавление Лайка"""
    user = await dao.check_user(api_key)
    if user:
        await dao.add_like(tweet_id=tweet_id, user_id=user.id, name=user.name)
        return {"result": True}
    return {"result": False}


@router.delete("/tweets/{tweet_id}/likes")
async def delete_like_tweet(api_key: Annotated[str | None, Header()], tweet_id: int):
    """Удаление лайка"""
    user = await dao.check_user(api_key)
    if user:
        await dao.remove_like(tweet_id=tweet_id, user_id=user.id)
        return {"result": True}
    return {"result": False}


@router.delete("/tweets/{tweet_id}")
async def delete_tweet_by_user(api_key: Annotated[str | None, Header()], tweet_id: int):
    """Удаление твита"""
    user = await dao.check_user(api_key)
    if user:
        result = await dao.delete_tweet(tweet_id=tweet_id, user_id=user.id)
        if result:
            for image in result:
                try:
                    remove(image)
                except FileNotFoundError:
                    return {"result": True}
        return {"result": True}
    return {"result": False}


@router.get("/users/me")
async def get_user_profile(api_key: Annotated[str | None, Header()]):
    """Получение страницы профиля"""
    user = await dao.check_and_get_user(api_key)
    if user:
        data = UserSchema.model_validate(user, from_attributes=True).dict()
        data["followers"] = [{"id": u.id, "name": u.name} for u in user.followers]
        data["following"] = [{"id": u.id, "name": u.name} for u in user.following]
        return {"result": True, "user": data}
    return {"result": False}


@router.get("/users/{user_id}")
async def get_profile_another_user(
    api_key: Annotated[str | None, Header()], user_id: int
):
    """Получение информации об другом пользователе"""
    if await dao.check_user(api_key=api_key):
        user = await dao.get_user_by_id(id_user=user_id)
        if user:
            data = UserSchema.model_validate(user, from_attributes=True).dict()
            data["followers"] = [{"id": u.id, "name": u.name} for u in user.followers]
            data["following"] = [{"id": u.id, "name": u.name} for u in user.following]
            return {"result": True, "user": data}
        return {"result": False}
    return {"result": False}


# Подкоректировано под Frontend (Frontend на подписку отправляет url http://localhost/api/users/user_id/follow метод DELETE)
@router.delete("/users/{user_id}/follow")
async def follow(api_key: Annotated[str | None, Header()], user_id: int):
    """Пользователь может зафоловить другого пользователя."""
    user = await dao.check_user(api_key)
    if user:
        result = await dao.follow_user(id_following=user_id, user_me=user.id)
        return {"result": result}
    return {"result": False}


# Подкоректировано под Frontend (Frontend на удаление подписки отправляет url http://localhost/api/tweets/user_id/follow метод DELETE)
@router.delete("/tweets/{follower_id}/follow")
async def unfollow(api_key: Annotated[str | None, Header()], follower_id: int):
    """Пользователь может убрать подписку на другого пользователя."""
    user = await dao.check_user(api_key)
    if user:
        res = await dao.unfollow_user(id_following=follower_id, user_me=user)
        return {"result": res}
    return {"result": False}
