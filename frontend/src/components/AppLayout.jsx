import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"

import Logo from "./Logo"
import ProfileMenu from "./ProfileMenu"

import {
  HomeIcon,
  UploadIcon,
  FileIcon,
  MenuIcon
} from "./Icons"

export default function AppLayout({
  session,
  onLogout,
  children
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const location = useLocation()
  const navigate = useNavigate()

  const navigation = [
    {
      id: "home",
      path: "/home",
      label: "Home",
      icon: <HomeIcon />
    },
    {
      id: "upload",
      path: "/upload",
      label: "Upload report",
      icon: <UploadIcon />
    },
    {
      id: "history",
      path: "/reports",
      label: "My reports",
      icon: <FileIcon />
    }
  ]

  const getActivePage = () => {
    if (location.pathname === "/home") {
      return "home"
    }

    if (location.pathname === "/upload") {
      return "upload"
    }

    if (
      location.pathname === "/reports" ||
      location.pathname.startsWith("/reports/")
    ) {
      return "history"
    }

    if (location.pathname === "/profile") {
      return "profile"
    }

    return "home"
  }

  const activePage = getActivePage()

  const handleNavigation = (path) => {
    navigate(path)
    setMobileMenuOpen(false)
  }

  const handleLogoClick = () => {
    navigate("/home")
    setMobileMenuOpen(false)
  }

  const handleProfile = () => {
    navigate("/profile")
    setMobileMenuOpen(false)
  }

  return (
    <div className="app-layout">

      <header className="top-navbar">

        <div className="navbar-left">

          <button
            className="navbar-logo-button"
            onClick={handleLogoClick}
          >
            <Logo />
          </button>

          <nav className="desktop-navigation">
            {navigation.map((item) => (
              <button
                key={item.id}
                className={
                  activePage === item.id
                    ? "navigation-link active"
                    : "navigation-link"
                }
                onClick={() => handleNavigation(item.path)}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}
          </nav>

        </div>


        <div className="navbar-right">

          <button
            className="mobile-menu-button"
            onClick={() =>
              setMobileMenuOpen((open) => !open)
            }
            aria-label={
              mobileMenuOpen
                ? "Close navigation menu"
                : "Open navigation menu"
            }
            aria-expanded={mobileMenuOpen}
          >
            <MenuIcon />
          </button>

          <ProfileMenu
            session={session}
            onProfile={handleProfile}
            onLogout={onLogout}
          />

        </div>

      </header>


      {mobileMenuOpen && (
        <>
          <div
            className="mobile-menu-backdrop"
            onClick={() => setMobileMenuOpen(false)}
          />

          <nav className="mobile-navigation">

            {navigation.map((item) => (
              <button
                key={item.id}
                className={
                  activePage === item.id
                    ? "mobile-navigation-link active"
                    : "mobile-navigation-link"
                }
                onClick={() => handleNavigation(item.path)}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            ))}


            <div className="mobile-navigation-divider" />


            <button
              className={
                activePage === "profile"
                  ? "mobile-navigation-link active"
                  : "mobile-navigation-link"
              }
              onClick={handleProfile}
            >
              <span className="mobile-profile-icon">•</span>
              <span>Profile</span>
            </button>


            <button
              className="mobile-navigation-link mobile-logout"
              onClick={() => {
                setMobileMenuOpen(false)
                onLogout()
              }}
            >
              <span className="mobile-profile-icon">↪</span>
              <span>Log out</span>
            </button>

          </nav>
        </>
      )}


      <main className="page-container">
        {children}
      </main>


      <footer className="app-footer">
        <span>CAMRA</span>

        <span>
          Context-Aware Medical Report Analyzer
        </span>
      </footer>

    </div>
  )
}