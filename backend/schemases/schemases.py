from pydantic import BaseModel, field_serializer


class UserSchema(BaseModel):
    id: int
    name: str


class MediaSchema(BaseModel):
    link: str


class LikeSchema(BaseModel):
    user_id: int
    name: str


class TweetSchema(BaseModel):
    id: int
    content: str
    author: UserSchema
    attachments: list["MediaSchema"] | None
    likes: list["LikeSchema"] | None

    @field_serializer('attachments')
    def serialize_attachments(self, attachments: list["MediaSchema"]):
        return [media.link for media in attachments]
