import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Menu, X, LogOut, BarChart3, Users, Truck, ShoppingCart, DollarSign, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Layout({ children, adminInfo, onLogout }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    onLogout()
    navigate('/login')
  }

  const menuItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/captains', label: 'Captains', icon: Truck },
    { path: '/users', label: 'Users', icon: Users },
    { path: '/bookings', label: 'Bookings', icon: ShoppingCart },
    { path: '/financials', label: 'Financials', icon: DollarSign },
  ]

  const isActive = (path) => location.pathname === path

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gradient-to-b from-amber-900 to-amber-800 text-white transition-all duration-300 ease-in-out`}
      >
        {/* Logo */}
        <div className="flex items-center justify-between p-4 border-b border-amber-700">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <BarChart3 className="w-6 h-6" />
              <span className="font-bold text-lg">Tout's Admin</span>
            </div>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-amber-700 rounded"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="mt-8 space-y-2 px-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive(item.path)
                    ? 'bg-amber-700 text-white'
                    : 'text-amber-100 hover:bg-amber-700'
                }`}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Logout Button */}
        <div className="absolute bottom-4 left-2 right-2">
          <button
            onClick={handleLogout}
            className={`flex items-center gap-3 w-full px-4 py-3 rounded-lg text-amber-100 hover:bg-amber-700 transition-colors ${
              !sidebarOpen && 'justify-center'
            }`}
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="flex items-center justify-between px-8 py-4">
            <h1 className="text-2xl font-bold text-gray-800">Tout's Routes Admin Panel</h1>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-semibold text-gray-800">{adminInfo?.name || 'Admin'}</p>
                <p className="text-xs text-gray-500">{adminInfo?.email}</p>
              </div>
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center text-white font-bold">
                {adminInfo?.name?.charAt(0) || 'A'}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto bg-gray-50 p-8">
          {children}
        </main>
      </div>
    </div>
  )
}

