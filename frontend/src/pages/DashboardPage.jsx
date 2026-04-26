import BreakdownPanel from '../components/dashboard/BreakdownPanel'
import HeroSection from '../components/dashboard/HeroSection'
import HistoryPanel from '../components/dashboard/HistoryPanel'
import InsightsPanel from '../components/dashboard/InsightsPanel'
import ProgressPanel from '../components/dashboard/ProgressPanel'
import SummaryPanel from '../components/dashboard/SummaryPanel'
import UploadPanel from '../components/dashboard/UploadPanel'
import { API_URL } from '../constants/modelConfig'
import { useInference } from '../context/InferenceContext'

const DashboardPage = () => {
  const {
    mode,
    setMode,
    selectedFile,
    selectFile,
    clearSelection,
    clearHistory,
    runClassification,
    isRunning,
    warning,
    error,
    result,
    progress,
    stageLabel,
    probabilityRows,
    activeInsights,
    history,
  } = useInference()

  return (
    <>
      <HeroSection />

      <section className="grid gap-6 lg:grid-cols-2">
        <UploadPanel
          mode={mode}
          setMode={setMode}
          selectedFile={selectedFile}
          selectFile={selectFile}
          clearSelection={clearSelection}
          runClassification={runClassification}
          isRunning={isRunning}
          warning={warning}
          error={error}
          apiUrl={API_URL}
        />

        <SummaryPanel result={result} mode={mode} />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <ProgressPanel progress={progress} stageLabel={stageLabel} isRunning={isRunning} />
        <BreakdownPanel probabilityRows={probabilityRows} />
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <InsightsPanel activeInsights={activeInsights} />
        <HistoryPanel history={history} clearHistory={clearHistory} />
      </section>
    </>
  )
}

export default DashboardPage
