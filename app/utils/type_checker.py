from typing import Any, Tuple, List, Type


def check_type(variable: Any, expected_type: Type):
    if type(variable) is not expected_type:
        raise RuntimeError(
            f'Unexpected type for variable {variable}. Expected: {expected_type}, Actual: {type(variable)}'
        )


def check_batch_type(to_check: List[Tuple[Any, Type]]):
    for t in to_check:
        check_type(t[0], t[1])
