import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { supabase } from "../supabase"
import {
    FileIcon,
    ArrowIcon,
    TrashIcon
} from "../components/Icons"
import "../styles/history.css"

export default function History() {
    const navigate = useNavigate()

    const [reports, setReports] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState("")

    useEffect(() => {
        loadReports()
    }, [])

    const loadReports = async () => {
        setLoading(true)
        setError("")

        const {
            data,
            error
        } = await supabase
            .from("reports")
            .select("id, report_name, created_at, updated_at, analysis")
            .order("created_at", { ascending: false })

        if (error) {
            setError(error.message)
        } else {
            setReports(data || [])
        }

        setLoading(false)
    }

    const handleDelete = async (event, reportId) => {
        event.stopPropagation()

        const confirmed = window.confirm(
            "Are you sure you want to delete this report?"
        )

        if (!confirmed) return

        const {
            error
        } = await supabase
            .from("reports")
            .delete()
            .eq("id", reportId)

        if (error) {
            setError(error.message)
            return
        }

        setReports((current) =>
            current.filter((report) => report.id !== reportId)
        )
    }

    const openReport = (reportId) => {
        navigate(`/reports/${reportId}`)
    }

    const formatDate = (date) => {
        if (!date) return ""

        return new Date(date).toLocaleDateString(
            undefined,
            {
                day: "numeric",
                month: "short",
                year: "numeric"
            }
        )
    }

    return (
        <div className="history-page">

            <div className="page-heading">

                <div>
                    <span className="section-eyebrow">
                        YOUR REPORTS
                    </span>

                    <h1>
                        My reports
                    </h1>

                    <p>
                        View and manage the medical reports you've
                        uploaded to CAMRA.
                    </p>
                </div>

            </div>


            {error && (
                <div className="auth-error">
                    {error}
                </div>
            )}


            {loading ? (

                <div className="empty-card">
                    Loading your reports...
                </div>

            ) : reports.length === 0 ? (

                <div className="empty-card">

                    <div className="empty-card-icon">
                        <FileIcon size={25} />
                    </div>

                    <h3>
                        No reports yet
                    </h3>

                    <p>
                        Reports you upload will appear here.
                    </p>

                </div>

            ) : (

                <div className="history-list">

                    <div className="history-list-header">
                        <span>
                            REPORT
                        </span>

                        <span>
                            DATE
                        </span>

                        <span>
                            STATUS
                        </span>

                        <span />
                    </div>


                    {reports.map((report) => (

                        <div
                            key={report.id}
                            className="history-row"
                            onClick={() => openReport(report.id)}
                        >

                            <div className="history-report">

                                <div className="history-file-icon">
                                    <FileIcon size={20} />
                                </div>

                                <div className="history-report-info">

                                    <strong>
                                        {report.report_name}
                                    </strong>

                                    <span>
                                        Medical report
                                    </span>

                                </div>

                            </div>


                            <span className="history-date">
                                {formatDate(report.created_at)}
                            </span>


                            <span
                                className={
                                    report.analysis
                                        ? "report-status analyzed"
                                        : "report-status"
                                }
                            >
                                {report.analysis
                                    ? "Analyzed"
                                    : "Uploaded"}
                            </span>


                            <div className="history-actions">

                                <button
                                    type="button"
                                    className="history-open-button"
                                    onClick={(event) => {
                                        event.stopPropagation()
                                        openReport(report.id)
                                    }}
                                    aria-label="Open report"
                                >
                                    <ArrowIcon size={17} />
                                </button>

                                <button
                                    type="button"
                                    className="history-delete-button"
                                    onClick={(event) =>
                                        handleDelete(event, report.id)
                                    }
                                    aria-label="Delete report"
                                >
                                    <TrashIcon size={17} />
                                </button>

                            </div>

                        </div>

                    ))}

                </div>

            )}

        </div>
    )
}