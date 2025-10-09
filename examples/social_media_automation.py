"""Social media automation workflow example."""

import asyncio
from datetime import datetime

from src.workflows import WorkflowBuilder, WorkflowEngine
from src.tools import APITool, ToolConfig
from src.llm import get_llm


async def main():
    """Run social media automation workflow."""
    print("🚀 Starting Social Media Automation Workflow\n")

    # Build workflow
    workflow = (
        WorkflowBuilder(
            name="social_media_content_workflow",
            description="Generate and schedule social media content",
        )
        .with_config(
            max_retries=2,
            timeout=600,
            parallel_execution=False,
        )
        .add_task_step(
            name="generate_content",
            task_type="content_generation",
            inputs={
                "topic": "AI automation for small businesses",
                "platform": "twitter",
                "tone": "professional but friendly",
                "length": "280 characters",
            },
        )
        .then(
            name="create_image",
            agent_type="task",
            agent_config={
                "name": "image_generator",
                "description": "Generate social media image",
                "task_type": "image_generation",
            },
            inputs={
                "prompt": "{{generate_content.output.image_description}}",
                "size": "1200x628",
                "style": "modern_tech",
            },
        )
        .then(
            name="schedule_post",
            agent_type="task",
            agent_config={
                "name": "post_scheduler",
                "description": "Schedule social media post",
                "task_type": "scheduling",
            },
            inputs={
                "content": "{{generate_content.output.content}}",
                "image_url": "{{create_image.output.url}}",
                "platform": "twitter",
                "scheduled_time": "2025-09-30T10:00:00Z",
            },
        )
        .build()
    )

    # Execute workflow
    engine = WorkflowEngine()
    result = await engine.execute(
        workflow,
        initial_input={
            "brand": "AI Automation Agency",
            "target_audience": "small business owners",
        },
    )

    # Print results
    print(f"\n✅ Workflow Status: {result.status}")
    print(f"⏱️  Execution Time: {result.total_execution_time:.2f}s\n")

    if result.status == "completed":
        print("📝 Step Results:")
        for step_id, step_result in result.step_results.items():
            print(f"\n  {step_id}:")
            print(f"    Status: {step_result.status}")
            print(f"    Time: {step_result.execution_time:.2f}s")
            if step_result.output:
                print(f"    Output: {step_result.output}")

        if result.final_output:
            print(f"\n🎯 Final Output: {result.final_output}")
    else:
        print(f"\n❌ Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())





