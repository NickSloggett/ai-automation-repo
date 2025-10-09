"""Data processing tool."""

from typing import Any, Dict, List
import pandas as pd
import structlog

from .base import Tool, ToolResult, ToolConfig

logger = structlog.get_logger(__name__)


class DataProcessorTool(Tool):
    """Tool for data processing and transformation."""

    def __init__(self, config: ToolConfig):
        """Initialize data processor tool.

        Args:
            config: Tool configuration
        """
        super().__init__(config)
        self.logger = logger.bind(tool="data_processor")

    async def execute(
        self,
        data: Any,
        operation: str,
        **kwargs
    ) -> ToolResult:
        """Process data.

        Args:
            data: Data to process (list, dict, DataFrame, etc.)
            operation: Operation to perform
            **kwargs: Operation-specific parameters

        Returns:
            Processed data
        """
        try:
            self.logger.info("Processing data", operation=operation)

            if operation == "to_dataframe":
                result = pd.DataFrame(data)

            elif operation == "filter":
                df = pd.DataFrame(data)
                condition = kwargs.get("condition")
                if condition:
                    result = df.query(condition)
                else:
                    result = df

            elif operation == "aggregate":
                df = pd.DataFrame(data)
                group_by = kwargs.get("group_by", [])
                aggregations = kwargs.get("aggregations", {})
                if group_by and aggregations:
                    result = df.groupby(group_by).agg(aggregations)
                else:
                    result = df

            elif operation == "transform":
                df = pd.DataFrame(data)
                transformations = kwargs.get("transformations", {})
                for column, func in transformations.items():
                    if callable(func):
                        df[column] = df[column].apply(func)
                result = df

            elif operation == "merge":
                df1 = pd.DataFrame(data)
                other_data = kwargs.get("other_data")
                if other_data:
                    df2 = pd.DataFrame(other_data)
                    on = kwargs.get("on")
                    how = kwargs.get("how", "inner")
                    result = pd.merge(df1, df2, on=on, how=how)
                else:
                    result = df1

            elif operation == "sort":
                df = pd.DataFrame(data)
                by = kwargs.get("by", [])
                ascending = kwargs.get("ascending", True)
                result = df.sort_values(by=by, ascending=ascending)

            elif operation == "deduplicate":
                df = pd.DataFrame(data)
                subset = kwargs.get("subset")
                result = df.drop_duplicates(subset=subset)

            elif operation == "fillna":
                df = pd.DataFrame(data)
                value = kwargs.get("value", 0)
                method = kwargs.get("method")
                if method:
                    result = df.fillna(method=method)
                else:
                    result = df.fillna(value)

            elif operation == "to_dict":
                df = pd.DataFrame(data)
                orient = kwargs.get("orient", "records")
                result = df.to_dict(orient=orient)

            elif operation == "to_json":
                df = pd.DataFrame(data)
                orient = kwargs.get("orient", "records")
                result = df.to_json(orient=orient)

            elif operation == "to_csv":
                df = pd.DataFrame(data)
                index = kwargs.get("index", False)
                result = df.to_csv(index=index)

            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}",
                )

            # Convert DataFrame to dict for serialization
            if isinstance(result, pd.DataFrame):
                result_data = result.to_dict(orient="records")
                metadata = {
                    "rows": len(result),
                    "columns": list(result.columns),
                }
            else:
                result_data = result
                metadata = {}

            self.logger.info("Data processing completed", operation=operation)

            return ToolResult(
                success=True,
                data=result_data,
                metadata=metadata,
            )

        except Exception as e:
            self.logger.error("Data processing failed", operation=operation, error=str(e))
            return ToolResult(
                success=False,
                error=f"Data processing failed: {str(e)}",
            )





