import base64
from typing import Mapping

import faker


def check_types(
    checking_obj: Mapping,
    expected_obj: Mapping,
) -> bool:
    if checking_obj.keys() != expected_obj.keys():
        return False
    return all(
        [
            isinstance(value, expected_obj.get(key))  # type: ignore
            for key, value in checking_obj.items()
        ]
    )


def generate_base64_image_string() -> str:
    fake = faker.Faker()
    return ''.join(
        (
            'data:image/png;base64,',
            base64.b64encode(fake.image()).decode('utf-8'),
        )
    )
