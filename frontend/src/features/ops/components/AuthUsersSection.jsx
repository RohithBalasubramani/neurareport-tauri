import { Stack, Typography, TextField, Button, Divider, Grid } from '@mui/material'
import Surface from '@/components/layout/Surface.jsx'
import SectionHeader from '@/components/layout/SectionHeader.jsx'

export default function AuthUsersSection({ state, busy, toast, runRequest, setBearerToken }) {
  const {
    registerEmail, setRegisterEmail,
    registerPassword, setRegisterPassword,
    registerName, setRegisterName,
    loginEmail, setLoginEmail,
    loginPassword, setLoginPassword,
    userId, setUserId,
  } = state

  return (
    <Surface>
      <SectionHeader
        title="Auth & Users"
        subtitle="Register users, obtain tokens, and manage user records."
      />
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Stack spacing={1.5}>
            <Typography variant="subtitle2">Register</Typography>
            <TextField
              fullWidth
              label="Email"
              value={registerEmail}
              onChange={(event) => setRegisterEmail(event.target.value)}
              size="small"
            />
            <TextField
              fullWidth
              label="Password"
              value={registerPassword}
              onChange={(event) => setRegisterPassword(event.target.value)}
              size="small"
              type="password"
            />
            <TextField
              fullWidth
              label="Full Name (optional)"
              value={registerName}
              onChange={(event) => setRegisterName(event.target.value)}
              size="small"
            />
            <Button
              variant="contained"
              disabled={busy}
              onClick={() => {
                if (!registerEmail || !registerPassword) {
                  toast.show('Email and password are required', 'warning')
                  return
                }
                const payload = {
                  email: registerEmail,
                  password: registerPassword,
                }
                if (registerName) payload.full_name = registerName
                runRequest({ method: 'post', url: '/auth/register', data: payload })
              }}
            >
              Register User
            </Button>
          </Stack>
        </Grid>
        <Grid item xs={12} md={6}>
          <Stack spacing={1.5}>
            <Typography variant="subtitle2">Login</Typography>
            <TextField
              fullWidth
              label="Email / Username"
              value={loginEmail}
              onChange={(event) => setLoginEmail(event.target.value)}
              size="small"
            />
            <TextField
              fullWidth
              label="Password"
              value={loginPassword}
              onChange={(event) => setLoginPassword(event.target.value)}
              size="small"
              type="password"
            />
            <Button
              variant="contained"
              disabled={busy}
              onClick={() => {
                if (!loginEmail || !loginPassword) {
                  toast.show('Login requires email and password', 'warning')
                  return
                }
                const params = new URLSearchParams()
                params.append('username', loginEmail)
                params.append('password', loginPassword)
                runRequest({
                  method: 'post',
                  url: '/auth/jwt/login',
                  data: params,
                  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                  onSuccess: (payload) => {
                    if (payload?.access_token) {
                      setBearerToken(payload.access_token)
                      toast.show('Token saved to bearer field', 'info')
                    }
                  },
                })
              }}
            >
              Get Access Token
            </Button>
          </Stack>
        </Grid>
        <Grid item xs={12}>
          <Divider />
        </Grid>
        <Grid item xs={12} md={6}>
          <Stack spacing={1.5}>
            <Typography variant="subtitle2">User Management</Typography>
            <TextField
              fullWidth
              label="User ID"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              size="small"
              placeholder="UUID"
            />
            <Stack direction="row" spacing={1} flexWrap="wrap">
              <Button
                variant="outlined"
                disabled={busy}
                onClick={() => runRequest({ url: '/users' })}
              >
                List Users
              </Button>
              <Button
                variant="outlined"
                disabled={busy}
                onClick={() => {
                  if (!userId) {
                    toast.show('User ID required', 'warning')
                    return
                  }
                  runRequest({ url: `/users/${encodeURIComponent(userId)}` })
                }}
              >
                Get User
              </Button>
              <Button
                variant="outlined"
                disabled={busy}
                onClick={() => {
                  if (!userId) {
                    toast.show('User ID required', 'warning')
                    return
                  }
                  runRequest({ method: 'delete', url: `/users/${encodeURIComponent(userId)}` })
                }}
                sx={{ color: 'text.secondary' }}
              >
                Delete User
              </Button>
            </Stack>
          </Stack>
        </Grid>
      </Grid>
    </Surface>
  )
}
