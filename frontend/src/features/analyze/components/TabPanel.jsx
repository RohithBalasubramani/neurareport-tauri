import { Box, Fade } from '@mui/material'

export default function TabPanel({ children, value, index, ...other }) {
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Fade in timeout={300}><Box sx={{ py: 3 }}>{children}</Box></Fade>}
    </div>
  )
}
