import ast
import os
from typing import Any, Dict, List

from llama_index.core import PromptTemplate, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.agent import ReActAgent
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core.schema import Document
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.ollama import Ollama
from llama_parse import LlamaParse
from pydantic import BaseModel

from attck_pe.code_reader import code_reader
from attck_pe.prompts import get_code_parser_template, get_context


def read_documents(input_dir, file_extractor) -> List[Document]:
    document_reader = SimpleDirectoryReader(input_dir, file_extractor=file_extractor)
    return document_reader.load_data()


class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str


def check_model_name(name: str) -> None:
    if not name:
        msg = "No model name given."
        raise ValueError(msg)
    elif not isinstance(name, str):
        msg = f"Expected str but {type(name).__name__} given."
        raise TypeError(msg)
    return None


def load_llm_model(model: str, timeout: float = 360.0) -> Ollama:

    check_model_name(model)
    return Ollama(model=model, request_timeout=timeout)


class CodeAgentBuilder:
    __slots__ = ("_llm", "_code_reader", "_code_generator", "_context")

    def __init__(
        self,
        llm=None,
        code_reader=None,
        code_generator=None,
        context: str | None = None,
    ) -> None:
        self.llm = llm
        self.code_reader = code_reader
        self.code_generator = code_generator
        self.context = context

    @property
    def code_reader(self):
        return self._code_reader

    @code_reader.setter
    def code_reader(self, code_reader) -> None:
        self._code_reader = code_reader

    @property
    def code_generator(self):
        return self._code_generator

    @code_generator.setter
    def code_generator(self, code_generator) -> None:
        self._code_generator = code_generator

    @property
    def llm(self):
        return self._llm

    @llm.setter
    def llm(self, llm) -> None:
        if not llm:
            msg = "llm must not be empty"
            raise ValueError(msg)
        if hasattr(llm, "model"):
            model = llm.model
            check_model_name(model)
            self._llm = llm
        elif isinstance(llm, str):
            self._llm = load_llm_model(llm)
        else:
            msg = f"Failed to set llm: Invalid type: {type(llm).__name__}"
            raise TypeError

    @property
    def llm_model_name(self) -> str:
        return self._llm.model

    @property
    def context(self) -> str | None:
        return self._context

    @context.setter
    def context(self, context: str | None) -> None:
        if not context:
            self._context = None
        elif not isinstance(context, str):
            msg = "context must be a str or None."
            raise TypeError(msg)
        else:
            self._context = context

    def build(self) -> ReActAgent:
        """Builds and returns a new agent."""
        llm = self._llm
        # context = self.context
        code_generator = self.code_generator
        code_reader = self.code_reader
        tools = [code_generator, code_reader]
        if not llm:
            msg = "llm must be set to build an agent."
            raise ValueError(msg)
        if not all(tools):
            msg = "code_reader and code_generator must be set to build an agent."
            raise ValueError(msg)
        return ReActAgent.from_tools(tools, llm=llm, verbose=True, context=self.context)


def load_embed_model(model: str = "local:BAAI/bge-m3") -> BaseEmbedding:
    check_model_name(model)
    # Do I need to pull this model?
    embed_model = resolve_embed_model(model)
    return embed_model


def build_vector_index(
    documents, embed_model: BaseEmbedding | str | None = None
) -> VectorStoreIndex:
    if not embed_model:
        embed_model = load_embed_model()
    if isinstance(embed_model, str):
        embed_model = load_embed_model(embed_model)
    if not isinstance(embed_model, BaseEmbedding):
        msg = "Embed model could not be loaded: \n"
        msg += f"embed_model is invalid type: {type(embed_model).__name__}"
        raise TypeError(msg)
    return VectorStoreIndex.from_documents(documents, embed_model=embed_model)


def build_query_engine(llm_model, embed_model, documents) -> BaseQueryEngine:
    index = build_vector_index(documents, embed_model=embed_model)
    query_engine = index.as_query_engine(llm=llm_model)
    return query_engine


def build_code_generator(query_engine: BaseQueryEngine) -> QueryEngineTool:
    metadata = ToolMetadata(
        name="code_generation", description="This generates Red Team Code"
    )
    return QueryEngineTool(query_engine=query_engine, metadata=metadata)


def build_code_agent(
    llm, code_reader, code_generator: QueryEngineTool, context: str | None = None
) -> ReActAgent:
    agent_builder = CodeAgentBuilder()
    agent_builder.llm = llm
    agent_builder.context = context or get_context()
    agent_builder.code_generator = code_generator
    agent_builder.code_reader = code_reader
    agent = agent_builder.build()
    return agent


def build_query_pipeline(llm) -> QueryPipeline:
    output_parser = PydanticOutputParser(CodeOutput)
    code_parser_template = get_code_parser_template()
    json_prompt_str = output_parser.format(code_parser_template)
    json_prompt_tmpl = PromptTemplate(json_prompt_str)
    query_pipeline = QueryPipeline(chain=[json_prompt_tmpl, llm])
    return query_pipeline


def process_response(response) -> Dict[str, Any] | None:
    try:
        cleaned_json: dict[str, Any] = ast.literal_eval(
            str(response).replace("assistant:", "")
        )
        if not all(key in cleaned_json for key in {"code", "description", "filename"}):
            raise KeyError("One or more expected keys are missing in the response")
        return cleaned_json
    except Exception as e:
        print(f"Error processing response: {e}")
        return None


def gen_code(agent, prompt, query_pipeline: QueryPipeline):

    max_retries = 5

    retries = 0
    cleaned_json = None

    while retries < max_retries and cleaned_json is None:
        try:
            result = agent.query(prompt)
            next_result = query_pipeline.run(response=result)
            cleaned_json = process_response(next_result)
        except Exception as e:
            retries += 1
            msg = f"Error occurred: {e}\n"
            msg += f"Attempt #{retries} (max {max_retries})"
            print(msg)

    if not cleaned_json:
        # TODO: raise a custom exception instead of printing.
        print(f"Failed to generate code after {retries} attempts.")

    return cleaned_json


def save_code(path, cleaned_json: Dict[str, Any]) -> None:
    try:
        os.makedirs("output", exist_ok=True)
        with open(os.path.join("output", path), "w") as f:
            f.write(cleaned_json["code"])
        print(f"Saved file {path}")
    except Exception as e:
        print(f"Error saving file: {e}")


def run_prompt_loop(query_pipeline: QueryPipeline, agent) -> None:
    while (prompt := input("Enter a prompt (q to quit): ")) != "q":
        cleaned_json = gen_code(agent, prompt, query_pipeline)
        if cleaned_json:
            print("Code Generated")
            print(cleaned_json["code"])
            print("\n\nDescription:", cleaned_json["description"])

            filename = cleaned_json["filename"]

            save_code(filename, cleaned_json)
        else:
            print("Failed to generate code after 3 retries.")


def main() -> None:
    # Read documents
    # TODO: find a way to develop your own parser using notion API
    file_parser = LlamaParse(result_type="markdown")
    file_extractor = {".pdf": file_parser}
    document_path = os.environ.get("document_path") or "./data"
    documents = read_documents(document_path, file_extractor)

    # Load AI models
    llm_model = load_llm_model("dolphin-mistral:latest")
    embed_model = load_embed_model("local:BAAI/bge-m3")
    agent_llm_model = load_llm_model("dolphin-phi:latest")
    agent_llm_model = load_llm_model("red-team-expert:latest")

    query_engine = build_query_engine(llm_model, embed_model, documents)
    code_generator = build_code_generator(query_engine)
    agent = build_code_agent(agent_llm_model, code_reader, code_generator)

    query_pipeline = build_query_pipeline(llm_model)
    run_prompt_loop(query_pipeline, agent)


if __name__ == "__main__":
    main()
