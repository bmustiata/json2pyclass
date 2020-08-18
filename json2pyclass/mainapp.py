#!/usr/bin/env python3

import click
import yaml
import yamldict

from json2pyclass.json_schema_parse import process_all_classes
from json2pyclass.types_writer import write_classes


@click.command()
@click.argument("input_file")
@click.argument("output_file")
# @click.option("--title", help="Postfix of the folder to add (i.e. 2019-10-10-{title})")
def main(input_file: str, output_file: str) -> None:
    with open(output_file, "wt", encoding="utf-8") as out:
        with open(input_file, "rt", encoding="utf-8") as f:
            json_data = yaml.safe_load(f)
            data = yamldict.YamlDict(content=json_data)

        found_items = process_all_classes(data)
        write_classes(output_file, found_items)


if __name__ == '__main__':
    main()
