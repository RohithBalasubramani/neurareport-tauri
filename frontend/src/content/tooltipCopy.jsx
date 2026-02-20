import { Link, Stack, Typography } from '@mui/material'

const createTooltip = ({ why, steps = [], extra = null, link = null }) => (
  <Stack spacing={0.9}>
    <Stack spacing={0.25}>
      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
        Why you need this
      </Typography>
      <Typography variant="body2">{why}</Typography>
    </Stack>
    {steps.length ? (
      <Stack spacing={0.25}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          Steps to perform
        </Typography>
        <Stack component="ol" spacing={0.25} sx={{ pl: 2, mt: 0 }}>
          {steps.map((step, index) => (
            <Typography
              key={`tooltip-step-${index}`}
              component="li"
              variant="body2"
              sx={{ display: 'list-item' }}
            >
              {step}
            </Typography>
          ))}
        </Stack>
      </Stack>
    ) : null}
    {extra ? (
      <Typography variant="body2" color="text.secondary">
        {extra}
      </Typography>
    ) : null}
    {link ? (
      <Link
        href={link.href}
        target="_blank"
        rel="noopener"
        variant="body2"
        sx={{ fontWeight: 600 }}
      >
        {link.label}
      </Link>
    ) : null}
  </Stack>
)

export const TOOLTIP_COPY = {
  connectDatabase: createTooltip({
    why: 'Every PDF and Excel pipeline draw pulls live data from this source. A verified connection ensures both renderers have permissioned access to the right schema before you start mapping tokens or refining sheets.',
    steps: [
      'Choose the engine to load the proper defaults (Postgres, MySQL/MariaDB, SQL Server, or SQLite file) so the correct drivers apply to both pipelines.',
      'Provide host, port, database name or file path, and credentials. Add SSL or driver overrides in the advanced fields if your infrastructure requires them.',
      'Use Test Connection to confirm the app can authenticate, stream sample rows for Excel previews, and reach the database without latency or firewall issues.',
      'Save the connection, then click Select Connection so subsequent verifications and report runs pull from the same approved source.',
    ],
    extra: 'Use a read-only service account scoped to the schemas your templates select from. Excel previews only pull a handful of rows but still require production-grade access.',
  }),
  savedConnections: createTooltip({
    why: 'Saved connections are shared within your workspace so teammates can reuse validated credentials across PDF and Excel flows without re-entering them.',
    steps: [
      'Select a connection to make it the active source for template verification, Excel workbook previews, and runs. The heartbeat badge confirms it is ready for new jobs.',
      'Use Test Connection to revalidate credentials when passwords rotate or firewall rules change, especially before Excel previews that need live sampling.',
      'Edit Settings to update connection details, or duplicate the record to branch off a staging variant.',
      'Delete retired connections to keep the list focused; the system will clear the active selection if that source was in use.',
    ],
    extra: 'Latency readings help you spot degraded databases before they impact long-running PDF jobs or Excel sheet renders.',
  }),
  uploadVerifyTemplate: createTooltip({
    why: 'Verification runs static PDF layouts and Excel workbooks against the active database so you catch missing fields, invalid SQL, or mismatched tokens before approving anything.',
    steps: [
      'Upload a PDF or Excel template. Excel uploads convert each worksheet into an HTML shell and enforce a small sample-row limit to keep previews fast.',
      'Click Verify Template to queue a sandbox run that hydrates the layout with sample data from the selected connection—Excel flows require the active database so sheet headers can be mapped to SQL columns.',
      'Monitor progress in the modal; when complete, review the HTML/PNG preview plus the stored source workbook and resolve any validation warnings.',
      'Open Review Mapping to confirm each token (including row_* placeholders from Excel sheets) is mapped to SQL or data fields and address any items flagged for manual fixes.',
    ],
    extra: 'Keep the connection online during verification—the system reads metadata and sample rows while the job executes, and Excel files fail if they exceed the configured row limit.',
  }),
  templatePicker: createTooltip({
    why: 'Approved templates define what can be executed in a reporting window, and the PDF/Excel chips show which pipeline each template uses. Filtering the catalog lets you quickly target the set relevant to your team or campaign.',
    steps: [
      'Filter by tag or name to narrow the library. Tags often represent business units, compliance tiers, or delivery channels, and the type chip lets you spot Excel workbooks at a glance.',
      'Open a template card to preview its generated output, review generator assets, and adjust the Output Format dropdown. Auto follows the template type (Excel auto-enables DOCX) but you can force PDF or DOCX per run.',
      'Select one or more templates to include them in the next discovery or run cycle. The badge shows when generator assets still need attention before either pipeline can execute.',
    ],
    extra: 'Need to stage new PDF or Excel content? Return to Upload & Verify to approve additional templates before they appear here.',
  }),
  runReports: createTooltip({
    why: 'Runs are how the system pulls live data into finished artifacts. Defining the window, format overrides, and key token filters keeps PDF and Excel jobs scoped and performant.',
    steps: [
      'Confirm the template selection is ready (generator assets green) and review each card\'s Output Format—Auto respects the template type while forcing DOCX enables Excel-friendly workbooks.',
      'Set the reporting window. The platform validates that the end date is after the start date, converts to the pipeline timezone, and applies to both renderers.',
      'Provide required key token values—these act as parameters in the SQL the generator executes for PDF and Excel runs.',
      'Use Find Reports to preview matching batches, then Run Reports to queue generation. Monitor progress and download the PDF/HTML canvases and DOCX workbook artifacts when each run completes.',
    ],
    extra: 'Queued runs respect concurrency limits. Excel runs may take slightly longer while sheet data is normalized, so leave the page open or grab results later from Recent Downloads.',
  }),
  recentDownloads: createTooltip({
    why: 'Recent downloads provide a quick trail of the latest artifacts you or your team generated, including the DOCX workbooks created by the Excel pipeline, so you can reopen evidence without re-querying the pipeline.',
    steps: [
      'Open a file to view it in a new tab, or download again if you need to forward it downstream—Excel runs surface both PDF copies and the workbook attachment.',
      'Use the metadata row (template name, format, size) to confirm you grabbed the correct batch before sharing, especially when both PDF and DOCX versions exist.',
      'Retry failed runs directly from this list once you resolve upstream issues like missing parameters or database outages.',
    ],
    extra: 'Entries persist for your session and across teammates, giving visibility into the most recent PDF and Excel deliverables.',
  }),
  headerMappings: createTooltip({
    why: 'Mappings translate template placeholders—whether PDF tokens or Excel row_* fields—into SQL expressions or dataset references, ensuring every token resolves during generation.',
    steps: [
      'Review the required and optional tokens list. Key tokens drive prompts later in the run wizard, and Excel placeholders retain the sheet/column context so you know what each row_* field represents.',
      'Inspect the auto-suggested SQL or field mapping, editing expressions to match your schema, rename sheet columns, or apply business logic.',
      'Resolve validation warnings—syntax issues, missing joins, sheet metadata mismatches, or unmapped tokens—to keep approval unblocked.',
      'Approve when each token preview renders the expected sample data (PDF) or worksheet row (Excel). The generator snapshot updates with your final expressions.',
    ],
    extra: 'Use the expression history dropdown to compare AI-suggested SQL with prior PDF and Excel versions before finalizing.',
  }),
  uploadTemplate: createTooltip({
    why: 'Uploading a new layout kicks off the verification cycle. Keeping the staged files visible helps you confirm every PDF or Excel workbook queued before you move on.',
    steps: [
      'Select or drag in the PDF or Excel template you want to stage. Excel uploads capture the original .xlsx alongside the converted HTML shell.',
      'Review the staged list to confirm filenames and sizes match what your stakeholders expect, and trim Excel sheets that exceed the allowed sample-row count.',
      'Proceed to Verify Template to validate mappings, sheet headers, and sample output before handing off for approval.',
    ],
    extra: 'Need to swap a file? Remove it here before verification—after approval the template becomes read-only and the stored Excel workbook is locked.',
  }),
  llm35Corrections: createTooltip({
    why: 'The corrections assistant rewrites the template HTML and inline constants so the final report matches the PDF or Excel source. Clear guidance prevents the model from over-editing your layout or sheet structure.',
    steps: [
      'Describe the issues you see in the preview—call out typos, alignment problems, constants that must be hard-coded, or sheet sections to ignore.',
      'Mention any key tokens or SQL fields that should be referenced when fixing narrative gaps, including row_* tokens for Excel tables.',
      'Run Corrections and review the updated preview. Repeat until the template layout mirrors the source document.',
      'When satisfied, save and close so the latest instructions are persisted for the approval step.',
    ],
    extra: 'Keep instructions action-oriented (“Inline the company name from Sheet 1 header”) to avoid unexpected structural changes.',
  }),
  llm4Narrative: createTooltip({
    why: 'The Narrative Instructions section generates the contract narrative and business summary the generator assets depend on. The guidance here steers aggregation logic and wording for both PDF documents and Excel workbook summaries.',
    steps: [
      'Explain the story you expect the narrative to tell—include grouping rules, comparisons, spreadsheet callouts, and any regulatory language that must appear.',
      'Call out unresolved placeholders or key tokens (including sheet totals) and describe how they should be referenced in the write-up.',
      'Note formatting rules such as bullet lists, currency formatting, or threshold-based highlights.',
      'Approve the template only after confirming these instructions produce a narrative your reviewers can sign off on.',
    ],
    extra: 'Share example snippets or prior report phrasing to keep tone consistent across releases.',
  }),
  setupOverview: createTooltip({
    why: 'The setup flow walks new workspaces through the prerequisite steps so PDF and Excel report automation is reliable from day one.',
    steps: [
      'Connect a database that mirrors production access levels for both pipelines.',
      'Verify and approve at least one PDF or Excel template so the catalog is actionable.',
      'Run a smoke-test report (PDF or Excel) to validate credentials, mappings, and downstream delivery.',
    ],
    extra: 'You can revisit any step later—progress indicators remind you which stages still need attention.',
  }),
}

export default TOOLTIP_COPY
