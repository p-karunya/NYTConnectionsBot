from pydantic import BaseModel, Field
from typing import List


class WordGroups(BaseModel):
    connection: str
    difficulty: int = Field(maximum=4, minimum=1)
    words: List[str] = Field(min_length=4, max_length=4)


class ConnectionsEntry(BaseModel):
    id: int
    groups: List[WordGroups] = Field(min_length=4, max_length=4)


class GroupGuess(BaseModel):
    group: List[str] = Field(min_length=4, max_length=4)
    missed_by: int = Field(ge=-4, le=0)
    difficulty: int


class GameState(BaseModel):
    num_attempts: int = Field(ge=0, le=4, default=0)
    previous_attempts: List[GroupGuess] = Field(default_factory=list)
    solved_groups: List[str] = Field(default_factory=list)
