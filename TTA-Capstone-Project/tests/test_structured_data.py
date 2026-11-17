import pytest

from tta_capstone_project.structured_data import parse_json_reply


@pytest.mark.parametrize(
    "text",
    [
        '["aws s3 ls", "aws ec2 describe-instances"]',
        '\n["aws s3 ls", "aws ec2 describe-instances"]\n',
        '```json\n["aws s3 ls", "aws ec2 describe-instances"]\n```',
    ],
)
def test_parse_json_reply(text):
    assert parse_json_reply(text) == ["aws s3 ls", "aws ec2 describe-instances"]
