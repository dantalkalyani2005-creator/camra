import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { supabase } from "../supabase"
import Logo from "../components/Logo"
import "../styles/auth.css"

export default function Signup() {
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (event) => {
    event.preventDefault()

    setError("")

    if (password !== confirmPassword) {
      setError("Passwords do not match.")
      return
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.")
      return
    }

    setLoading(true)

    const { data, error } = await supabase.auth.signUp({
      email: email.trim(),
      password
    })

    if (error) {
      setError(error.message)
      setLoading(false)
      return
    }

    // If email confirmation is enabled, Supabase returns no session.
    if (!data.session) {
      navigate("/verify-email", {
        state: {
          email: email.trim()
        }
      })

      setLoading(false)
      return
    }

    setLoading(false)
  }

  return (
    <div className="auth-page">

      <section className="auth-visual">

        <Logo light />

        <div className="auth-visual-content">

          <span className="auth-eyebrow">
            GET STARTED WITH CAMRA
          </span>

          <h1>
            Keep your reports organized and easier to understand.
          </h1>

          <p>
            Create your CAMRA account and keep your
            medical reports together in one secure place.
          </p>

        </div>

        <p className="auth-visual-footer">
          Simple. Organized. Context-aware.
        </p>

      </section>


      <section className="auth-form-section">

        <div className="auth-form-container">

          <div className="auth-mobile-logo">
            <Logo />
          </div>

          <span className="form-eyebrow">
            CREATE ACCOUNT
          </span>

          <h2>
            Create your CAMRA account
          </h2>

          <p className="auth-description">
            Use your email and a password to get started.
          </p>


          <form
            className="auth-form"
            onSubmit={handleSubmit}
          >

            <div className="input-group">

              <label htmlFor="signup-email">
                Email
              </label>

              <input
                id="signup-email"
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

              <label htmlFor="signup-password">
                Password
              </label>

              <input
                id="signup-password"
                type="password"
                value={password}
                onChange={(event) =>
                  setPassword(event.target.value)
                }
                placeholder="Create a password"
                autoComplete="new-password"
                required
              />

            </div>


            <div className="input-group">

              <label htmlFor="signup-confirm-password">
                Confirm password
              </label>

              <input
                id="signup-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(event.target.value)
                }
                placeholder="Enter your password again"
                autoComplete="new-password"
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
                ? "Creating account..."
                : "Create account"}
            </button>

          </form>


          <div className="auth-divider">
            <span />
            <span>OR</span>
            <span />
          </div>


          <p className="auth-bottom-text">
            Already have a CAMRA account?
          </p>

          <button
            type="button"
            className="signup-button"
            onClick={() => navigate("/login")}
          >
            Sign in
          </button>


          <p className="auth-legal">
            After creating your account, you'll need to
            verify your email once before signing in.
          </p>

        </div>

      </section>

    </div>
  )
}