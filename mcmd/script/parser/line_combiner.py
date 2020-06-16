from typing import List

from mcmd.script.model.lines import Line


def _ends_with_continuation_symbol(string: str) -> bool:
    return string.endswith(" \\") or string.endswith("\t\\")


def _strip_continuation_symbol(string: str) -> str:
    return string[:-1].strip()


def combine_multi_lines(lines: List[str]) -> List[Line]:
    """
    Combines multi-lines (lines that end with '\') into single Line objects.
    """

    combined_lines = list()

    if _ends_with_continuation_symbol(lines[-1]):
        lines[-1] = _strip_continuation_symbol(lines[-1])

    # iterate the lines backwards
    for i in range(len(lines) - 1, -1, -1):
        if i > 0:
            previous_line = lines[i - 1]
            continued = _ends_with_continuation_symbol(previous_line)
        else:
            continued = False

        if continued:
            # strip the continuation symbol of the previous line and add this line to it
            lines[i - 1] = _strip_continuation_symbol(lines[i - 1]) + ' ' + lines[i]
        else:
            # commit this line
            combined_lines.append(Line(number=i + 1, string=lines[i]))

    combined_lines.reverse()
    return combined_lines
