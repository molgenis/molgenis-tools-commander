from typing import List, Set, Dict

import attr

from mcmd.script.model.lines import ScriptLine


@attr.s(frozen=True)
class Script:
    lines: List[ScriptLine] = attr.ib()
    _dependencies: Dict[ScriptLine, Set[ScriptLine]] = attr.ib()

    def get_lines_with_dependencies(self, from_line_number: int) -> List[ScriptLine]:
        """
        Gets all the lines in the script from a certain line_number and up. If the lines depend on lines before
        line_number, then those lines will be included as well. This is done recursively, so all dependencies are
        included.
        """
        if from_line_number < 2:
            return list(self.lines)
        else:
            lines_subset = {line for line in self.lines if line.number >= from_line_number}

            print(self._dependencies)
            dependencies = set()
            for line in lines_subset:
                dependencies |= self._get_deep_dependencies(line)

            total_lines = (lines_subset | dependencies)
            return sorted(total_lines, key=lambda l: l.number)

    def _get_deep_dependencies(self, line: ScriptLine) -> Set[ScriptLine]:
        dependencies = set()
        dependencies.add(line)
        for dependency in self._dependencies.get(line, set()):
            dependencies |= self._get_deep_dependencies(dependency)
        return dependencies
