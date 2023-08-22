

import re


def validate_password(password):
    regex_password = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"

    # compiling regex
    pattern_password = re.compile(regex_password)

    # searching regex
    valid = re.search(pattern_password, password)

    return bool(valid)


def validate_email(email):
    pattern_email = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu)"
    validated_email = re.search(pattern_email, email)
    return validated_email
