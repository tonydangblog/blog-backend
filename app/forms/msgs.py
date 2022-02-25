"""Form Error Messages."""


def email_msg() -> str:
    """Error message for Email() validator."""
    return "Whoops, it looks like you did not enter a valid email!"


def required_msg(field_name: str) -> str:
    """Error message for DataRequired() validator."""
    return f"Whoops, it looks like you forgot to enter your {field_name}!"


def length_msg(field_name: str, min_len: int, max_len: int) -> str:
    """Error message for Length() validator."""
    return (
        f"Whoops, the {field_name} entered must be between {min_len} to {max_len} "
        "characters."
    )
