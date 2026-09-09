import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { supabase } from "../supabase"
import Logo from "../components/Logo"
import "../styles/auth.css"

export default function Login() {
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (event) => {
    event.preventDefault()

    setError("")
    setLoading(true)

    const { error } = await supabase.auth.signInWithPassword({
      email: email.trim(),
      password
    })

    if (error) {
      setError(error.message)
    }

    setLoading(false)
  }

  return (
    <div className="auth-page">

      {/* Left visual section */}

      <section className="auth-visual">

        <Logo light />

        <div className="auth-visual-content">

          <span className="auth-eyebrow">
            CONTEXT-AWARE MEDICAL REPORT ANALYZER
          </span>

          <h1>
            Understand your medical reports with clarity.
          </h1>

          <p>
            Upload your reports, keep them organized,
            and understand the information they contain
            in clear, simple language.
          </p>

        </div>

        <p className="auth-visual-footer">
          Your reports. Your account. One clear place.
        </p>

      </section>


      {/* Login section */}

      <section className="auth-form-section">

        <div className="auth-form-container">

          <div className="auth-mobile-logo">
            <Logo />
          </div>

          <span className="form-eyebrow">
            WELCOME BACK
          </span>

          <h2>
            Sign in to CAMRA
          </h2>

          <p className="auth-description">
            Sign in to access your medical reports.
          </p>


          <form
            className="auth-form"
            onSubmit={handleSubmit}
          >

            <div className="input-group">

              <label htmlFor="email">
                Email
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) =>
                  setEmail(event.target.value)
                }
                placeholder="you@example.com"
                autoComplete="email"
                required
              />

            </div>


            <div className="input-group">

              <label htmlFor="password">
                Password
              </label>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />

            </div>


            {error && (
              <div className="auth-error">
                {error}
              </div>
            )}


            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading
                ? "Signing in..."
                : "Sign in"}
            </button>

          </form>


          <div className="auth-divider">
            <span />
            <span>OR</span>
            <span />
          </div>


          <p className="auth-bottom-text">
            Don't have a CAMRA account?
          </p>

          <button
            type="button"
            className="signup-button"
            onClick={() => navigate("/signup")}
          >
            Create an account
          </button>


          <p className="auth-legal">
            By continuing, you agree to use CAMRA
            as an educational report-understanding tool.
          </p>

        </div>

      </section>

    </div>
  )
}