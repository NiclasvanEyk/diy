"""
Honestly, this is just an experiment. Wrote some Rust, liked the error
handling, and tried to replicate it in Python. The CLI is considered private
anyways, so trying out new stuff here seems fine.
"""

from dataclasses import dataclass


@dataclass
class Ok[T]:
    value: T


@dataclass
class Err[E]:
    error: E


type Result[T, E] = Ok[T] | Err[E]
