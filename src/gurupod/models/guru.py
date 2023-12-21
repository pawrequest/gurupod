from sqlmodel import Field, SQLModel


class Guru(SQLModel):
    name: str
    episodes: list[Episode] = Field
    ...