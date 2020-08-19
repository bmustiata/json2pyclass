from typing import Optional, List, Dict, Union, TypeVar

import yamldict


_S = TypeVar("_S")


class TypeDefinition:
    def __init__(self,
                 type: str) -> None:
        self.required = False
        self.original_type = type
        self.typevar1: Optional['TypeDefinition'] = None

    def with_typevar(self: _S, t: str) -> _S:
        self.typevar1 = TypeDefinition(type=t)
        return self


class UnionDefinition:
    def __init__(self, name: str, *items) -> None:
        self.class_name = name
        self.items: List[TypeDefinition] = list(items)
        self.description: Optional[str] = None


class TypeAlias:
    def __init__(self,
                 name: str,
                 type_definition: TypeDefinition) -> None:
        if not isinstance(type_definition, TypeDefinition):
            raise Exception(f"Wrong type for {type_definition}")

        self.class_name = name
        self.type_definition = type_definition


class ClassProperty:
    def __init__(self,
                 name: str,
                 _type: TypeDefinition) -> None:
        self.name = name
        self.type = _type
        self.description: Optional[str] = None

    @property
    def required(self) -> bool:
        return self.type.required

    @required.setter
    def required(self, value: bool) -> None:
        self.type.required = value


class ClassDefinition:
    def __init__(self,
                 class_name: str) -> None:
        self.class_name = class_name
        self.description: Optional[str] = None
        self.properties: Dict[str, ClassProperty] = dict()


JSON_TYPES = [
    TypeDefinition("boolean"),
    TypeDefinition("integer"),
    TypeDefinition("float"),
    TypeDefinition("string"),
    TypeDefinition("array").with_typevar("Any"),
    TypeDefinition("object").with_typevar("Any"),
]


def process_all_classes(data: yamldict.YamlDict) -> List[Union[ClassDefinition, UnionDefinition, TypeAlias]]:
    found_items = []

    for class_name, definition in data.definitions._items():
        if definition.type == "object":
            c = process_class(class_name, definition)
            found_items.append(c)
        elif definition.type:  # type alias
            t = parse_type_definition(definition)
            found_items.append(TypeAlias(class_name, t))  # FIXME description
        elif has_no_attribute(definition):
            json = UnionDefinition(class_name, *JSON_TYPES)
            if definition.description:
                json.description = definition.description
            found_items.append(json)
        elif is_union(definition):
            u = process_union(class_name, definition)
            found_items.append(u)
        else:
            raise Exception(f"Unsupported definition for {class_name}: {definition}")

    return found_items


def is_union(c: yamldict.YamlDict) -> bool:
    return c.oneOf


def process_union(union_name: str,
                  c: yamldict.YamlDict) -> UnionDefinition:
    u = UnionDefinition(name=union_name)

    for utype in c.oneOf:
        u.items.append(parse_type_definition(utype))

    return u


def has_no_attribute(definition: yamldict.YamlDict) -> bool:
    """
    It contains at most the description
    :param definition:
    :return:
    """
    if not definition:
        return True

    if len(definition) == 1 and definition.description:
        return True

    return False


def process_class(class_name: str,
                  definition: yamldict.YamlDict) -> ClassDefinition:
    c = ClassDefinition(class_name)

    if definition.description:
        c.description = definition.description

    if definition.properties:
        for property_name, property_def in definition.properties._items():
            c.properties[property_name] = process_property(property_name, property_def)

    if definition.required:
        for property_name in definition.required:
            c.properties[property_name].required = True

    return c


def process_property(attribute_name: str,
                     attribute_def: yamldict.YamlDict) -> ClassProperty:
    result = ClassProperty(name=attribute_name,
                           _type=parse_type_definition(attribute_def))

    if attribute_def.description:
        result.description = attribute_def.description

    return result


def parse_type_definition(attribute_def: yamldict.YamlDict) -> TypeDefinition:
    if attribute_def["$ref"]:
        return TypeDefinition(type=attribute_def["$ref"])

    result = TypeDefinition(type=attribute_def.type)

    if attribute_def.type == "array":
        result.typevar1 = parse_type_definition(attribute_def.items)
        result.typevar1.required = True

    if attribute_def.type == "object":
        result.typevar1 = parse_type_definition(attribute_def.additionalProperties)
        result.typevar1.required = True

    return result



