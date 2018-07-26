from dateutil.parser import parse


def try_int(val, default: int):
    try:
        return int(val)
    except:
        return default


def try_date(val, default: str) -> str:
    try:
        parsed_date = parse(val)
        if not parsed_date:
            return default

        return parsed_date.date().isoformat()
    except:
        return default
