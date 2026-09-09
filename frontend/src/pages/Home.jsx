import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { supabase } from "../supabase"
import {
    UploadIcon,
    FileIcon,
    ArrowIcon
} from "../components/Icons"
import "../styles/home.css"

export default function Home({ session }) {
    const navigate = useNavigate()

    const [reports, setReports] = useState([])
    const [totalReports, setTotalReports] = useState(0)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadReports()
    }, [])

    const loadReports = async () => {
        setLoading(true)

        const [
            {
                count,
                error: countError
            },
            {
                data,
                error: reportsError
            }
        ] = await Promise.all([
            supabase
                .from("reports")
                .select("id", {
                    count: "exact",
                    head: true
                }),

            supabase
                .from("reports")
                .select("id, report_name, created_at, analysis")
                .order("created_at", { ascending: false })
                .limit(5)
        ])

        if (!countError) {
            setTotalReports(count || 0)
        }

        if (!reportsError) {
            setReports(data || [])
        }

        setLoading(false)
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
        <div className="home-page">

            <section className="home-hero">

                <div className="home-hero-content">

                    <span className="home-eyebrow">
                        YOUR CAMRA DASHBOARD
                    </span>

                    <h1>
                        Understand your reports,
                        <br />
                        one report at a time.
                    </h1>

                    <p>
                        Upload a medical report and CAMRA will
                        organize its information into clear,
                        understandable insights.
                    </p>

                    <button
                        className="primary-action"
                        onClick={() => navigate("/upload")}
                    >
                        <UploadIcon size={19} />
                        <span>Upload a report</span>
                        <ArrowIcon size={17} />
                    </button>

                </div>

                <div className="home-hero-decoration">

                    <div className="hero-document">

                        <div className="hero-document-top">
                            <span />
                            <span />
                        </div>

                        <div className="hero-document-lines">
                            <span />
                            <span />
                            <span />
                            <span />
                            <span />
                        </div>

                        <div className="hero-document-highlight">
                            <span />
                            <span />
                        </div>

                    </div>

                </div>

            </section>


            <section className="home-stats">

                <div className="stat-card">

                    <div className="stat-icon">
                        <FileIcon size={20} />
                    </div>

                    <div>
                        <span className="stat-label">
                            Total reports
                        </span>

                        <strong>
                            {totalReports}
                        </strong>
                    </div>

                </div>


                <div className="stat-card">

                    <div className="stat-icon">
                        ✓
                    </div>

                    <div>
                        <span className="stat-label">
                            Report analysis
                        </span>

                        <strong>
                            Available
                        </strong>
                    </div>

                </div>

            </section>


            <section className="home-section">

                <div className="section-heading">

                    <div>
                        <span className="section-eyebrow">
                            RECENT ACTIVITY
                        </span>

                        <h2>
                            Recent reports
                        </h2>
                    </div>

                    {reports.length > 0 && (
                        <button
                            className="section-link"
                            onClick={() => navigate("/reports")}
                        >
                            View all
                            <ArrowIcon size={16} />
                        </button>
                    )}

                </div>


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
                            Upload your first medical report to
                            start building your CAMRA history.
                        </p>

                        <button
                            className="secondary-action"
                            onClick={() => navigate("/upload")}
                        >
                            Upload your first report
                            <ArrowIcon size={16} />
                        </button>

                    </div>

                ) : (

                    <div className="recent-reports">

                        {reports.map((report) => (

                            <button
                                key={report.id}
                                className="recent-report-card"
                                onClick={() =>
                                    navigate(`/reports/${report.id}`)
                                }
                            >

                                <div className="recent-report-icon">
                                    <FileIcon size={21} />
                                </div>

                                <div className="recent-report-info">

                                    <strong>
                                        {report.report_name}
                                    </strong>

                                    <span>
                                        {formatDate(report.created_at)}
                                    </span>

                                </div>

                                <div className="recent-report-status">
                                    {report.analysis
                                        ? "Analyzed"
                                        : "Uploaded"}
                                </div>

                                <ArrowIcon
                                    size={18}
                                    className="recent-report-arrow"
                                />

                            </button>

                        ))}

                    </div>

                )}

            </section>


            <section className="home-info-grid">

                <div className="info-card">

                    <span className="info-number">
                        01
                    </span>

                    <h3>
                        Upload
                    </h3>

                    <p>
                        Add your medical report as a PDF or
                        supported image file.
                    </p>

                </div>


                <div className="info-card">

                    <span className="info-number">
                        02
                    </span>

                    <h3>
                        Analyze
                    </h3>

                    <p>
                        CAMRA processes the report and organizes
                        its information for easier understanding.
                    </p>

                </div>


                <div className="info-card">

                    <span className="info-number">
                        03
                    </span>

                    <h3>
                        Understand
                    </h3>

                    <p>
                        Review the findings and questions you may
                        want to discuss with your doctor.
                    </p>

                </div>

            </section>


            <div className="home-disclaimer">
                CAMRA is an educational report-understanding
                tool and does not replace professional medical advice.
            </div>

        </div>
    )
}