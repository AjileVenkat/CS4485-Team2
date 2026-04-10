import { Route, Routes } from 'react-router-dom'
import AppLayout from './app/AppLayout'
import { InferenceProvider } from './context/InferenceContext'
import DashboardPage from './pages/DashboardPage'
import NotFoundPage from './pages/NotFoundPage'
import PipelinePage from './pages/PipelinePage'
import ProjectPage from './pages/ProjectPage'

const App = () => {
  return (
    <InferenceProvider>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/pipeline" element={<PipelinePage />} />
          <Route path="/project" element={<ProjectPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </InferenceProvider>
  )
}

export default App
