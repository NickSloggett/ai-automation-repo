"""Data analysis and reporting workflow example."""

import asyncio
from datetime import datetime, timedelta
from src.workflows import WorkflowBuilder, WorkflowEngine
from src.tools import DataProcessorTool, APITool, EmailTool, ToolConfig


async def main():
    """Run data analysis workflow."""
    print("🚀 Starting Data Analysis & Reporting Workflow\n")

    # Build workflow
    workflow = (
        WorkflowBuilder(
            name="automated_data_analysis",
            description="Extract data, perform analysis, generate insights, and send report",
        )
        .with_config(
            max_retries=2,
            timeout=1200,
            parallel_execution=False,
        )
        .add_task_step(
            name="extract_data",
            task_type="data_extraction",
            inputs={
                "sources": [
                    {"type": "database", "connection": "postgresql", "query": "SELECT * FROM sales WHERE date >= '2025-09-01'"},
                    {"type": "api", "endpoint": "https://api.analytics.com/events", "params": {"date_from": "2025-09-01"}},
                    {"type": "csv", "path": "/data/customer_feedback.csv"},
                ],
            },
        )
        .then(
            name="clean_data",
            agent_type="task",
            agent_config={
                "name": "data_cleaner",
                "description": "Clean and normalize data",
                "task_type": "data_cleaning",
            },
            inputs={
                "data": "{{extract_data.output.data}}",
                "operations": [
                    "remove_duplicates",
                    "fill_missing_values",
                    "normalize_dates",
                    "standardize_currencies",
                ],
            },
        )
        .then(
            name="perform_analysis",
            agent_type="task",
            agent_config={
                "name": "data_analyzer",
                "description": "Perform statistical analysis",
                "task_type": "data_analysis",
            },
            inputs={
                "data": "{{clean_data.output.cleaned_data}}",
                "analysis_types": [
                    "revenue_trends",
                    "customer_segmentation",
                    "conversion_rates",
                    "churn_prediction",
                ],
            },
        )
        .then(
            name="generate_insights",
            agent_type="task",
            agent_config={
                "name": "insight_generator",
                "description": "Generate AI-powered insights",
                "task_type": "insight_generation",
            },
            inputs={
                "analysis_results": "{{perform_analysis.output.results}}",
                "llm_model": "gpt-4",
                "insight_types": [
                    "key_findings",
                    "trends",
                    "anomalies",
                    "recommendations",
                ],
            },
        )
        .then(
            name="create_visualizations",
            agent_type="task",
            agent_config={
                "name": "viz_creator",
                "description": "Create data visualizations",
                "task_type": "visualization",
            },
            inputs={
                "data": "{{perform_analysis.output.results}}",
                "chart_types": [
                    {"type": "line", "title": "Revenue Trends", "x": "date", "y": "revenue"},
                    {"type": "bar", "title": "Customer Segments", "x": "segment", "y": "count"},
                    {"type": "pie", "title": "Conversion Funnel", "values": "stage_counts"},
                ],
            },
        )
        .then(
            name="generate_report",
            agent_type="task",
            agent_config={
                "name": "report_generator",
                "description": "Generate comprehensive report",
                "task_type": "report_generation",
            },
            inputs={
                "insights": "{{generate_insights.output.insights}}",
                "visualizations": "{{create_visualizations.output.charts}}",
                "analysis": "{{perform_analysis.output.results}}",
                "report_format": "pdf",
                "template": "executive_summary",
            },
        )
        .then(
            name="send_report",
            agent_type="task",
            agent_config={
                "name": "report_sender",
                "description": "Email report to stakeholders",
                "task_type": "email_delivery",
            },
            inputs={
                "recipients": [
                    "ceo@company.com",
                    "cfo@company.com",
                    "analytics-team@company.com",
                ],
                "subject": "Monthly Analytics Report - {{month}} {{year}}",
                "report_file": "{{generate_report.output.file_path}}",
                "summary": "{{generate_insights.output.executive_summary}}",
            },
        )
        .build()
    )

    # Execute workflow
    engine = WorkflowEngine()
    result = await engine.execute(
        workflow,
        initial_input={
            "report_month": "September",
            "report_year": "2025",
            "database_credentials": {
                "host": "db.company.com",
                "database": "analytics",
                "user": "readonly",
            },
        },
    )

    # Print results
    print(f"\n✅ Workflow Status: {result.status}")
    print(f"⏱️  Execution Time: {result.total_execution_time:.2f}s\n")

    if result.status == "completed":
        print("📊 Analysis Summary:")
        for step_id, step_result in result.step_results.items():
            if step_result.metadata:
                print(f"\n  {step_id}:")
                for key, value in step_result.metadata.items():
                    print(f"    {key}: {value}")

        print(f"\n📧 Report sent successfully!")
    else:
        print(f"\n❌ Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())





