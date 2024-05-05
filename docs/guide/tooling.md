# Tooling

This part covers various techniques and tools that help you to be more confident that your code does not crash at runtime with relatively low effort.

## Motivation

Python is a very dynamic programming language.
By default, nothing prevents you from writing code like this

```python
def compute_average(items) -> str:
    print(f"DEBUG: {items}")
    return sum(items[::-1] / len(items))
```

This function has no documentation and even annotates a wrong return type, which has no effect at runtime.
It will crash if you pass it either an empty list, something that is not a list at all, or something that can't be turned into a string.
It also crashes at runtime, since you can't divide a builtin Python `list`, this is something only third-party libraries such as numpys `np.array`s support.

Manual code review processes and writing automated tests can prevent such issues to some extend, but we want to focus on a different solution here:
**static and dynamic analysis of the program, _before_ it is deployed to production**.
`diy` was written with these processes in mind.

!!! note
    Please still practise code review and write tests!
    Just because tools exist that can help you rely less on them, they still catch bugs that no automated analysis could ever catch.
    Most importantly, they can verify business logic.

## Type Checker

The introductory example had a wrong return type annotation and did not specify the type of the `items` argument.
**Type Checkers** like Mypy or Pyright can scan your code and prove that it will crash at runtime, without actually running it.

Hovever, you need to document your code properly to reap their benefits.
Nothing can help you if you write code like this

```python
def has_student_passed(student, grades, minimum): ...
```

`grades` here could be eveything:

- A class containing information about the student, where the actual grades need to be extracted from a property
- A list of numbers representing the grades of the student
- A parsed CSV of the grades of the whole class

But if we annotate everything correctly:

```python
def has_student_passed(student: Student, grades: list[float], minimum: float) -> bool: ...
```

now we (and automated tools) at least know, that we want to return a boolean, and that `grades` is a list of floats.
This

```python
def has_student_passed(student: Student, grades: list[float], minimum: float) -> bool:
    log(f"Checking if {student.name} has passed...")
    for grade in grades:
        if grade < minimum:
            return False

    return True
```



### Runtime Type Checkers

## Dynamic Validation

In addition, we highly recommend the `ValidatingContainer` or to run the
