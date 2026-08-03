import { NavLink } from 'react-router-dom'
import { UploadSimple, ClockCounterClockwise } from '@phosphor-icons/react'

export default function Navbar() {
  const linkClass = ({ isActive }) =>
    [
      'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
      isActive
        ? 'bg-accent-soft text-accent'
        : 'text-text-secondary hover:text-text-primary hover:bg-surface-overlay',
    ].join(' ')

  return (
    <nav className="sticky top-0 z-50 h-16 border-b border-border bg-surface/80 backdrop-blur-xl">
      <div className="mx-auto flex h-full max-w-5xl items-center justify-between px-4 sm:px-6">
        <NavLink to="/" className="flex items-center gap-2 group">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white text-sm font-bold">
            L
          </div>
          <span className="text-lg font-semibold tracking-tight text-text-primary">
            Larisin AI
          </span>
        </NavLink>

        <div className="flex items-center gap-1">
          <NavLink to="/" end className={linkClass}>
            <UploadSimple weight="bold" size={18} />
            <span className="hidden sm:inline">Upload</span>
          </NavLink>
          <NavLink to="/history" className={linkClass}>
            <ClockCounterClockwise weight="bold" size={18} />
            <span className="hidden sm:inline">History</span>
          </NavLink>
        </div>
      </div>
    </nav>
  )
}
