import { useEffect, useState } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { supabase } from "../supabase"
import {
  FileIcon,
  TrashIcon
} from "../components/Icons"
import "../styles/report-details.css"

export default function ReportDetails() {
  const { reportId } = useParams()
  const navigate = useNavigate()

  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (reportId) {
      loadReport()
    }
  }, [reportId])

  const loadReport = async () => {
    setLoading(true)
    setError("")

    const {
      data,
      error
    } = await supabase
      .from("reports")
      .select("*")
      .eq("id", reportId)
      .single()

    if (error) {
      setError(error.message)
    } else {
      setReport(data)
    }

    setLoading(false)
  }

  const handleDelete = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this report?"
    )

    if (!confirmed) return

    setDeleting(true)
    setError("")

    const {
      error
    } = await supabase
      .from("reports")
      .delete()
      .eq("id", reportId)

    if (error) {
      setError(error.message)
      setDeleting(false)
      return
    }

    navigate("/reports", { replace: true })
  }

  const formatDate = (date) => {
    if (!date) return ""

    return new Date(date).toLocaleDateString(
      undefined,
      {
        day: "numeric",
        month: "long",
        year: "numeric"
      }
    )
  }

  /*
   * Safely convert AI response values into something
   * React can render.
   */
  const renderValue = (value) => {
    if (value === null || value === undefined) {
      return ""
    }

    if (
      typeof value === "string" ||
      typeof value === "number"
    ) {
      return String(value)
    }

    if (typeof value === "boolean") {
      return value ? "Yes" : "No"
    }

    if (Array.isArray(value)) {
      return value
        .map((item) => renderValue(item))
        .filter(Boolean)
        .join(" • ")
    }

    if (typeof value === "object") {
      return Object.entries(value)
        .map(([key, item]) => {
          const label = key
            .replace(/_/g, " ")
            .replace(/\b\w/g, (char) => char.toUpperCase())

          const rendered = renderValue(item)

          return rendered
            ? `${label}: ${rendered}`
            : ""
        })
        .filter(Boolean)
        .join(" · ")
    }

    return String(value)
  }

  const renderListItem = (item, index, bullet = null) => {
    const isObject =
      item !== null &&
      typeof item === "object" &&
      !Array.isArray(item)

    return (
      <div
        className="analysis-list-item"
        key={index}
      >
        <span className="analysis-bullet">
          {bullet !== null ? bullet : index + 1}
        </span>

        <p>
          {isObject
            ? renderValue(item)
            : String(item ?? "")}
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="report-details-page">
        <div className="empty-card">
          Loading report...
        </div>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="report-details-page">
        <div className="auth-error">
          {error || "Report could not be found."}
        </div>
      </div>
    )
  }

  const analysis = report.analysis || {}

  const findings =
    Array.isArray(analysis.key_findings)
      ? analysis.key_findings
      : []

  const abnormalResults =
    Array.isArray(analysis.abnormal_results)
      ? analysis.abnormal_results
      : []

  const possibleExplanations =
    Array.isArray(analysis.possible_explanations)
      ? analysis.possible_explanations
      : []

  const questions =
    Array.isArray(
      analysis.questions_to_discuss_with_doctor
    )
      ? analysis.questions_to_discuss_with_doctor
      : []

  const guidance =
    Array.isArray(analysis.general_guidance)
      ? analysis.general_guidance
      : []

  return (
    <div className="report-details-page">

      <div className="report-topbar">

        <div />

        <button
          className="report-delete-button"
          onClick={handleDelete}
          disabled={deleting}
        >
          <TrashIcon size={17} />

          {deleting
            ? "Deleting..."
            : "Delete report"}
        </button>

      </div>


      <header className="report-header">

        <div className="report-title-area">

          <div>

            <span className="section-eyebrow">
              MEDICAL REPORT
            </span>

            <h1>
              {report.report_name}
            </h1>

            <p>
              Uploaded {formatDate(report.created_at)}
            </p>

          </div>

        </div>


        <div
          className={
            report.analysis
              ? "report-header-status analyzed"
              : "report-header-status"
          }
        >
          {report.analysis
            ? "Analysis available"
            : "Not analyzed"}
        </div>

      </header>


      {!report.analysis ? (

        <div className="empty-card report-no-analysis">

          <div className="empty-card-icon">
            <FileIcon size={25} />
          </div>

          <h3>
            Analysis isn't available yet
          </h3>

          <p>
            This report was saved, but no analysis is
            currently attached to it.
          </p>

        </div>

      ) : (

        <div className="analysis-layout">

          <main className="analysis-main">

            {analysis.summary && (
              <section className="analysis-card analysis-summary">

                <span className="analysis-label">
                  SUMMARY
                </span>

                <h2>
                  Report overview
                </h2>

                <p>
                  {renderValue(analysis.summary)}
                </p>

              </section>
            )}


            {findings.length > 0 && (
              <section className="analysis-card">

                <span className="analysis-label">
                  KEY FINDINGS
                </span>

                <h2>
                  What the report shows
                </h2>

                <div className="analysis-list">

                  {findings.map((item, index) =>
                    renderListItem(item, index)
                  )}

                </div>

              </section>
            )}


            {abnormalResults.length > 0 && (
              <section className="analysis-card">

                <span className="analysis-label">
                  ABNORMAL RESULTS
                </span>

                <h2>
                  Results outside the provided range
                </h2>

                <div className="analysis-list">

                  {abnormalResults.map((item, index) =>
                    renderListItem(item, index, "!")
                  )}

                </div>

              </section>
            )}


            {possibleExplanations.length > 0 && (
              <section className="analysis-card">

                <span className="analysis-label">
                  POSSIBLE EXPLANATIONS
                </span>

                <h2>
                  What these findings can mean
                </h2>

                <div className="analysis-list">

                  {possibleExplanations.map(
                    (item, index) =>
                      renderListItem(item, index)
                  )}

                </div>

              </section>
            )}


            {questions.length > 0 && (
              <section className="analysis-card">

                <span className="analysis-label">
                  DISCUSS WITH YOUR DOCTOR
                </span>

                <h2>
                  Questions you may want to ask
                </h2>

                <div className="question-list">

                  {questions.map(
                    (question, index) => (
                      <div
                        className="question-item"
                        key={index}
                      >

                        <span>
                          {index + 1}
                        </span>

                        <p>
                          {renderValue(question)}
                        </p>

                      </div>
                    )
                  )}

                </div>

              </section>
            )}


            {guidance.length > 0 && (
              <section className="analysis-card">

                <span className="analysis-label">
                  GENERAL GUIDANCE
                </span>

                <h2>
                  Helpful context
                </h2>

                <div className="analysis-list">

                  {guidance.map(
                    (item, index) =>
                      renderListItem(
                        item,
                        index,
                        "✓"
                      )
                  )}

                </div>

              </section>
            )}

          </main>


          <aside className="analysis-sidebar">

            <div className="analysis-side-card">

              <span className="analysis-label">
                REPORT INFORMATION
              </span>

              <div className="report-meta">

                <div>
                  <span>
                    Report name
                  </span>

                  <strong>
                    {report.report_name}
                  </strong>
                </div>

                <div>
                  <span>
                    Uploaded
                  </span>

                  <strong>
                    {formatDate(report.created_at)}
                  </strong>
                </div>

                <div>
                  <span>
                    Status
                  </span>

                  <strong>
                    Analyzed
                  </strong>
                </div>

              </div>

            </div>


            {analysis.disclaimer && (
              <div className="analysis-disclaimer">

                <span className="analysis-label">
                  IMPORTANT
                </span>

                <p>
                  {renderValue(analysis.disclaimer)}
                </p>

              </div>
            )}

          </aside>

        </div>

      )}

    </div>
  )
}