"""Test the DslParser class."""

import pytest

from src.core.recognition.dsl_parser import DslParser


@pytest.mark.parametrize(
    ("dsl_code", "expected_ast"),
    [
        (
            "<hunt>[param=val]{pluck:data}</hunt>",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [
                    {
                        "type": "beta_bracket",
                        "command": "param",
                        "has_assign": True,
                        "assign_value": "val",
                        "gamma_brackets": [],
                    }
                ],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
        (
            "<hunt>[param=val]{pluck:data}</hunt> EXEC",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [
                    {
                        "type": "beta_bracket",
                        "command": "param",
                        "has_assign": True,
                        "assign_value": "val",
                        "gamma_brackets": [],
                    }
                ],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
        (
            "<hunt>@@target[param=val]{pluck:data}</hunt>",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": True,
                "bridge_target": "target",
                "beta_brackets": [
                    {
                        "type": "beta_bracket",
                        "command": "param",
                        "has_assign": True,
                        "assign_value": "val",
                        "gamma_brackets": [],
                    }
                ],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
        (
            "<hunt>[param=val]{pluck:data}</hunt> EXEC debug=true verbose=false",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [
                    {
                        "type": "beta_bracket",
                        "command": "param",
                        "has_assign": True,
                        "assign_value": "val",
                        "gamma_brackets": [],
                    }
                ],
                "gamma_brackets": [],
                "exec_params": [
                    {
                        "type": "exec_param",
                        "param_name": "debug",
                        "param_value": "true",
                    },
                    {
                        "type": "exec_param",
                        "param_name": "verbose",
                        "param_value": "false",
                    },
                ],
            },
        ),
        (
            "<hunt>[param1=val1][param2=val2]{pluck1:data1}{pluck2:data2}</hunt>",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [
                    {
                        "type": "beta_bracket",
                        "command": "param1",
                        "has_assign": True,
                        "assign_value": "val1",
                        "gamma_brackets": [],
                    },
                    {
                        "type": "beta_bracket",
                        "command": "param2",
                        "has_assign": True,
                        "assign_value": "val2",
                        "gamma_brackets": [],
                    },
                ],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
        (
            "<hunt>(somefunc,arg1,arg2)</hunt>",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
    ],
    ids=[
        "simple_hunt",
        "simple_hunt_with_exec",
        "hunt_with_bridge",
        "hunt_with_exec_params",
        "hunt_with_multiple_brackets",
        "hunt_with_delta_bracket",
    ],
)
def test_parse_happy_path(dsl_code: str, expected_ast: dict) -> None:
    """Test the happy path of the DslParser class.

    This test case tests the happy path of the DslParser class.
    """
    # Arrange
    parser = DslParser()

    # Act
    actual_ast = parser.parse(dsl_code)

    # Assert
    assert actual_ast == expected_ast


@pytest.mark.parametrize(
    ("dsl_code", "expected_ast"),
    [
        (
            "<hunt>",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
        (
            "<hunt>[param]{pluck}</hunt>",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [
                    {
                        "type": "beta_bracket",
                        "command": "param",
                        "has_assign": False,
                        "assign_value": None,
                        "gamma_brackets": [],
                    }
                ],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
        (
            "<hunt>@@target</hunt>",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": True,
                "bridge_target": "target",
                "beta_brackets": [],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
        (
            "<hunt> EXEC",
            {
                "type": "alpha_bracket",
                "command": "hunt",
                "has_bridge": False,
                "bridge_target": None,
                "beta_brackets": [],
                "gamma_brackets": [],
                "exec_params": [],
            },
        ),
    ],
    ids=[
        "empty_hunt",
        "hunt_with_empty_brackets",
        "hunt_with_bridge_only",
        "hunt_with_exec_only",
    ],
)
def test_parse_edge_cases(dsl_code: str, expected_ast: dict) -> None:
    """Test the edge cases of the DslParser class.

    This test case tests the edge cases of the DslParser class.
    """
    # Arrange
    parser = DslParser()

    # Act
    actual_ast = parser.parse(dsl_code)

    # Assert
    assert actual_ast == expected_ast


@pytest.mark.parametrize(
    ("dsl_code", "expected_exception"),
    [
        ("hunt", ValueError),
        ("<hunt", ValueError),
        ("<hunt[param=val]", ValueError),
        ("<hunt>[param=val]{pluck:data", ValueError),
        ("<hunt>[param=val]{pluck:data}</hunt> EXEC debug", ValueError),
    ],
    ids=[
        "no_alpha_bracket",
        "unclosed_alpha_bracket",
        "unclosed_beta_bracket",
        "unclosed_gamma_bracket",
        "invalid_exec_param",
    ],
)
def test_parse_error_cases(dsl_code: str, expected_exception: Exception) -> None:
    """Test the error cases of the DslParser class.

    This test case tests the error cases of the DslParser class.
    """
    # Arrange
    parser = DslParser()

    # Act & Assert
    with pytest.raises(expected_exception):
        parser.parse(dsl_code)
