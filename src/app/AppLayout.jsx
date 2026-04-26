import { Outlet } from 'react-router-dom'
import TopNav from '../components/navigation/TopNav'

const AppLayout = () => {
  return (
    <div className="relative min-h-screen px-4 py-8 md:px-8 md:py-10">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute left-[-12rem] top-[10rem] h-[22rem] w-[22rem] rounded-full bg-cyan-200/30 blur-3xl" />
        <div className="absolute right-[-8rem] top-[16rem] h-[20rem] w-[20rem] rounded-full bg-orange-200/30 blur-3xl" />
      </div>

      <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <TopNav />

        <main className="space-y-6">
          <Outlet />
        </main>

        <footer className="px-2 pb-6 pt-2 text-center text-xs text-slate-500 md:text-sm">
          CS4485 Team 2 | v1.0.0
        </footer>
      </div>
    </div>
  )
}

export default AppLayout
