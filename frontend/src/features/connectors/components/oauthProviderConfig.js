import {
  Google as GoogleIcon,
  Cloud as CloudIcon,
} from '@mui/icons-material'
import { neutral, secondary } from '@/app/theme'

export const OAUTH_PROVIDERS = {
  google_drive: {
    name: 'Google Drive',
    icon: GoogleIcon,
    color: secondary.cyan[500],
    scopes: ['drive.readonly', 'drive.file'],
  },
  dropbox: {
    name: 'Dropbox',
    icon: CloudIcon,
    color: secondary.violet[500],
    scopes: ['files.content.read', 'files.content.write'],
  },
  onedrive: {
    name: 'OneDrive',
    icon: CloudIcon,
    color: secondary.slate[500],
    scopes: ['Files.Read', 'Files.ReadWrite'],
  },
  s3: {
    name: 'Amazon S3',
    icon: CloudIcon,
    color: secondary.fuchsia[500],
    scopes: [],
    authType: 'credentials',
  },
  azure_blob: {
    name: 'Azure Blob',
    icon: CloudIcon,
    color: secondary.teal[500],
    scopes: [],
    authType: 'mixed',
  },
}

/**
 * Check if a provider uses OAuth
 */
export function isOAuthProvider(provider) {
  const config = OAUTH_PROVIDERS[provider]
  return config && config.authType !== 'credentials'
}

/**
 * Get provider configuration
 */
export function getProviderConfig(provider) {
  return OAUTH_PROVIDERS[provider] || null
}
