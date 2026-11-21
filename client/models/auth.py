from pydantic import BaseModel


class TokenOwner(BaseModel):
    username: str
    token: str
    expiration: int


class CheckResponse(BaseModel):
    Item: TokenOwner
