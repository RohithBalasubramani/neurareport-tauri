/**
 * Premium Data Table Empty State
 * Beautiful empty state with animations and call-to-action
 */
import { Box } from '@mui/material'
import { Inbox as InboxIcon, Add as AddIcon } from '@mui/icons-material'
import {
  EmptyContainer,
  IconContainer,
  StyledIcon,
  Title,
  Description,
  ActionButton,
  SecondaryButton,
} from './DataTableEmptyStateStyled'

export default function DataTableEmptyState({
  icon: Icon = InboxIcon,
  title = 'No data',
  description,
  action,
  actionLabel,
  onAction,
  secondaryAction,
  secondaryActionLabel,
  onSecondaryAction,
}) {
  return (
    <EmptyContainer>
      <IconContainer>
        <StyledIcon as={Icon} />
      </IconContainer>

      <Title>{title}</Title>

      {description && <Description>{description}</Description>}

      <Box sx={{ display: 'flex', gap: 1.5 }}>
        {(action || onAction) && (
          <ActionButton
            onClick={onAction}
            startIcon={action?.icon || <AddIcon />}
          >
            {actionLabel || action?.label || 'Get Started'}
          </ActionButton>
        )}

        {(secondaryAction || onSecondaryAction) && (
          <SecondaryButton
            variant="outlined"
            onClick={onSecondaryAction}
            startIcon={secondaryAction?.icon}
          >
            {secondaryActionLabel || secondaryAction?.label || 'Learn More'}
          </SecondaryButton>
        )}
      </Box>

    </EmptyContainer>
  )
}
