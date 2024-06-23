import pytest

from diy import Specification
from diy.container.verifying import VerifyingContainer
from diy.errors import FailedToInferDependencyError
from tests.fixtures import ApiClient


class UserService: ...


def test_it_throws_for_unknown_dependencies() -> None:
    spec = Specification()
    spec.add(ApiClient)

    with pytest.raises(FailedToInferDependencyError):
        VerifyingContainer(spec)


def test_it_throws_for_builder_dependencies() -> None:
    spec = Specification()

    @spec.add
    def build_user_service(api: ApiClient) -> UserService:
        return UserService()

    with pytest.raises(FailedToInferDependencyError) as exception:
        VerifyingContainer(spec)

    assert exception.value.subject == ApiClient
