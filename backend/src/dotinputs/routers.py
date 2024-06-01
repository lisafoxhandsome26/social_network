from os import makedirs, path, remove
from asyncio import run as async_run
from typing import Annotated
from time import sleep
from fastapi import APIRouter, Header, Body, UploadFile
from database.core import create_tables, session
from schemases.schemases import TweetSchema, UserSchema
from config.settings import env
from database.dao import (
    create_users,
    check_and_get_user,
    select_tweets,
    insert_tweet,
    add_like,
    remove_like,
    delete_tweet,
    get_user_by_id
)


router = APIRouter(prefix="/api")
makedirs(env.DIR_IMAGES, exist_ok=True)


@router.on_event("startup")
async def startup():
    sleep(15)
    await create_tables()
    await create_users()


@router.get("/tweets")
async def list_tweets(api_key: Annotated[str | None, Header()]):

    user = async_run(check_and_get_user(api_key))
    if user:
        orm_obj = async_run(select_tweets())
        data = [TweetSchema.model_validate(obj, from_attributes=True).dict() for obj in orm_obj]
        return {"result": True, "tweets": data}
    return {"result": False}


@router.post("/tweets")
async def add_tweet(api_key: Annotated[str | None, Header()], data=Body()):

    user = async_run(check_and_get_user(api_key))
    if user:
        tweet_data: str = data.get("tweet_data")
        tweet_media_ids: list[str] | None = data.get("tweet_media_ids")
        tweet_id = insert_tweet(content=tweet_data, id_user=user.id, media_links=tweet_media_ids)
        return {"result": True, "tweet_id": tweet_id}
    return {"result": False}


@router.post("/medias")
async def add_medias(api_key: Annotated[str | None, Header()], file: UploadFile):

    user = async_run(check_and_get_user(api_key))
    if user:
        file_location = path.join(env.DIR_IMAGES, "_".join([api_key, file.filename]))
        with open(file_location, "wb") as f:
            f.write(await file.read())
        return {"result": True, "media_id": file_location}
    return {"result": False}


@router.post("/tweets/{tweet_id}/likes")
async def add_like_tweet(api_key: Annotated[str | None, Header()], tweet_id: int):

    user = async_run(check_and_get_user(api_key))
    if user:
        async_run(add_like(tweet_id=tweet_id, user_id=user.id, name=user.name))
        return {"result": True}
    return {"result": False}


@router.delete("/tweets/{tweet_id}/likes")
async def delete_like_tweet(api_key: Annotated[str | None, Header()], tweet_id: int):

    user = check_and_get_user(api_key)
    if user:
        async_run(remove_like(tweet_id=tweet_id, user_id=user.id))
        return {"result": True}
    return {"result": False}


@router.delete("/tweets/{tweet_id}")
async def delete_tweet_by_user(api_key: Annotated[str | None, Header()], tweet_id: int):

    user = async_run(check_and_get_user(api_key))
    if user:
        result = async_run(delete_tweet(tweet_id=tweet_id, user_id=user.id))
        if result:
            for image in result:
                remove(image)
        return {"result": result}
    return {"result": False}


@router.get("/users/me")
async def get_user_profile(api_key: Annotated[str | None, Header()]):

    user = async_run(check_and_get_user(api_key))
    if user:
        data = UserSchema.model_validate(user, from_attributes=True).dict()
        return {"result": True, "user": data}
    return {"result": False}


@router.get("/users/{user_id}")
async def get_profile_another_user(api_key: Annotated[str | None, Header()], user_id: int):

    if async_run(check_and_get_user(api_key=api_key)):
        user = async_run(get_user_by_id(id_user=user_id))
        if user:
            data = UserSchema.model_validate(user, from_attributes=True).dict()
            return {"result": True, "user": data}
        return {"result": False}
    return {"result": False}


# @router.post("/users/{user_id}/follow")
# async def follow(api_key: Annotated[str | None, Header()], user_id: int):
#     """Пользователь может зафоловить другого пользователя."""
#     user = check_and_get_user(api_key)
#     if user:
#         res = follow_user(id_following=user_id, user_me=user)
#         return {"result": res}
#     return {"result": False}
#
#
# @router.delete("/users/{follower_id}/follow")
# async def unfollow(api_key: Annotated[str | None, Header()], follower_id: int):
#     """Пользователь может убрать подписку на другого пользователя."""
#     user = check_and_get_user(api_key)
#     if user:
#         res = unfollow_user(id_following=follower_id, user_me=user)
#         return {"result": res}
#     return {"result": False}
