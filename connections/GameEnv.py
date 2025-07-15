import json
import random
from pydantic import BaseModel, Field
from typing import List, Tuple, Dict, Optional
from DataModels import WordGroups, ConnectionsEntry
from DataModels import GroupGuess, GameState


class GameEnv:
    def __init__(self):
        self.game = get_random_game()
        self.state = GameState(num_attempts=0, previous_attempts=[], solved_groups=[])

    def reset(self):
        self.game = get_random_game()
        self.state = GameState(num_attempts=0, previous_attempts=[], solved_groups=[])
        return self.state

    def step(self, action):
        min_missed_by = 4
        min_missed_group = None

        # Update state based on action
        self.state.num_attempts += 1

        # Find the group that best matches the action
        for group in self.game.groups:
            if group in self.state.solved_groups:
                continue

            missed_by = len(set(action + group.words)) - 4
            if missed_by < min_missed_by:
                min_missed_by = missed_by
                min_missed_group = group

        if min_missed_group in self.state.solved_groups:
            reward = -1.0

        # If no groups were available to check (all solved), this is an invalid action
        if min_missed_group is None:
            # Don't add to previous attempts, just return current state with negative reward
            reward = -1.0
        # Correct guess
        elif min_missed_by == 0:
            self.state.solved_groups.append(min_missed_group)
            self.state.previous_attempts.append(
                GroupGuess(
                    group=action,
                    missed_by=0,
                    difficulty=min_missed_group.difficulty,
                )
            )
            reward = (
                min_missed_group.difficulty
            )  # Reward based on difficulty of the group
        # Incorrect guess
        else:
            self.state.previous_attempts.append(
                GroupGuess(
                    group=action,
                    missed_by=-min_missed_by,
                    difficulty=min_missed_group.difficulty,
                )
            )
            reward = -0.2 * self.state.num_attempts

        # Check if game is done
        done = False
        info = {}

        # Game is won if all groups are solved
        if len(self.state.solved_groups) == 4:
            done = True
            info["win"] = True
        # Game is lost if max attempts reached
        elif self.state.num_attempts >= 4:
            done = True
            info["win"] = False

        return self.state, reward, done, info

    def render(self, mode="human"):
        """Display current game state"""
        print(f"Attempts: {self.state.num_attempts}/4")
        print(f"Solved groups: {len(self.state.solved_groups)}/4")
        for i, attempt in enumerate(self.state.previous_attempts):
            status = "✓" if attempt.missed_by == 0 else "✗"
            print(f"Attempt {i+1}: {attempt.group} - {status}")

    def print_game(self):
        """Print the current game groups"""
        print("Current Game Groups:")
        for group in self.game.groups:
            print(
                f"Connection: {group.connection}, Words: {', '.join(group.words)}, Difficulty: {group.difficulty}"
            )

    def close(self):
        pass


def get_random_game():
    with open("connections/games/AllConnections.json", "r") as f:
        import json

        connections = json.load(f)

    return ConnectionsEntry(**random.choice(connections))
