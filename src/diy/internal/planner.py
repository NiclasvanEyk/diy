from collections.abc import Callable
from inspect import Parameter, getfullargspec, signature
from typing import Any

from diy.errors import (
    MissingConstructorKeywordTypeAnnotationError,
    UninstanciableTypeError,
    UnsupportedParameterTypeError,
)
from diy.internal.validation import assert_is_typelike
from diy.internal.validation import assert_is_typelike
from diy.plan import (
    BuilderBasedResolutionPlan,
    BuilderParameterResolutionPlan,
    CallableResolutionPlan,
    DefaultParameterResolutionPlan,
    InferenceBasedResolutionPlan,
    InferenceParameterResolutionPlan,
)
from diy.specification import Specification


class Planner:
    """
    Looks at a type or function and constructs a plan how to build or call it.
    The plan is based upon the spec provided to the builder upon instantiation.
    """

    def __init__(self, spec: Specification) -> None:
        self.spec = spec

    def plan[T](
        self, subject: type[T]
    ) -> BuilderBasedResolutionPlan[T] | InferenceBasedResolutionPlan[T]:
        """
        Plans the resolution of an instance of the type.
        """
        assert_is_instantiable(subject)

        # maybe we already know how to build this
        builder = self.spec.builders.get(subject)
        if builder is not None:
            return BuilderBasedResolutionPlan(subject, builder)

        # if not, try to resolve it based on the knowledge we have
        plan = InferenceBasedResolutionPlan(subject)
        self._fill_plan_based_on_inference(subject.__init__, plan)
        return plan

    def _fill_plan_based_on_inference[**P, T](
        self,
        subject: Callable[..., Any],
        parent: InferenceParameterResolutionPlan[T]
        | InferenceBasedResolutionPlan[T]
        | CallableResolutionPlan[P, T],
    ) -> None:
        depth = -1
        if isinstance(parent, InferenceParameterResolutionPlan):
            depth = parent.depth

        for name, parameter in signature(subject, eval_str=True).parameters.items():
            # TODO: This can definitely be done better
            if name == "self" or name[0:1] == "*" or name[0:2] == "**":
                continue

            if parameter.kind in [Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD]:
                # TODO: Maybe introduce a way of supplying these?
                #       We skip them for now, since the empty constructor
                #       has these at the end.
                continue

            if parameter.kind not in [
                Parameter.KEYWORD_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
            ]:
                # HINT: Take a look at Signature.apply_defaults for supporting
                #       positional argument defaults
                # TODO: Support other cases
                raise UnsupportedParameterTypeError

            print(parameter)

            # If a specific type requests a parameter, we can ask if we have a
            # partial builder for it. Since this is the most specific
            # instruction, we check it first.
            #
            # TODO: Maybe we can support this also for functions?
            #       E.g. when function XY needs param Z, then supply it via the
            #       partial builder. Maybe we could also **only** deal with
            #       functions, since abstract.__init__ is also just a function.
            if isinstance(
                parent, InferenceParameterResolutionPlan | InferenceBasedResolutionPlan
            ):
                parent_type = parent.type
                if isinstance(parent_type, type):
                    partial_builder = self.spec.partials.get(parent_type, name)
                    if partial_builder is not None:
                        parent.parameters.append(
                            BuilderParameterResolutionPlan(
                                name,
                                depth + 1,
                                type=parent_type,
                                builder=partial_builder,
                            )
                        )
                        continue
            else:
                print(parent)

            # If the parameter has a default, it is preferrable
            if parameter.default is not Parameter.empty:
                parent.parameters.append(
                    DefaultParameterResolutionPlan(
                        name, depth + 1, type(parameter.default)
                    )
                )
                continue

            # From here on out, we rely on type annotations. If the type is
            # annotated, we can run inference and look if we can build the
            # annotated type from the spec. If not, there is hardly anything we
            # can do.
            abstract = parameter.annotation
            if abstract is Parameter.empty:
                # TODO: Maybe don't throw, but annotate the step and plan to be
                #       not executable. Then we could report *all* X errors at
                #       once, instead of bailling X times one after another.
                raise MissingConstructorKeywordTypeAnnotationError(abstract, name)

            assert_is_typelike(abstract)

            # If the user told us to resolve this type in a specific way, use it
            builder = self.spec.builders.get(abstract)
            if builder is not None:
                parent.parameters.append(
                    BuilderParameterResolutionPlan(
                        parameter.name, depth + 1, subject, builder
                    )
                )
                continue

            # As a last fallback, we inspect the constructor of the type in
            # question and see if we can build all parameters. This recurses
            # potentially multiple levels deep.
            #
            # TODO: Detect loops, maybe using the plan?
            plan = InferenceParameterResolutionPlan(name, depth + 1, abstract)
            parent.parameters.append(plan)
            print(f"inferring '{abstract}' for parameter {name}...")
            self._fill_plan_based_on_inference(abstract, plan)

    def _get_requestor(self, parent: Any) -> type[Any] | None:
        """
        Plans the resolution of an parameters for a function.
        """
        if isinstance(parent, InferenceParameterResolutionPlan):
            return parent.type
        # TODO: This makes sense, if we support partials for bare functions
        # if isinstance(parent, CallableResolutionPlan):
        #     return parent.subject
        return None

    def plan_call[**P, R](
        self, subject: Callable[P, R]
    ) -> CallableResolutionPlan[P, R]:
        plan = CallableResolutionPlan(subject)
        self._fill_plan_based_on_inference(subject, plan)
        return plan


def assert_is_instantiable(abstract: type[Any]) -> None:
    # TODO: Maybe we can also use `signature` here
    spec = getfullargspec(abstract.__init__)
    if len(spec.args) <= 0:
        raise UninstanciableTypeError(abstract)

    if spec.args[0] != "self":
        raise UninstanciableTypeError(abstract)
