import { Stack, Typography, TextField, Button, Grid } from '@mui/material'

export default function CompareCommentsSection({ analyzeState, busy, toast, runRequest }) {
  const {
    compareId1, setCompareId1,
    compareId2, setCompareId2,
    commentAnalysisId, setCommentAnalysisId,
    commentUserId, setCommentUserId,
    commentUserName, setCommentUserName,
    commentContent, setCommentContent,
    commentElementType, setCommentElementType,
    commentElementId, setCommentElementId,
  } = analyzeState

  return (
    <>
      <Grid item xs={12} md={6}>
        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Compare Analyses</Typography>
          <TextField
            fullWidth
            label="Analysis ID 1"
            value={compareId1}
            onChange={(event) => setCompareId1(event.target.value)}
            size="small"
          />
          <TextField
            fullWidth
            label="Analysis ID 2"
            value={compareId2}
            onChange={(event) => setCompareId2(event.target.value)}
            size="small"
          />
          <Button
            variant="outlined"
            disabled={busy}
            onClick={() => {
              if (!compareId1 || !compareId2) {
                toast.show('Both analysis IDs are required', 'warning')
                return
              }
              runRequest({
                method: 'post',
                url: '/analyze/v2/compare',
                data: {
                  analysis_id_1: compareId1,
                  analysis_id_2: compareId2,
                },
              })
            }}
          >
            Compare
          </Button>
        </Stack>
      </Grid>
      <Grid item xs={12} md={6}>
        <Stack spacing={1.5}>
          <Typography variant="subtitle2">Comments</Typography>
          <TextField
            fullWidth
            label="Analysis ID"
            value={commentAnalysisId}
            onChange={(event) => setCommentAnalysisId(event.target.value)}
            size="small"
          />
          <TextField
            fullWidth
            label="User ID"
            value={commentUserId}
            onChange={(event) => setCommentUserId(event.target.value)}
            size="small"
          />
          <TextField
            fullWidth
            label="User Name"
            value={commentUserName}
            onChange={(event) => setCommentUserName(event.target.value)}
            size="small"
          />
          <TextField
            fullWidth
            label="Element Type (optional)"
            value={commentElementType}
            onChange={(event) => setCommentElementType(event.target.value)}
            size="small"
          />
          <TextField
            fullWidth
            label="Element ID (optional)"
            value={commentElementId}
            onChange={(event) => setCommentElementId(event.target.value)}
            size="small"
          />
          <TextField
            fullWidth
            label="Comment"
            value={commentContent}
            onChange={(event) => setCommentContent(event.target.value)}
            size="small"
            multiline
            minRows={2}
          />
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Button
              variant="outlined"
              disabled={busy}
              onClick={() => {
                if (!commentAnalysisId) {
                  toast.show('Analysis ID is required', 'warning')
                  return
                }
                runRequest({ url: `/analyze/v2/${encodeURIComponent(commentAnalysisId)}/comments` })
              }}
            >
              List Comments
            </Button>
            <Button
              variant="contained"
              disabled={busy}
              onClick={() => {
                if (!commentAnalysisId || !commentContent) {
                  toast.show('Analysis ID and comment content are required', 'warning')
                  return
                }
                runRequest({
                  method: 'post',
                  url: `/analyze/v2/${encodeURIComponent(commentAnalysisId)}/comments`,
                  data: {
                    content: commentContent,
                    user_id: commentUserId || undefined,
                    user_name: commentUserName || undefined,
                    element_type: commentElementType || undefined,
                    element_id: commentElementId || undefined,
                  },
                })
              }}
            >
              Add Comment
            </Button>
          </Stack>
        </Stack>
      </Grid>
    </>
  )
}
