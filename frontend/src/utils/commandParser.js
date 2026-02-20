// Command patterns for natural language processing
const COMMAND_PATTERNS = [
  // Connection commands
  {
    pattern: /^connect\s+(?:to\s+)?(.+)$/i,
    type: 'connect',
    extract: (match) => ({ connectionString: match[1].trim() }),
  },
  {
    pattern: /^disconnect$/i,
    type: 'disconnect',
    extract: () => ({}),
  },
  // Template commands
  {
    pattern: /^upload\s+(?:template\s+)?(.+)$/i,
    type: 'upload',
    extract: (match) => ({ path: match[1].trim() }),
  },
  {
    pattern: /^(?:list\s+)?templates?$/i,
    type: 'list_templates',
    extract: () => ({}),
  },
  {
    pattern: /^use\s+(?:template\s+)?["']?([^"']+)["']?$/i,
    type: 'use_template',
    extract: (match) => ({ templateName: match[1].trim() }),
  },
  // Report generation commands
  {
    pattern: /^generate\s+(?:report\s+)?(?:for\s+)?(.+)$/i,
    type: 'generate',
    extract: (match) => ({ query: match[1].trim() }),
  },
  {
    pattern: /^run\s+(?:report\s+)?(?:for\s+)?(.+)$/i,
    type: 'generate',
    extract: (match) => ({ query: match[1].trim() }),
  },
  {
    pattern: /^report\s+(.+)$/i,
    type: 'report',
    extract: (match) => {
      // Parse date range: "report template_name 2024-01-01 to 2024-01-31"
      const args = match[1].trim()
      const dateMatch = args.match(/(\S+)\s+(\d{4}-\d{2}-\d{2})\s+(?:to\s+)?(\d{4}-\d{2}-\d{2})/)
      if (dateMatch) {
        return {
          templateId: dateMatch[1],
          startDate: dateMatch[2],
          endDate: dateMatch[3],
        }
      }
      return { templateId: args }
    },
  },
  // Analysis commands
  {
    pattern: /^analyze\s+(.+)$/i,
    type: 'analyze',
    extract: (match) => ({ query: match[1].trim() }),
  },
  // Help command
  {
    pattern: /^(?:help|\?)$/i,
    type: 'help',
    extract: () => ({}),
  },
  // Clear command
  {
    pattern: /^clear$/i,
    type: 'clear',
    extract: () => ({}),
  },
  // Status command
  {
    pattern: /^status$/i,
    type: 'status',
    extract: () => ({}),
  },
]

export function parseCommand(input) {
  const trimmed = input.trim()

  // Check if it starts with a slash (explicit command)
  if (trimmed.startsWith('/')) {
    const withoutSlash = trimmed.slice(1)
    for (const { pattern, type, extract } of COMMAND_PATTERNS) {
      const match = withoutSlash.match(pattern)
      if (match) {
        return { type, params: extract(match), raw: input }
      }
    }
  }

  // Check natural language patterns
  for (const { pattern, type, extract } of COMMAND_PATTERNS) {
    const match = trimmed.match(pattern)
    if (match) {
      return { type, params: extract(match), raw: input }
    }
  }

  // Default to natural language query for report generation
  return {
    type: 'query',
    params: { query: trimmed },
    raw: input,
  }
}

export function getCommandSuggestions(input) {
  const trimmed = input.trim().toLowerCase()

  const suggestions = [
    { command: '/connect', description: 'Connect to a database' },
    { command: '/disconnect', description: 'Disconnect from database' },
    { command: '/upload', description: 'Upload a template file' },
    { command: '/list templates', description: 'List available templates' },
    { command: '/use', description: 'Select a template to use' },
    { command: '/generate', description: 'Generate a report' },
    { command: '/analyze', description: 'Analyze data or document' },
    { command: '/help', description: 'Show available commands' },
    { command: '/clear', description: 'Clear current session' },
    { command: '/status', description: 'Show connection status' },
  ]

  if (!trimmed || trimmed === '/') {
    return suggestions
  }

  return suggestions.filter(
    (s) =>
      s.command.toLowerCase().includes(trimmed) ||
      s.description.toLowerCase().includes(trimmed)
  )
}

export const HELP_TEXT = `
Available commands:
  /connect <connection-string>  Connect to a database
  /disconnect                   Disconnect from database
  /upload <file>                Upload a template file
  /list templates               Show available templates
  /use <template>               Select a template
  /generate <query>             Generate a report
  /analyze <query>              Analyze data
  /help                         Show this help
  /clear                        Clear session
  /status                       Show status

Or simply describe what you want in natural language:
  "Generate revenue report for Q4 2024"
  "Show me sales by region"
  "Analyze the uploaded document"
`.trim()
