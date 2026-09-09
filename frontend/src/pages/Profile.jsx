import { useState } from "react"
import "../styles/profile.css"

export default function Profile({
    session,
    onLogout
}) {
    const email = session?.user?.email || ""
    const initial = email.charAt(0).toUpperCase() || "U"

    const [showLogoutConfirm, setShowLogoutConfirm] = useState(false)

    const createdAt = session?.user?.created_at
        ? new Date(session.user.created_at).toLocaleDateString(
            undefined,
            {
                day: "numeric",
                month: "long",
                year: "numeric"
            }
        )
        : "—"

    return (
        <div className="profile-page">

            <div className="page-heading">
                <div>
                    <span className="section-eyebrow">
                        ACCOUNT
                    </span>

                    <h1>
                        Profile
                    </h1>

                    <p>
                        Manage your CAMRA account information.
                    </p>
                </div>
            </div>


            <div className="profile-layout">

                <section className="profile-card">

                    <div className="profile-card-header">

                        <div className="profile-large-avatar">
                            {initial}
                        </div>

                    </div>


                    <div className="profile-details">

                        <div className="profile-detail">

                            <div className="profile-detail-icon">
                                <span>@</span>
                            </div>

                            <div>
                                <span>
                                    Email address
                                </span>

                                <strong>
                                    {email}
                                </strong>
                            </div>

                        </div>


                        <div className="profile-detail">

                            <div className="profile-detail-icon">
                                ✓
                            </div>

                            <div>
                                <span>
                                    Account created
                                </span>

                                <strong>
                                    {createdAt}
                                </strong>
                            </div>

                        </div>

                    </div>

                </section>


                <aside className="profile-side">

                    <div className="profile-logout-card">

                        <div>
                            <span className="section-eyebrow">
                                ACCOUNT
                            </span>

                            <h3>
                                Sign out
                            </h3>

                            <p>
                                Sign out of your CAMRA account on this device.
                            </p>
                        </div>

                        <button
                            type="button"
                            className="profile-logout-button"
                            onClick={() => setShowLogoutConfirm(true)}
                        >
                            Log out
                        </button>

                    </div>

                </aside>

            </div>


            {showLogoutConfirm && (
                <div
                    className="modal-backdrop"
                    onClick={() => setShowLogoutConfirm(false)}
                >

                    <div
                        className="logout-modal"
                        onClick={(event) => event.stopPropagation()}
                    >

                        <span className="section-eyebrow">
                            SIGN OUT
                        </span>

                        <h2>
                            Log out of CAMRA?
                        </h2>

                        <p>
                            You'll need to sign in again to access
                            your reports.
                        </p>

                        <div className="modal-actions">

                            <button
                                type="button"
                                className="modal-cancel"
                                onClick={() => setShowLogoutConfirm(false)}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="modal-confirm"
                                onClick={onLogout}
                            >
                                Log out
                            </button>

                        </div>

                    </div>

                </div>
            )}

        </div>
    )
}