tweets_1 = [
    {
        "attachments": ["/link/to/image.JPEG"],
        "author": {"id": 1, "name": "Марина"},
        "content": "some content",
        "id": 1,
        "likes": [],
    }
]

tweets_2 = [
    {
        "attachments": ["/link/to/image.JPEG"],
        "author": {"id": 1, "name": "Марина"},
        "content": "some content",
        "id": 1,
        "likes": [],
    },
    {
        "attachments": [],
        "author": {"id": 1, "name": "Марина"},
        "content": "some content 2",
        "id": 2,
        "likes": [],
    },
]

check_likes = [
    {
        "attachments": ["/link/to/image.JPEG"],
        "author": {"id": 1, "name": "Марина"},
        "content": "some content",
        "id": 1,
        "likes": [{"name": "Марина", "user_id": 1}],
    }
]

data_user = {
    "result": True,
    "user": {
        "followers": [],
        "following": [{"id": 2, "name": "Алина"}],
        "id": 1,
        "name": "Марина",
    },
}

data_user_by_id = {
    "result": True,
    "user": {
        "followers": [{"id": 1, "name": "Марина"}],
        "following": [],
        "id": 2,
        "name": "Алина",
    },
}
