import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/common/Layout'
import DashboardPage from './pages/DashboardPage'
import ServicesPage from './pages/ServicesPage'
import DeploymentsPage from './pages/DeploymentsPage'
import IncidentsPage from './pages/IncidentsPage'
import EnvironmentsPage from './pages/EnvironmentsPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="services" element={<ServicesPage />} />
          <Route path="deployments" element={<DeploymentsPage />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="environments" element={<EnvironmentsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
