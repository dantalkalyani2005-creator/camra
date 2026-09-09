import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { supabase } from "../supabase"
import {
    UploadIcon,
    FileIcon,
    CheckIcon,
    ArrowIcon
} from "../components/Icons"
import "../styles/upload.css"

const API_URL = import.meta.env.VITE_API_URL

export default function UploadReport() {
    const navigate = useNavigate()

    const [file, setFile] = useState(null)
    const [report, setReport] = useState(null)

    const [reportName, setReportName] = useState("")
    const [additionalInformation, setAdditionalInformation] = useState("")

    const [dragging, setDragging] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    const allowedTypes = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    const selectFile = (selectedFile) => {
        setError("")
        setReport(null)
        setReportName("")
        setAdditionalInformation("")

        if (!selectedFile) return

        if (!allowedTypes.includes(selectedFile.type)) {
            setError("Please upload a PDF, JPG, PNG, or WEBP file.")
            return
        }

        if (selectedFile.size > 10 * 1024 * 1024) {
            setError("File size must be 10 MB or less.")
            return
        }

        setFile(selectedFile)
    }

    const handleFileChange = (event) => {
        selectFile(event.target.files?.[0])
    }

    const handleDrop = (event) => {
        event.preventDefault()
        setDragging(false)

        selectFile(event.dataTransfer.files?.[0])
    }

    const handleUpload = async () => {
        if (!file) return

        setLoading(true)
        setError("")
        setReport(null)

        try {
            const {
                data: sessionData
            } = await supabase.auth.getSession()

            const token = sessionData.session?.access_token

            if (!token) {
                throw new Error(
                    "Your session has expired. Please sign in again."
                )
            }

            const formData = new FormData()
            formData.append("file", file)

            const response = await fetch(
                `${API_URL}/upload`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`
                    },
                    body: formData
                }
            )

            const data = await response.json()

            if (!response.ok) {
                throw new Error(
                    data.detail || "Unable to process the report."
                )
            }

            setReport(data.report)
        } catch (err) {
            setError(
                err.message ||
                "Something went wrong while uploading the report."
            )
        } finally {
            setLoading(false)
        }
    }

    const handleSaveAndAnalyze = async () => {
        if (!report) return

        setLoading(true)
        setError("")

        try {
            const {
                data: sessionData
            } = await supabase.auth.getSession()

            const token = sessionData.session?.access_token

            if (!token) {
                throw new Error(
                    "Your session has expired. Please sign in again."
                )
            }

            /*
             * The name is optional.
             * If the user leaves it empty, use the
             * original uploaded filename.
             */
            const finalReportName =
                reportName.trim() ||
                report.report_name ||
                file?.name ||
                "Medical report"

            const reportToSave = {
                ...report,
                report_name: finalReportName,
                additional_information: additionalInformation.trim()
            }

            const saveResponse = await fetch(
                `${API_URL}/reports/save`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(reportToSave)
                }
            )

            const savedData = await saveResponse.json()

            if (!saveResponse.ok) {
                throw new Error(
                    savedData.detail || "Unable to save the report."
                )
            }

            const reportId =
                savedData.id ||
                savedData.report?.id ||
                savedData.report_id

            if (!reportId) {
                throw new Error(
                    "Report was saved but no report ID was returned."
                )
            }

            const analyzeResponse = await fetch(
                `${API_URL}/reports/${reportId}/analyze`,
                {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            )

            const analyzedData = await analyzeResponse.json()

            if (!analyzeResponse.ok) {
                throw new Error(
                    analyzedData.detail ||
                    "Unable to analyze the report."
                )
            }

            navigate(`/reports/${reportId}`)
        } catch (err) {
            setError(
                err.message ||
                "Something went wrong while analyzing the report."
            )
        } finally {
            setLoading(false)
        }
    }

    const removeFile = () => {
        setFile(null)
        setReport(null)
        setReportName("")
        setAdditionalInformation("")
        setError("")
    }

    return (
        <div className="upload-page">

            <div className="page-heading">

                <div>
                    <span className="section-eyebrow">
                        REPORTS
                    </span>

                    <h1>
                        Upload a medical report
                    </h1>

                    <p>
                        Add a report and CAMRA will extract and organize
                        the information for analysis.
                    </p>
                </div>

            </div>


            <div className="upload-layout">

                <section className="upload-main-card">

                    {!file ? (

                        <label
                            className={
                                dragging
                                    ? "upload-dropzone dragging"
                                    : "upload-dropzone"
                            }
                            onDragOver={(event) => {
                                event.preventDefault()
                                setDragging(true)
                            }}
                            onDragLeave={() => setDragging(false)}
                            onDrop={handleDrop}
                        >

                            <input
                                type="file"
                                accept=".pdf,.jpg,.jpeg,.png,.webp"
                                onChange={handleFileChange}
                                hidden
                            />

                            <div className="upload-icon-large">
                                <UploadIcon size={28} />
                            </div>

                            <h2>
                                Drop your report here
                            </h2>

                            <p>
                                or click to browse files from your computer
                            </p>

                            <span className="upload-formats">
                                PDF, JPG, PNG or WEBP · Maximum 10 MB
                            </span>

                        </label>

                    ) : (

                        <>
                            <div className="selected-file">

                                <div className="selected-file-icon">
                                    <FileIcon size={25} />
                                </div>

                                <div className="selected-file-info">

                                    <strong>
                                        {file.name}
                                    </strong>

                                    <span>
                                        {(file.size / 1024 / 1024).toFixed(2)} MB
                                    </span>

                                </div>

                                <button
                                    type="button"
                                    className="remove-file-button"
                                    onClick={removeFile}
                                    disabled={loading}
                                >
                                    Remove
                                </button>

                            </div>


                            {!report && (
                                <div className="report-name-field">

                                    <label htmlFor="report-name">
                                        Report name
                                        <span>
                                            Optional
                                        </span>
                                    </label>

                                    <input
                                        id="report-name"
                                        type="text"
                                        value={reportName}
                                        onChange={(event) =>
                                            setReportName(event.target.value)
                                        }
                                        placeholder="e.g. Blood test - September"
                                        maxLength={120}
                                    />

                                    <small>
                                        Leave this blank to use the uploaded
                                        filename.
                                    </small>

                                </div>
                            )}
                        </>

                    )}


                    {file && !report && (
                        <button
                            type="button"
                            className="primary-action upload-process-button"
                            onClick={handleUpload}
                            disabled={loading}
                        >
                            <UploadIcon size={18} />

                            <span>
                                {loading
                                    ? "Processing report..."
                                    : "Process report"}
                            </span>

                            {!loading && (
                                <ArrowIcon size={17} />
                            )}
                        </button>
                    )}


                    {report && (
                        <div className="processed-report">

                            <div className="processed-success">

                                <div className="success-icon">
                                    <CheckIcon size={19} />
                                </div>

                                <div>
                                    <strong>
                                        Report processed successfully
                                    </strong>

                                    <span>
                                        The report text has been extracted and
                                        prepared for analysis.
                                    </span>
                                </div>

                            </div>


                            <div className="report-name-field">

                                <label htmlFor="processed-report-name">
                                    Report name
                                    <span>
                                        Optional
                                    </span>
                                </label>

                                <input
                                    id="processed-report-name"
                                    type="text"
                                    value={reportName}
                                    onChange={(event) =>
                                        setReportName(event.target.value)
                                    }
                                    placeholder={
                                        report.report_name ||
                                        file?.name ||
                                        "Medical report"
                                    }
                                    maxLength={120}
                                />

                                <small>
                                    Leave blank to keep the original filename.
                                </small>

                                <div className="additional-information-field">

                                    <label htmlFor="additional-information">
                                        Additional information
                                        <span>Optional</span>
                                    </label>

                                    <textarea
                                        id="additional-information"
                                        value={additionalInformation}
                                        onChange={(event) =>
                                            setAdditionalInformation(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Add anything you want CAMRA to consider while explaining this report..."
                                        maxLength={1000}
                                        rows={5}
                                    />

                                    <small>
                                        You can mention symptoms, concerns, or what you want
                                        CAMRA to focus on. This information is treated as
                                        user-provided context.
                                    </small>

                                </div>

                            </div>


                            <div className="processed-report-preview">

                                <span className="preview-label">
                                    EXTRACTED REPORT DATA
                                </span>

                                <div className="preview-box">
                                    {report.report_data?.report_text
                                        ? report.report_data.report_text
                                        : "No report text was extracted."}
                                </div>

                            </div>


                            <button
                                type="button"
                                className="primary-action"
                                onClick={handleSaveAndAnalyze}
                                disabled={loading}
                            >
                                <span>
                                    {loading
                                        ? "Analyzing report..."
                                        : "Save & analyze"}
                                </span>

                                {!loading && (
                                    <ArrowIcon size={17} />
                                )}
                            </button>

                        </div>
                    )}


                    {error && (
                        <div className="auth-error upload-error">
                            {error}
                        </div>
                    )}

                </section>


                <aside className="upload-side-card">

                    <span className="section-eyebrow">
                        HOW IT WORKS
                    </span>

                    <h3>
                        From report to understanding
                    </h3>


                    <div className="upload-step">

                        <div className="upload-step-number">
                            01
                        </div>

                        <div>
                            <strong>
                                Upload
                            </strong>

                            <p>
                                Add your PDF or image report here to analyse.
                            </p>
                        </div>

                    </div>


                    <div className="upload-step">

                        <div className="upload-step-number">
                            02
                        </div>

                        <div>
                            <strong>
                                Extract
                            </strong>

                            <p>
                                CAMRA extracts the visible report information.
                            </p>
                        </div>

                    </div>


                    <div className="upload-step">

                        <div className="upload-step-number">
                            03
                        </div>

                        <div>
                            <strong>
                                Analyze
                            </strong>

                            <p>
                                Review the report in clear, structured language.
                            </p>
                        </div>

                    </div>


                    <div className="upload-note">

                        <strong>
                            Important
                        </strong>

                        <p>
                            CAMRA helps explain report information for
                            educational purposes. It does not provide a
                            diagnosis or replace your doctor.
                        </p>

                    </div>

                </aside>

            </div>

        </div>
    )
}