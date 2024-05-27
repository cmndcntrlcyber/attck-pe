import os
import ast
import torch
import gc  # Import garbage collector
from dotenv import load_dotenv
from pydantic import BaseModel
from llama_parse import LlamaParse
from code_reader import code_reader
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from prompts import context, code_parser_template
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import ToolMetadata, QueryEngineTool
from llama_index.core.output_parsers import PydanticOutputParser
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, PromptTemplate

load_dotenv()

# Initialize LLM
llm = Ollama(model="dolphin-mistral:latest", request_timeout=360.0)

# Initialize parser
parser = LlamaParse(result_type="markdown")
file_extractor = {".pdf": parser}
documents = SimpleDirectoryReader("./data", file_extractor=file_extractor).load_data()

# Resolve and load embed model
embed_model = resolve_embed_model("local:BAAI/bge-m3")

# Clear CUDA cache before creating the index
torch.cuda.empty_cache()

# Force garbage collection
gc.collect()

# Create vector index
vector_index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
query_engine = vector_index.as_query_engine(llm=llm)

# Tools for the agent
tools = [
    QueryEngineTool(
        query_engine=query_engine,
        metadata=ToolMetadata(
            name="code_generation",
            description="This generates code",
        ),
    ),
    code_reader,
]

# Initialize agent
code_llm = Ollama(model="red_expert_lvl3:latest")
agent = ReActAgent.from_tools(tools, llm=code_llm, verbose=True, context=context)

# Define output parser
class CodeOutput(BaseModel):
    code: str
    description: str
    filename: str

parser = PydanticOutputParser(CodeOutput)
json_prompt_str = parser.format(code_parser_template)
json_prompt_tmpl = PromptTemplate(json_prompt_str)
output_pipeline = QueryPipeline(chain=[json_prompt_tmpl, llm])

# Function to process response
def process_response(response):
    try:
        cleaned_json = ast.literal_eval(str(response).replace("assistant:", ""))
        if not all(key in cleaned_json for key in ["code", "description", "filename"]):
            raise KeyError("One or more expected keys are missing in the response")
        return cleaned_json
    except Exception as e:
        print(f"Error processing response: {e}")
        return None

# Main loop
while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    retries = 0
    cleaned_json = None

    while retries < 5 and cleaned_json is None:
        try:
            result = agent.query(prompt)
            next_result = output_pipeline.run(response=result)
            cleaned_json = process_response(next_result)
        except Exception as e:
            retries += 1
            print(f"Error occurred, retry #{retries}:", e)

    if cleaned_json:
        print('Code Generated')
        print(cleaned_json["code"])
        print("\n\nDescription:", cleaned_json["description"])

        filename = cleaned_json["filename"]

        try:
            os.makedirs("output", exist_ok=True)
            with open(os.path.join("output", filename), "w") as f:
                f.write(cleaned_json["code"])
            print("Saved file", filename)
        except Exception as e:
            print("Error saving file:", e)
    else:
        print("Failed to generate code after 5 retries.")

    # Clear CUDA cache after each prompt processing
    torch.cuda.empty_cache()

    # Force garbage collection
    gc.collect()
