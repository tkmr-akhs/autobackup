"""Module of utilities related to dict"""


def recursive_merge(
    target_dict: dict[str], source_dict: dict[str], overwrite_none: bool = False
) -> None:
    """Recursively merge source dict into target dict.

    Args:
        target_dict (dict[str]):\
            The target dictionary that will be modified and receive the merged result.
        source_dict (dict[str]):\
            The source dictionary whose values will be merged into the target dictionary.
        overwrite_none (bool):\
            Whether or not to overwrite with None when the source dictionary contains None.

    Note:
        This function has side effects and modifies the input dictionary "target_dict".
    """
    for key, value in source_dict.items():
        if (
            key in target_dict
            and isinstance(value, dict)
            and isinstance(target_dict[key], dict)
        ):
            recursive_merge(target_dict[key], source_dict[key])
        else:
            if not value is None or overwrite_none:
                target_dict[key] = value
