import { useEffect, useState } from "react"
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom"

import { supabase } from "./supabase"

import Login from "./pages/Login"
import Signup from "./pages/Signup"
import VerifyEmail from "./pages/VerifyEmail"

import Home from "./pages/Home"
import UploadReport from "./pages/UploadReport"
import History from "./pages/History"
import ReportDetails from "./pages/ReportDetails"
import Profile from "./pages/Profile"
import "./App.css"
import AppLayout from "./components/AppLayout"

function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session)
      setLoading(false)
    })

    const {
      data: { subscription }
    } = supabase.auth.onAuthStateChange(
      (_event, newSession) => {
        setSession(newSession)
        setLoading(false)
      }
    )

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  const handleLogout = async () => {
    await supabase.auth.signOut()
    setSession(null)
  }

  if (loading) {
    return null
  }

  return (
    <BrowserRouter>
      {!session ? (
        <Routes>

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/signup"
            element={<Signup />}
          />

          <Route
            path="/verify-email"
            element={<VerifyEmail />}
          />

          <Route
            path="*"
            element={<Navigate to="/login" replace />}
          />

        </Routes>
      ) : (
        <AppLayout
          session={session}
          onLogout={handleLogout}
        >
          <Routes>

            <Route
              path="/home"
              element={
                <Home
                  session={session}
                />
              }
            />

            <Route
              path="/upload"
              element={<UploadReport />}
            />

            <Route
              path="/reports"
              element={<History />}
            />

            <Route
              path="/reports/:reportId"
              element={<ReportDetails />}
            />

            <Route
              path="/profile"
              element={
                <Profile
                  session={session}
                  onLogout={handleLogout}
                />
              }
            />

            <Route
              path="*"
              element={<Navigate to="/home" replace />}
            />

          </Routes>
        </AppLayout>
      )}
    </BrowserRouter>
  )
}

export default App