/**
 * Search sidebar with saved searches, history, and facets
 */
import React from 'react'
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Checkbox,
  FormControlLabel,
  alpha,
  styled,
} from '@mui/material'
import {
  History as HistoryIcon,
  Bookmark as SavedIcon,
} from '@mui/icons-material'

const SidebarContainer = styled(Box)(({ theme }) => ({
  width: 280,
  borderLeft: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  display: 'flex',
  flexDirection: 'column',
}))

const FacetSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}))

export default function SearchSidebar({
  savedSearches,
  searchHistory,
  facets,
  onRunSavedSearch,
  onHistoryClick,
}) {
  return (
    <SidebarContainer>
      {/* Saved Searches */}
      <FacetSection>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Saved Searches
          </Typography>
          <SavedIcon fontSize="small" color="action" />
        </Box>
        <List dense>
          {savedSearches.slice(0, 5).map((saved) => (
            <ListItem
              key={saved.id}
              button
              onClick={() => onRunSavedSearch(saved)}
              sx={{ borderRadius: 1 }}
            >
              <ListItemText
                primary={saved.name}
                secondary={saved.query}
                primaryTypographyProps={{ variant: 'body2' }}
                secondaryTypographyProps={{ noWrap: true }}
              />
            </ListItem>
          ))}
          {savedSearches.length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
              No saved searches
            </Typography>
          )}
        </List>
      </FacetSection>

      {/* Recent Searches */}
      <FacetSection>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Recent Searches
          </Typography>
          <HistoryIcon fontSize="small" color="action" />
        </Box>
        <List dense>
          {searchHistory.slice(0, 5).map((item, index) => (
            <ListItem
              key={index}
              button
              onClick={() => onHistoryClick(item)}
              sx={{ borderRadius: 1 }}
            >
              <ListItemText
                primary={item.query}
                secondary={`${item.resultCount} results`}
                primaryTypographyProps={{ variant: 'body2', noWrap: true }}
              />
            </ListItem>
          ))}
          {searchHistory.length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
              No recent searches
            </Typography>
          )}
        </List>
      </FacetSection>

      {/* Facets */}
      {Object.keys(facets).length > 0 && (
        <FacetSection>
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            Refine Results
          </Typography>
          {Object.entries(facets).map(([facetName, facetValues]) => (
            <Box key={facetName} sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary">
                {facetName.replace(/_/g, ' ').toUpperCase()}
              </Typography>
              {Object.entries(facetValues).slice(0, 5).map(([value, count]) => (
                <FormControlLabel
                  key={value}
                  control={<Checkbox size="small" />}
                  label={
                    <Typography variant="body2">
                      {value} ({count})
                    </Typography>
                  }
                />
              ))}
            </Box>
          ))}
        </FacetSection>
      )}
    </SidebarContainer>
  )
}
