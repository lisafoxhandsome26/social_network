from database.models import User
from schemases.schemases import TweetSchema


def serializer(tweets):
    return [
        TweetSchema.model_validate(obj, from_attributes=True).dict() for obj in tweets
    ]


def serializer_follow(following: list[User | None], followers: list[User | None]):
    following = [{"id": user.id, "name": user.name} for user in following]
    followers = [{"id": user.id, "name": user.name} for user in followers]
    return following, followers
