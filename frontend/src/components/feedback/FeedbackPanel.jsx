/**
 * FeedbackPanel - Thumbs, star ratings, and quality correction input.
 *
 * Provides user feedback collection with thumbs up/down, optional
 * star rating, and expandable correction text field.
 */
import React from 'react';
import {
  Rating,
  TextField,
  IconButton,
  Box,
  Typography,
  Collapse,
  Button,
} from '@mui/material';
import ThumbUpOutlined from '@mui/icons-material/ThumbUpOutlined';
import ThumbUp from '@mui/icons-material/ThumbUp';
import ThumbDownOutlined from '@mui/icons-material/ThumbDownOutlined';
import ThumbDown from '@mui/icons-material/ThumbDown';
import SendIcon from '@mui/icons-material/Send';
import CompactFeedback from './CompactFeedback';
import useFeedbackState from './useFeedbackState';

export default function FeedbackPanel({
  entityId,
  source = 'docqa',
  onSubmit,
  compact = false,
  showRating = true,
  showCorrection = true,
}) {
  const {
    feedbackType, rating, setRating,
    correctionText, setCorrectionText,
    showCorrectionField, setShowCorrectionField,
    submitting, submitted,
    handleThumb, handleSubmit,
  } = useFeedbackState({ entityId, source, showCorrection, onSubmit });

  if (submitted) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, py: compact ? 0.5 : 1 }}>
        <Typography variant="body2" color="success.main" sx={{ fontWeight: 500 }}>
          Thank you for your feedback!
        </Typography>
      </Box>
    );
  }

  if (compact) {
    return (
      <CompactFeedback
        feedbackType={feedbackType}
        onThumb={handleThumb}
        onSubmit={handleSubmit}
        submitting={submitting}
      />
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
          Was this helpful?
        </Typography>
        <IconButton onClick={() => handleThumb('positive')}
          color={feedbackType === 'positive' ? 'success' : 'default'} disabled={submitting}>
          {feedbackType === 'positive' ? <ThumbUp /> : <ThumbUpOutlined />}
        </IconButton>
        <IconButton onClick={() => handleThumb('negative')}
          color={feedbackType === 'negative' ? 'error' : 'default'} disabled={submitting}>
          {feedbackType === 'negative' ? <ThumbDown /> : <ThumbDownOutlined />}
        </IconButton>
      </Box>

      {showRating && feedbackType && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" color="text.secondary">Rate quality:</Typography>
          <Rating value={rating} onChange={(_, newValue) => setRating(newValue || 0)}
            size="medium" disabled={submitting} />
        </Box>
      )}

      {showCorrection && feedbackType && (
        <>
          {!showCorrectionField && (
            <Typography variant="caption" sx={{ color: 'primary.main', cursor: 'pointer' }}
              onClick={() => setShowCorrectionField(true)}>
              Add correction
            </Typography>
          )}
          <Collapse in={showCorrectionField}>
            <TextField fullWidth multiline minRows={2} maxRows={4}
              placeholder="Describe the issue or provide a correction..."
              value={correctionText} onChange={(e) => setCorrectionText(e.target.value)}
              variant="outlined" size="small" disabled={submitting} sx={{ mt: 0.5 }} />
          </Collapse>
        </>
      )}

      {feedbackType && (
        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button variant="contained" size="small" onClick={handleSubmit}
            disabled={submitting} endIcon={<SendIcon />} sx={{ textTransform: 'none' }}>
            {submitting ? 'Submitting...' : 'Submit Feedback'}
          </Button>
        </Box>
      )}
    </Box>
  );
}
