export default function Logo({ light = false }) {
  return (
    <div className={`camra-logo ${light ? "camra-logo-light" : ""}`}>
      <div className="camra-logo-mark">
        C
      </div>

      <span className="camra-logo-text">
        CAMRA
      </span>
    </div>
  )
}