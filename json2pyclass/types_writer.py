import textwrap
import re
from typing import TextIO, List, Union
import keyword

from json2pyclass.json_schema_parse import ClassDefinition, UnionDefinition, TypeAlias, TypeDefinition


NAME_EXTRACTOR = re.compile(r"^.*\.(.+?)$")
RESERVED_WORDS = set(keyword.kwlist)
IDENTIFIER_RE = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)


def write_classes(output_file: str,
                  found_items: List[Union[ClassDefinition, UnionDefinition, TypeAlias]]) -> None:
    with open(output_file, "wt", encoding="utf-8") as f:
        f.write("from typing import Optional, Union, List, Dict, Any\n\n")
        for c in found_items:
            if isinstance(c, ClassDefinition):
                write_class(f, c)
            elif isinstance(c, UnionDefinition):
                write_union(f, c)
            elif isinstance(c, TypeAlias):
                write_alias(f, c)
            else:
                raise Exception(f"Unsupported item {c}")


def write_class(f: TextIO, c: ClassDefinition) -> None:
    try:
        f.write(f"class {class_name(c.class_name)}:  # {c.class_name}\n")

        if c.description:
            f.write('    """\n')
            f.write(textwrap.indent(c.description, '    ') + "\n")
            f.write('    """\n')

        if not c.properties:
            f.write("    pass\n")
            return

        for property_name, cproperty in c.properties.items():
            if property_name in RESERVED_WORDS:
                f.write("# FIXME: reserved word # ")

            if not IDENTIFIER_RE.match(property_name):
                f.write("# FIXME: wrong name # ")

            f.write(f"    {property_name}: {typedef_to_str(cproperty.type)}\n")
    except Exception as e:
        raise Exception(f"Unable to write class {c.class_name}", e)


def write_union(f: TextIO, c: UnionDefinition) -> None:
    try:
        union_def = "Union[" + ", ".join(map(typedef_to_str, c.items)) + "]"
        f.write(f"{class_name(c.union_name)} = {union_def}\n")
    except Exception as e:
        raise Exception(f"Unable to write union {c.union_name}", e)


def write_alias(f: TextIO, c: TypeAlias) -> None:
    f.write(f"{class_name(c.type_name)} = {typedef_to_str(c.type_definition)}\n")


def typedef_to_str(t: TypeDefinition) -> str:
    clazz_type = as_type(t)

    if t.required:
        return clazz_type

    return f"Optional[{clazz_type}]"


def class_name(s: str) -> str:
    m = NAME_EXTRACTOR.match(s)

    if not m:
        return s

    return m.group(1)


def as_type(self: TypeDefinition) -> str:
    if self.original_type == "string":
        return "str"
    elif self.original_type == "integer":
        return "int"
    elif self.original_type == "float" or self.original_type == "number":
        return "float"
    elif self.original_type == "boolean":
        return "bool"
    elif self.original_type == "array":
        return f"List[{as_type(self.typevar1)}]"
    elif self.original_type == "object":
        return f"Dict[str, {as_type(self.typevar1)}]"
    elif self.original_type == "Any":
        return "Any"
    elif '#' not in self.original_type:
        raise Exception(f"Unsupported base type {self.original_type}")

    return "'" + class_name(self.original_type) + "'"
