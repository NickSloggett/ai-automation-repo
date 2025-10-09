"""CRM integration and lead enrichment workflow example."""

import asyncio
from src.workflows import WorkflowBuilder, WorkflowEngine
from src.tools import APITool, DataProcessorTool, EmailTool, ToolConfig


async def main():
    """Run CRM integration workflow."""
    print("🚀 Starting CRM Integration Workflow\n")

    # Build workflow
    workflow = (
        WorkflowBuilder(
            name="crm_lead_enrichment",
            description="Fetch leads from CRM, enrich data, and send follow-up emails",
        )
        .with_config(
            max_retries=3,
            timeout=900,
            parallel_execution=True,
        )
        .add_task_step(
            name="fetch_leads",
            task_type="data_fetch",
            inputs={
                "source": "hubspot",
                "filter": "status:new AND created_date:last_7_days",
                "fields": ["email", "company", "phone", "industry"],
            },
        )
        .then(
            name="enrich_data",
            agent_type="task",
            agent_config={
                "name": "data_enricher",
                "description": "Enrich lead data from external sources",
                "task_type": "data_enrichment",
            },
            inputs={
                "leads": "{{fetch_leads.output.leads}}",
                "enrichment_apis": ["clearbit", "linkedin"],
                "fields_to_enrich": ["company_size", "revenue", "technologies"],
            },
        )
        .then(
            name="score_leads",
            agent_type="decision",
            agent_config={
                "name": "lead_scorer",
                "description": "Score leads based on criteria",
                "decision_criteria": [
                    "company_size",
                    "industry_fit",
                    "budget_indicators",
                    "engagement_level",
                ],
                "alternatives": ["hot", "warm", "cold"],
                "confidence_threshold": 0.7,
            },
            inputs={
                "leads": "{{enrich_data.output.enriched_leads}}",
                "scoring_model": "enterprise_fit",
            },
        )
        .add_conditional_step(
            name="send_hot_lead_alert",
            agent_type="task",
            condition_field="score_leads.output.score",
            condition_value="hot",
            condition_operator="equals",
            agent_config={
                "name": "alert_sender",
                "description": "Send alert for hot leads",
                "task_type": "notification",
            },
            inputs={
                "leads": "{{score_leads.output.hot_leads}}",
                "notification_channel": "slack",
                "message_template": "🔥 Hot lead alert: {{lead.company}}",
            },
            depends_on=["score_leads"],
        )
        .add_task_step(
            name="update_crm",
            task_type="data_update",
            inputs={
                "leads": "{{score_leads.output.all_leads}}",
                "crm": "hubspot",
                "updates": {
                    "lead_score": "{{score}}",
                    "enrichment_date": "{{timestamp}}",
                    "data_quality": "{{quality_score}}",
                },
            },
            depends_on=["score_leads"],
        )
        .add_task_step(
            name="send_followup_emails",
            task_type="email_automation",
            inputs={
                "leads": "{{score_leads.output.hot_leads}}",
                "email_template": "hot_lead_followup",
                "personalization": True,
                "send_delay": "1 hour",
            },
            depends_on=["update_crm"],
        )
        .build()
    )

    # Execute workflow
    engine = WorkflowEngine()
    result = await engine.execute(
        workflow,
        initial_input={
            "crm_api_key": "your-crm-api-key",
            "enrichment_api_keys": {
                "clearbit": "your-clearbit-key",
                "linkedin": "your-linkedin-key",
            },
        },
    )

    # Print results
    print(f"\n✅ Workflow Status: {result.status}")
    print(f"⏱️  Execution Time: {result.total_execution_time:.2f}s\n")

    if result.status == "completed":
        print("📊 Workflow Summary:")
        print(f"  - Leads fetched: {len(result.step_results.get('fetch_leads', {}).get('output', {}).get('leads', []))}")
        print(f"  - Leads enriched: {len(result.step_results.get('enrich_data', {}).get('output', {}).get('enriched_leads', []))}")
        print(f"  - Hot leads: {len(result.step_results.get('score_leads', {}).get('output', {}).get('hot_leads', []))}")
        print(f"  - Emails sent: {result.step_results.get('send_followup_emails', {}).get('metadata', {}).get('emails_sent', 0)}")
    else:
        print(f"\n❌ Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())





