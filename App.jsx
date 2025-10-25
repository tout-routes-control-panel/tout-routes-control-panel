import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import CaptainManagement from './pages/CaptainManagement'
import UserManagement from './pages/UserManagement'
import BookingManagement from './pages/BookingManagement'
import FinancialManagement from './pages/FinancialManagement'
import Layout from './components/Layout'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [adminInfo, setAdminInfo] = useState(null)

  useEffect(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('admin_token')
    if (token) {
      setIsAuthenticated(true)
      // Get admin info from localStorage
      const adminData = localStorage.getItem('admin_info')
      if (adminData) {
        setAdminInfo(JSON.parse(adminData))
      }
    }
    setLoading(false)
  }, [])

  const handleLogin = (token, adminData) => {
    localStorage.setItem('admin_token', token)
    localStorage.setItem('admin_info', JSON.stringify(adminData))
    setIsAuthenticated(true)
    setAdminInfo(adminData)
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_info')
    setIsAuthenticated(false)
    setAdminInfo(null)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-amber-50 to-orange-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
          <p className="mt-4 text-amber-800 font-semibold">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LoginPage onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <Layout adminInfo={adminInfo} onLogout={handleLogout}>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/captains" element={<CaptainManagement />} />
                  <Route path="/users" element={<UserManagement />} />
                  <Route path="/bookings" element={<BookingManagement />} />
                  <Route path="/financials" element={<FinancialManagement />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Layout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </Router>
  )
}

export default App

