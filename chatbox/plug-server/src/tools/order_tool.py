from llama_index.tools.types import BaseTool, ToolMetadata, ToolOutput
from llama_index.langchain_helpers.agents.tools import IndexToolConfig, LlamaIndexTool
from typing import Any, Optional, cast
from llama_index.tools import BaseTool
import requests
DEFAULT_NAME = ""
DEFAULT_DESCRIPTION = ""

class ParamSchema:
    def __init__(self):
        self.parameters = {
            "type": "object",
            "properties": {
                "ProductID": {
                    "type": "number",
                    "description": "Specifies the ID of the product being added to the order.",
                },
                "Amount": {
                    "type": "number",
                    "description": "Specifies the quantity of the product to be added to the order.",
                }
            },
            "required": ["ProductID", "Amount"],
        }
    def schema(self):
        return self.parameters
    
class OrderTool(BaseTool):
    def __init__(
        self,
        metadata: ToolMetadata,
    ) -> None:
        self._metadata = metadata
        self._metadata.fn_schema = ParamSchema()

    def add_product_to_order(self, product_id, amount):
        payload = {
            "OrderID": 3,
            "ProductID": product_id,
            "Amount": amount,
        }
        headers = {"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySUQiOjIsIlVzZXJuYW1lIjoidXNlciIsIkF1dGhJRCI6MywiT3JkZXJJRCI6W3siT3JkZXJJRCI6M31dLCJpYXQiOjE3MzI5NTM2ODUsImV4cCI6MTczNjU1MDA4NX0.ty-dQW2eXAAtXowYBR_v7t9dOIc6NTE6XII6CqEzN-Q"}
        response = requests.post("http://localhost:3001/api/v1/order/product", json=payload, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            return "Product added to order successfully."
        else:
            return "Failed to add product to order."
    
    @classmethod
    def from_defaults(
        cls,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "OrderTool":
        name = name or DEFAULT_NAME
        description = description or DEFAULT_DESCRIPTION
        metadata = ToolMetadata(name=name, description=description)
        return cls(metadata=metadata)
    
    @property
    def metadata(self) -> ToolMetadata:
        return self._metadata
    
    def __call__(self, **kwargs) -> ToolOutput:
        product_id = kwargs.get('ProductID')
        amount = kwargs.get('Amount')
        data = self.add_product_to_order(product_id, amount)
        return ToolOutput(
            content=data,
            tool_name=self.metadata.name,
            raw_input={"input": input},
            raw_output=data,
        )
    def as_langchain_tool(self) -> LlamaIndexTool:
        tool_config = IndexToolConfig(
            name=self.metadata.name,
            description=self.metadata.description,
        )
        return LlamaIndexTool.from_tool_config(tool_config=tool_config)