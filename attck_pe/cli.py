import os
from typing import Dict

import click
from dotenv import load_dotenv

from attck_pe.main import main

DATA_PATH_TYPE = click.Path(
    exists=True, dir_okay=True, readable=True, resolve_path=True, path_type=str
)


def _init_env(envvars: Dict[str, str]) -> None:
    load_dotenv()
    for k, v in envvars.items():
        if not k:
            continue
        os.environ[k] = v


@click.command()
@click.option("--document-path", "document_path", type=DATA_PATH_TYPE, default="./data")
@click.option("--llm-model", "llm_model", type=str, default="dolphin-mistral:latest")
@click.option("--embed-model", "embed_model", type=str, default="local:BAAI/bge-m3")
@click.option(
    "--code-agent-model", "code_agent_model", type=str, default="red-team-expert:latest"
)
def cli(document_path, llm_model, embed_model, code_agent_model) -> None:
    envvars = {
        "document_path": document_path,
        "llm_model": llm_model,
        "embed_model": embed_model,
        "code_agent_model": code_agent_model,
    }
    envvars = {k: v for k, v in envvars.items() if all((k, v))}
    _init_env(envvars=envvars)
    main()


def run_cli() -> None:
    cli()
