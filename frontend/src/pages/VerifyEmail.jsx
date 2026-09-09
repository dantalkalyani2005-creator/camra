import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import { supabase } from "../supabase"
import Logo from "../components/Logo"
import { CheckIcon } from "../components/Icons"
import "../styles/auth.css"

export default function VerifyEmail() {
  const navigate = useNavigate()
  const location = useLocation()

  const email = location.state?.email || ""

  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")

  const handleResend = async () => {
    if (!email) {
      setError("Email address is missing. Please return to sign in.")
      return
    }

    setLoading(true)
    setMessage("")
    setError("")

    const { error } = await supabase.auth.resend({
      type: "signup",
      email
    })

    if (error) {
      setError(error.message)
    } else {
      setMessage("Verification email sent again.")
    }

    setLoading(false)
  }

  return (
    <div className="auth-page">

      <section className="auth-visual">

        <Logo light />

        <div className="auth-visual-content">

          <span className="auth-eyebrow">
            ONE-TIME VERIFICATION
          </span>

          <h1>
            You're almost ready to use CAMRA.
          </h1>

          <p>
            Verify your email address once to activate
            your account and continue to CAMRA.
          </p>

        </div>

        <p className="auth-visual-footer">
          Verification is only required when creating your account.
        </p>

      </section>


      <section className="auth-form-section">

        <div className="auth-form-container">

          <div className="auth-mobile-logo">
            <Logo />
          </div>

          <div className="verification-icon">
            <CheckIcon size={28} strokeWidth={2} />
          </div>

          <span className="form-eyebrow">
            CHECK YOUR EMAIL
          </span>

          <h2>
            Verify your email
          </h2>

          <p className="auth-description">
            We've sent a verification link to:
          </p>

          <div className="verification-email">
            {email || "your email address"}
          </div>

          <p className="verification-help">
            Click the link in that email to verify your
            account. Once verified, come back here and
            sign in normally.
          </p>


          {message && (
            <div className="auth-success">
              {message}
            </div>
          )}

          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}


          <button
            type="button"
            className="auth-submit"
            onClick={handleResend}
            disabled={loading || !email}
          >
            {loading
              ? "Sending..."
              : "Resend verification email"}
          </button>


          <button
            type="button"
            className="text-button"
            onClick={() => navigate("/login")}
          >
            Back to sign in
          </button>


          <p className="auth-legal">
            Didn't receive it? Check your spam or junk
            folder before requesting another email.
          </p>

        </div>

      </section>

    </div>
  )
}