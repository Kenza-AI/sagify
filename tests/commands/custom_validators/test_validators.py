import click
import pytest

from sagify.commands.custom_validators.validators import validate_tags


@pytest.mark.parametrize("test_input,expected", [
    (
        "key1=value1;key2=3",
        [
            {'Key': "key1", 'Value': "value1"},
            {'Key': "key2", 'Value': "3"}
        ]
    ),
    (
        "key1=value1",
        [
            {'Key': "key1", 'Value': "value1"}
        ]
    )
])
def test_validate_tags_happy_case(test_input, expected):
    assert validate_tags(ctx=None, param=None, value=test_input) == expected


@pytest.mark.parametrize("test_input", [
    "key1=value1;;key2=3",
    "key1==value1;"
])
def test_validate_tags_invalid_input(test_input):
    with pytest.raises(click.BadParameter):
        assert validate_tags(ctx=None, param=None, value=test_input)
