import textwrap
import re
from typing import TextIO, List, Union, Iterable
import keyword
from collections import OrderedDict

from json2pyclass.json_pyclass_config import JsonPyClassConfig
from json2pyclass.json_schema_parse import ClassDefinition, UnionDefinition, TypeAlias, TypeDefinition


NAME_EXTRACTOR = re.compile(r"^.*\.(.+?)$")
RESERVED_WORDS = set(keyword.kwlist)
IDENTIFIER_RE = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE)
NAMESPACE_EXTRACTOR = re.compile(r"^.*\.([^.]+?)\.([^.]+?)$")


def get_namespace(class_name: str) -> str:
    m = NAMESPACE_EXTRACTOR.match(class_name)

    if not m:
        return class_name.split(".")[0]

    return m.group(1)


def filter_classes(found_items: List[Union[ClassDefinition, UnionDefinition, TypeAlias]])\
        -> Iterable[Union[ClassDefinition, UnionDefinition, TypeAlias]]:
    result = OrderedDict()

    for item in found_items:
        cn = class_name(item.class_name)

        if cn not in result:
            result[cn] = item
            continue

        # we have a conflict.
        if get_namespace(item.class_name) == "v1":
            result[cn] = item

    return result.values()


def write_classes(config: JsonPyClassConfig,
                  found_items: List[Union[ClassDefinition, UnionDefinition, TypeAlias]]) -> None:
    unique_classes = filter_classes(found_items)

    with open(config.output_name, "wt", encoding="utf-8") as f:
        # FIXME: have only the required imports
        f.write("from typing import Optional, Union, List, Dict, Any\n\n")

        for c in unique_classes:
            if isinstance(c, ClassDefinition):
                write_class(config, f, c)
            elif isinstance(c, UnionDefinition):
                write_union(config, f, c)
            elif isinstance(c, TypeAlias):
                write_alias(config, f, c)
            else:
                raise Exception(f"Unsupported item {c}")


def write_class(config: JsonPyClassConfig,
                f: TextIO,
                c: ClassDefinition) -> None:
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

            f.write(f"    {property_name}: {typedef_to_str(config, cproperty.type)}\n")
    except Exception as e:
        raise Exception(f"Unable to write class {c.class_name}", e)


def write_union(config: JsonPyClassConfig,
                f: TextIO,
                c: UnionDefinition) -> None:
    try:
        typedef_str_items = []

        for item in c.items:
            typedef_str_items.append(typedef_to_str(config, item))

        union_def = "Union[" + ", ".join(typedef_str_items) + "]"

        f.write(f"{class_name(c.class_name)} = {union_def}\n")
    except Exception as e:
        raise Exception(f"Unable to write union {c.class_name}", e)


def write_alias(config: JsonPyClassConfig,
                f: TextIO,
                c: TypeAlias) -> None:
    f.write(f"{class_name(c.class_name)} = {typedef_to_str(config, c.type_definition)}\n")


def typedef_to_str(config: JsonPyClassConfig,
                   t: TypeDefinition) -> str:
    clazz_type = as_type(t)

    if t.required or not config.optionals:
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

