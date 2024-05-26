from pathlib import Path

DEFAULT_PROMPT_DIR = Path(__file__).parent / "templates"

# from jinja2 import Environment, PackageLoader, Template, select_autoescape

# env = Environment(
#     loader=PackageLoader("attck_pe.prompt"), autoescape=select_autoescape()
# )


# def get_prompt_template(file_name: str) -> Template:
#     return env.get_template(file_name)


# def render_prompt_template(file_name: str, fields: dict[str, str] | None) -> str:
#     template = get_prompt_template(file_name)
#     if fields:
#         return template.render(fields)
#     return template.render()


def get_raw_template(path: str) -> str:
    fp = DEFAULT_PROMPT_DIR / path
    with fp.open("r") as f:
        data = f.read()
    return data


def get_code_parser_template(filename: str = "code_parser.txt") -> str:
    return get_raw_template(filename)


def get_context(filename: str = "code_generator.txt") -> str:
    return get_raw_template(filename)


__all__ = [
    # "get_prompt_template",
    # "render_prompt_template",
    "DEFAULT_PROMPT_DIR",
    "get_code_parser_template",
    "get_context",
    "get_raw_template",
]
