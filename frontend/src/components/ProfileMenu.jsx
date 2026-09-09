import { useState } from "react"
import { UserIcon } from "./Icons"

export default function ProfileMenu({
  session,
  onProfile,
  onLogout
}) {
  const [open, setOpen] = useState(false)

  const email = session?.user?.email || ""
  const initial = email.charAt(0).toUpperCase() || "U"

  return (
    <div className="profile-menu">

      <button
        className="profile-trigger"
        onClick={() => setOpen((current) => !current)}
        aria-label="Open profile menu"
      >
        <span className="profile-avatar">
          {initial}
        </span>

        <span className="profile-chevron">
          {open ? "⌃" : "⌄"}
        </span>
      </button>

      {open && (
        <>
          <div
            className="profile-backdrop"
            onClick={() => setOpen(false)}
          />

          <div className="profile-dropdown">

            <div className="profile-dropdown-header">

              <div className="profile-dropdown-avatar">
                {initial}
              </div>

              <div className="profile-dropdown-user">

                <strong>
                  CAMRA User
                </strong>

                <span>
                  {email}
                </span>

              </div>

            </div>

            <div className="profile-dropdown-divider" />

            <button
              className="profile-dropdown-item"
              onClick={() => {
                setOpen(false)
                onProfile()
              }}
            >
              <UserIcon size={17} />

              <span>
                Profile
              </span>
            </button>

            <button
              className="profile-dropdown-item logout"
              onClick={() => {
                setOpen(false)
                onLogout()
              }}
            >
              <span className="logout-icon">
                ↪
              </span>

              <span>
                Log out
              </span>
            </button>

          </div>
        </>
      )}

    </div>
  )
}