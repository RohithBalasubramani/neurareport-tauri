import { Box, Portal, Fade } from '@mui/material'
import { alpha } from '@mui/material/styles'
import { useAppStore } from '@/stores'
import Surface from '@/components/layout/Surface.jsx'
import { neutral } from '@/app/theme'
import { PanelHeader, PanelBody, PanelActions } from './DetailPanelSections'

export default function ConnectionDetailPanel({
  panelRef,
  detailConnection,
  detailAnchor,
  detailStatus,
  detailLatency,
  detailNote,
  setDetailId,
  setConfirmDelete,
  requestSelect,
  handleRowTest,
  beginEditConnection,
}) {
  const { activeConnectionId } = useAppStore()

  if (!detailConnection) return null

  return (
    <Portal>
      <Fade in={!!detailConnection} timeout={200}>
        <Box
          sx={{
            position: 'fixed',
            inset: 0,
            zIndex: (theme) => theme.zIndex.drawer + 10,
            pointerEvents: 'none',
            display: 'flex',
            alignItems: { xs: 'flex-end', md: 'center' },
            justifyContent: { xs: 'center', md: 'flex-start' },
            p: { xs: 2, sm: 3, md: 0 },
          }}
        >
          <Box
            onClick={() => setDetailId(null)}
            sx={{
              position: 'absolute',
              inset: 0,
              bgcolor: alpha(neutral[900], 0.32),
              pointerEvents: 'auto',
              zIndex: 0,
            }}
          />
          <Surface
            ref={panelRef}
            onClick={(event) => event.stopPropagation()}
            sx={[
              (theme) => {
                const anchor = detailAnchor
                const base = {
                  width: anchor ? `${anchor.width}px` : 'min(92vw, 560px)',
                  maxWidth: anchor ? `${anchor.width}px` : 'min(92vw, 560px)',
                  pointerEvents: 'auto',
                  position: 'relative',
                  zIndex: 1,
                }
                if (anchor) {
                  base[theme.breakpoints.up('md')] = {
                    position: 'absolute',
                    top: anchor.top,
                    left: anchor.left,
                    width: anchor.width,
                    maxWidth: anchor.width,
                    transform: 'none',
                  }
                } else {
                  base[theme.breakpoints.up('md')] = {
                    position: 'absolute',
                    top: theme.spacing(10),
                    left: theme.spacing(10),
                    width: 560,
                    maxWidth: 560,
                  }
                }
                return base
              },
              {
                p: 0,
                gap: 0,
                display: 'flex',
                flexDirection: 'column',
                borderRadius: '18px !important',
                borderTopLeftRadius: '18px !important',
                borderTopRightRadius: '18px !important',
                borderBottomRightRadius: '18px !important',
                borderBottomLeftRadius: '18px !important',
                boxShadow: `0 12px 32px ${alpha(neutral[900], 0.14)}`,
                maxHeight: {
                  xs: 'calc(100vh - 96px)',
                  sm: 'calc(100vh - 112px)',
                  md: 'calc(100vh - 128px)',
                },
                overflow: 'hidden',
              },
            ]}
          >
            <PanelHeader
              detailConnection={detailConnection}
              detailStatus={detailStatus}
              detailLatency={detailLatency}
              detailNote={detailNote}
              setDetailId={setDetailId}
              activeConnectionId={activeConnectionId}
            />
            <PanelBody
              detailConnection={detailConnection}
              detailLatency={detailLatency}
              detailNote={detailNote}
            />
            <PanelActions
              detailConnection={detailConnection}
              requestSelect={requestSelect}
              handleRowTest={handleRowTest}
              beginEditConnection={beginEditConnection}
              setConfirmDelete={setConfirmDelete}
            />
          </Surface>
        </Box>
      </Fade>
    </Portal>
  )
}
