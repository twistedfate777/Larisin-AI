import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function Layout() {
  return (
    <div className="min-h-[100dvh] flex flex-col">
      <Navbar />
      <main className="flex-1 mx-auto w-full max-w-5xl px-4 sm:px-6 py-8">
        <Outlet />
      </main>
    </div>
  )
}
