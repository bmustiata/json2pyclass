#!/usr/bin/env python3

import click
import yaml
import yamldict

from json2pyclass.json_pyclass_config import JsonPyClassConfig
from json2pyclass.json_schema_parse import process_all_classes
from json2pyclass.types_writer import write_classes


@click.command()
@click.argument("input_file")
@click.argument("output_name")
@click.option("--mode",
              help="Output mode [class|dict]. Dict is not yet implemented.",
              default="class",
              show_default=True)
@click.option("--optionals/--no-optionals",
              help="Disable Optional[] generation.",
              default=True,
              show_default=True)
def main(input_file: str,
         output_name: str,
         mode: str,
         optionals: bool) -> None:
    config = JsonPyClassConfig(
        output_name=output_name,
        mode=mode,
        optionals=optionals)

    with open(input_file, "rt", encoding="utf-8") as f:
        json_data = yaml.safe_load(f)
        data = yamldict.YamlDict(content=json_data)

    found_items = process_all_classes(data)
    if config.mode == "class":
        write_classes(config, found_items)
    else:
        raise Exception(f"Unknown mode {config.mode}")


if __name__ == '__main__':
    main()
