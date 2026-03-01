import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

// ─── Realistic interview transcripts ────────────────────────────────────────

const INTERVIEWS = [
  {
    contact_name: "Sarah Chen",
    source_ref: "ZD-10482",
    sentiment: "negative",
    transcript: `Interviewer: Walk me through how your team currently handles feature prioritisation.

Sarah: It's honestly chaos. We have feedback spread across Zendesk, Intercom, Gong call recordings, and random Slack threads. Every Monday our PM spends about four hours copying snippets from all those tools into a Google Doc, then tries to group them by theme. By the time we have a "synthesized" view, it's already Thursday and half the signals are stale.

Interviewer: What happens when you build the PRD from that?

Sarah: The PRD is basically vibes at that point. We write something like "Users want better onboarding" but we can't actually cite which users said what, or how many complained. Engineering pushes back because the requirements are vague, QA doesn't know what "done" looks like, and we ship something that only half-addresses the real problem.

Interviewer: If you could wave a magic wand, what would you change?

Sarah: Give me a tool that reads all our customer channels automatically, finds the patterns, and writes the PRD with real quotes. Then generate the Jira tickets with acceptance criteria so engineering can just start building. I'd pay serious money for that.`,
  },
  {
    contact_name: "Marcus Johnson",
    source_ref: "INT-7291",
    sentiment: "negative",
    transcript: `Interviewer: How do you decide what to build next quarter?

Marcus: We run a quarterly planning cycle. Product managers present their "top 5" to leadership, and leadership picks based on gut feel and who argued loudest. It's political, not data-driven.

Interviewer: Do you use any quantitative signals?

Marcus: We pull NPS scores and look at churn reasons, but it's all manual. Our data analyst builds a spreadsheet with ticket volumes by category, but the categories are inconsistent because every support agent tags things differently. Last quarter we built a feature that our PM was convinced was critical — turned out only 3 customers out of 2,000 had asked for it. Meanwhile the real pain point (broken CSV imports) had 200+ tickets and we missed it entirely.

Interviewer: How does the handoff to engineering work?

Marcus: Terribly. The PM writes a one-page brief, engineering asks 40 clarifying questions in Slack, half the answers get lost, and the Jira tickets are created by the tech lead from memory of the conversation. Acceptance criteria are an afterthought. We spend the first week of every sprint just figuring out what we're actually building.`,
  },
  {
    contact_name: "Aisha Patel",
    source_ref: "GONG-3384",
    sentiment: "negative",
    transcript: `Interviewer: You mentioned your team struggles with user research synthesis. Can you elaborate?

Aisha: We do 15-20 customer interviews per month across three PMs. Each PM keeps their notes in their own Notion page. There's no shared repository, no tagging, no way to search across all interviews. When I need to build a case for a feature, I literally have to message each PM and ask "hey, did anyone mention X in their interviews this quarter?"

Interviewer: What does your ideal workflow look like?

Aisha: I want to upload interview transcripts — or even better, have them pulled automatically from Gong and Zoom — and have the system extract pain points, cluster them by theme, tell me how many users mentioned each theme, and show me the exact quotes. Then when I'm ready to write the PRD, the tool should draft it for me using the evidence it already has. The PRD should include suggested UI components and engineering tickets ready to import into Jira.

Interviewer: How would that change your team's velocity?

Aisha: We'd probably ship 2x faster. Right now 40% of a PM's week is just synthesis and documentation drudgework. If AI handled that, we could spend that time actually talking to more users and validating prototypes.`,
  },
  {
    contact_name: "Tom Nakamura",
    source_ref: "ZD-11203",
    sentiment: "neutral",
    transcript: `Interviewer: Tell me about your current product analytics stack.

Tom: We use Mixpanel for event tracking, Zendesk for support, and Jira for project management. The problem isn't the individual tools — they're all fine. The problem is they don't talk to each other. I can see that feature adoption dropped 15% in Mixpanel, and I can see support tickets spiked around the same time in Zendesk, but connecting those two data points requires me to manually export CSVs and cross-reference timestamps.

Interviewer: Have you tried any integration tools?

Tom: We looked at building a data warehouse pipeline with Airbyte, but we don't have the engineering bandwidth to set it up properly. What I really want is something purpose-built for product teams — ingest data from Mixpanel, Zendesk, and Jira, and give me a unified view of "here's what's broken, here's how many users are affected, and here's what you should build to fix it."

Interviewer: How much time would that save?

Tom: Our PM team of 4 collectively spends about 20 hours a week on data gathering and synthesis. If we cut that in half, that's 40 hours a month we could redirect to strategic work.`,
  },
  {
    contact_name: "Priya Ramaswamy",
    source_ref: "INT-8045",
    sentiment: "positive",
    transcript: `Interviewer: You mentioned you've been experimenting with AI for product management. What's working?

Priya: We've tried using ChatGPT to summarise interview transcripts, and it's decent for individual summaries. But it falls apart when you need cross-interview synthesis. I can't paste 20 transcripts into ChatGPT and get a coherent insight cluster — the context window isn't enough, and even if it were, the output is too generic. It says things like "users want better UX" which is useless.

Interviewer: What would make AI useful for your workflow?

Priya: I need structured output, not prose. Give me a JSON object that says: "Insight: CSV import failures affecting 34% of enterprise accounts. Evidence: 12 interviews, 87 support tickets. Recommended feature: Bulk import validation wizard. Jira tickets: [specific stories with acceptance criteria]." That's what I can actually act on. And it needs to be tenant-aware — I work with 3 different enterprise clients and their data must never cross.

Interviewer: Would you trust AI-generated PRDs?

Priya: If it shows me the evidence and I can trace every claim back to a real user quote, yes. I don't want a black box. Show me the receipts.`,
  },
];

// ─── Deterministic IDs (must match lib/auth.ts dev stub) ────────────────────

const DEV_ORG_ID = "00000000-0000-0000-0000-000000000010";
const DEV_USER_AUTH_ID = "00000000-0000-0000-0000-000000000001";
const DEV_USER_ID = "00000000-0000-0000-0000-000000000002";
const DEV_DATASOURCE_ID = "00000000-0000-0000-0000-000000000003";

// ─── Seed function ──────────────────────────────────────────────────────────

async function main() {
  console.log("🌱 Seeding ProductOS database...\n");

  // 1. Organization (deterministic ID matches lib/auth.ts)
  const org = await prisma.organization.upsert({
    where: { slug: "acme-corp" },
    update: {},
    create: {
      id: DEV_ORG_ID,
      name: "Acme Corp",
      slug: "acme-corp",
    },
  });
  console.log(`  ✓ Organization: ${org.name} (${org.id})`);

  // 2. User (deterministic ID matches lib/auth.ts)
  const user = await prisma.user.upsert({
    where: { auth_id: DEV_USER_AUTH_ID },
    update: {},
    create: {
      id: DEV_USER_ID,
      organization_id: org.id,
      auth_id: DEV_USER_AUTH_ID,
      email: "dev@productos.app",
      full_name: "Dev User",
      role: "OWNER",
    },
  });
  console.log(`  ✓ User: ${user.email} (${user.id})`);

  // 3. Data Source
  const zendesk = await prisma.dataSource.upsert({
    where: { id: DEV_DATASOURCE_ID },
    update: {},
    create: {
      id: DEV_DATASOURCE_ID,
      organization_id: org.id,
      provider: "ZENDESK",
      label: "Production Zendesk",
      connection_meta: { workspace: "acme-corp.zendesk.com" },
    },
  });
  console.log(`  ✓ DataSource: ${zendesk.label}`);

  // 4. Interviews
  const interviewIds: string[] = [];
  for (const data of INTERVIEWS) {
    const interview = await prisma.interview.create({
      data: {
        organization_id: org.id,
        data_source_id: zendesk.id,
        source_ref: data.source_ref,
        contact_name: data.contact_name,
        transcript: data.transcript,
        sentiment: data.sentiment,
        language: "en",
      },
    });
    interviewIds.push(interview.id);
    console.log(`  ✓ Interview: ${data.contact_name} (${data.source_ref})`);
  }

  // 5. Feature PRD (pre-generated, as if an agent run already completed)
  const prd = await prisma.featurePrd.create({
    data: {
      organization_id: org.id,
      title: "Automated Interview Synthesis Engine",
      rationale:
        "5/5 interviewed PMs report spending 4-10 hours/week on manual interview synthesis. " +
        "Cross-referencing feedback across Zendesk, Gong, and Intercom is entirely manual. " +
        "87% of PRDs lack traceable evidence. An automated synthesis engine would reduce " +
        "PM drudgework by ~40% and improve PRD accuracy with cited quotes.",
      status: "APPROVED",
      priority: "CRITICAL",
      target_persona: "B2B SaaS Product Manager (3-8 person PM team)",
      success_metrics: [
        { metric_name: "PM synthesis time", target_value: "-50%", measurement_method: "Weekly time-tracking survey" },
        { metric_name: "PRD evidence citations", target_value: ">90% with quotes", measurement_method: "Automated PRD audit" },
        { metric_name: "Sprint planning clarity", target_value: "+30% fewer clarifying questions", measurement_method: "Slack thread count week 1 of sprint" },
      ],
    },
  });
  console.log(`  ✓ FeaturePrd: ${prd.title}`);

  // 6. UI Specs
  const uiSpecs = [
    { component_name: "InterviewUploader", description: "Drag-and-drop transcript upload with real-time PII scrubbing indicator. Supports .txt, .docx, and paste-from-clipboard. Shows a progress bar per file with entity count badges.", props_schema: { files: "File[]", onComplete: "(ids: string[]) => void" }, layout_hint: "modal", sort_order: 0 },
    { component_name: "InsightClusterGrid", description: "Masonry grid of insight cluster cards. Each card shows cluster title, signal count badge, sentiment distribution bar, and expandable quote list. Supports drag-to-reorder for manual prioritisation.", props_schema: { clusters: "InsightCluster[]", onSelect: "(id: string) => void" }, layout_hint: "full-page", sort_order: 1 },
    { component_name: "PrdComposer", description: "Split-pane PRD editor. Left side: AI-generated PRD with inline evidence citations (hover to see source quote). Right side: linked Jira ticket preview cards. Top toolbar: status selector, priority badge, export-to-PDF button.", props_schema: { prdId: "string", mode: "'edit' | 'review'" }, layout_hint: "full-page", sort_order: 2 },
    { component_name: "EvidenceTraceDrawer", description: "Slide-over drawer that shows the full evidence chain for a PRD claim: original interview transcript → extracted signal → insight cluster → PRD statement. Highlighted quote with surrounding context.", props_schema: { claimId: "string", onClose: "() => void" }, layout_hint: "sidebar", sort_order: 3 },
  ];

  for (const spec of uiSpecs) {
    await prisma.uiSpec.create({ data: { feature_prd_id: prd.id, ...spec } });
    console.log(`  ✓ UiSpec: ${spec.component_name}`);
  }

  // 7. Jira Tickets
  const tickets = [
    { type: "EPIC" as const, title: "Interview Synthesis Engine", description: "Epic covering end-to-end automated interview ingestion, PII scrubbing, insight clustering, and PRD generation.", acceptance_criteria: ["All 5 interview sources supported", "PII scrubbed before any LLM call", "Insights traceable to source quotes"], story_points: null },
    { type: "STORY" as const, title: "Interview Upload & PII Scrubbing", description: "As a PM, I can upload interview transcripts and have PII automatically redacted using Microsoft Presidio before storage.\n\n**Technical notes:**\n- POST /interviews endpoint\n- Presidio analyzer with PERSON, EMAIL, PHONE entities\n- Store scrubbed text + embedding via LlamaIndex", acceptance_criteria: ["Upload .txt and .docx files", "PII entities redacted with <PERSON>, <EMAIL> placeholders", "Scrubbed transcript stored with 1024-dim embedding", "Structlog audit trail with tenant_id"], story_points: 5 },
    { type: "STORY" as const, title: "Cross-Interview Insight Clustering", description: "As a PM, I can view automatically generated insight clusters that group pain points across multiple interviews with signal counts and sentiment.\n\n**Technical notes:**\n- LangGraph synthesize_insights node\n- Mistral structured output → InsightClusterOutput schema\n- pgvector similarity for cluster merging", acceptance_criteria: ["Clusters generated from 3+ interviews", "Each cluster shows signal count and sentiment breakdown", "Verbatim quotes linked to source interview", "Minimum 1 quote per signal"], story_points: 8 },
    { type: "STORY" as const, title: "AI-Generated PRD with Evidence Citations", description: "As a PM, I can generate a PRD from an insight cluster. The PRD includes inline evidence citations traceable to specific interview quotes.\n\n**Technical notes:**\n- LangGraph draft_feature_strategy + generate_tech_specs nodes\n- Pydantic strict output: FeaturePrdHandoff schema\n- Citations stored as JSON references to interview IDs", acceptance_criteria: ["PRD generated in < 60 seconds", "Every claim has ≥1 citation", "Success metrics included with measurement method", "UI component specs and Jira tickets auto-generated"], story_points: 8 },
    { type: "TASK" as const, title: "Jira Sync Worker", description: "Background Arq task that pushes generated JiraTicket records to the customer's Jira instance via the Jira Cloud REST API.\n\n**Technical notes:**\n- Arq worker function: sync_jira_tickets\n- OAuth 2.0 via Atlassian Connect\n- Idempotent: store external_ref after creation", acceptance_criteria: ["Tickets created in Jira with correct type and story points", "external_ref stored back to DB", "Retry on 429 with exponential backoff", "Structlog trace with tenant_id and ticket count"], story_points: 5 },
    { type: "TASK" as const, title: "E2E Tests: Ingestion → PRD → Jira", description: "Playwright E2E test covering the full flow: upload interview → verify insight cluster → generate PRD → verify Jira tickets in dashboard.", acceptance_criteria: ["Test runs in CI (GitHub Actions)", "Covers happy path and empty-state", "Assertions on PII scrubbing (no raw names in output)", "< 90 second total runtime"], story_points: 3 },
  ];

  for (const ticket of tickets) {
    await prisma.jiraTicket.create({
      data: { organization_id: org.id, feature_prd_id: prd.id, ...ticket },
    });
    console.log(`  ✓ JiraTicket: [${ticket.type}] ${ticket.title}`);
  }

  // 8. Second PRD (DRAFT) for visual variety on the dashboard
  const prd2 = await prisma.featurePrd.create({
    data: {
      organization_id: org.id,
      title: "Unified Data Source Connector Hub",
      rationale:
        "3/5 PMs cited inability to connect Mixpanel + Zendesk + Jira data as a top blocker. " +
        "Manual CSV exports waste ~20 hours/month across a 4-person PM team. " +
        "A unified connector via Airbyte would automate ingestion and enable real-time cross-source analysis.",
      status: "DRAFT",
      priority: "HIGH",
      target_persona: "Head of Product / Director-level PM",
      success_metrics: [
        { metric_name: "Data source setup time", target_value: "< 10 minutes", measurement_method: "Time-to-first-sync metric" },
        { metric_name: "Manual export elimination", target_value: "0 CSV exports/month", measurement_method: "User activity log" },
      ],
    },
  });
  console.log(`  ✓ FeaturePrd: ${prd2.title}`);

  // 9. Agent Run (completed)
  await prisma.agentRun.create({
    data: {
      organization_id: org.id,
      triggered_by_id: user.id,
      status: "COMPLETED",
      graph_name: "product_discovery",
      input_payload: { interview_ids: interviewIds },
      output_payload: { features: [{ feature_name: prd.title }] },
      token_usage: 14_832,
      started_at: new Date(Date.now() - 45_000),
      completed_at: new Date(Date.now() - 3_000),
    },
  });
  console.log(`  ✓ AgentRun: product_discovery (COMPLETED)\n`);

  console.log("✅ Seed complete.");
}

main()
  .catch((e) => {
    console.error("Seed failed:", e);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
