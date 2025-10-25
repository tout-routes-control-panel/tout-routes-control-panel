import { useState, useEffect } from 'react'
import { Users, Truck, ShoppingCart, TrendingUp, AlertCircle } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [activities, setActivities] = useState([])
  const [bookingsTrend, setBookingsTrend] = useState([])
  const [revenueTrend, setRevenueTrend] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      // Fetch overview
      const overviewRes = await fetch('/api/dashboard/overview', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (overviewRes.ok) {
        setOverview(await overviewRes.json())
      }

      // Fetch recent activities
      const activitiesRes = await fetch('/api/dashboard/recent-activity?limit=5', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (activitiesRes.ok) {
        const data = await activitiesRes.json()
        setActivities(data.activities || [])
      }

      // Fetch bookings trend
      const bookingsTrendRes = await fetch('/api/dashboard/charts/bookings-trend?days=7', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (bookingsTrendRes.ok) {
        const data = await bookingsTrendRes.json()
        setBookingsTrend(data.trend_data || [])
      }

      // Fetch revenue trend
      const revenueTrendRes = await fetch('/api/dashboard/charts/revenue-trend?days=7', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (revenueTrendRes.ok) {
        const data = await revenueTrendRes.json()
        setRevenueTrend(data.trend_data || [])
      }

      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div>
      </div>
    )
  }

  const COLORS = ['#B45309', '#F59E0B', '#FBBF24', '#FCD34D']

  return (
    <div className="space-y-8">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Users Card */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Users</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.users?.total || 0}</p>
              <p className="text-xs text-green-600 mt-2">+{overview?.users?.new_today || 0} today</p>
            </div>
            <Users className="w-12 h-12 text-blue-500 opacity-20" />
          </div>
        </div>

        {/* Captains Card */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-amber-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Captains</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.captains?.total || 0}</p>
              <p className="text-xs text-orange-600 mt-2">{overview?.captains?.pending || 0} pending</p>
            </div>
            <Truck className="w-12 h-12 text-amber-500 opacity-20" />
          </div>
        </div>

        {/* Active Bookings Card */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Active Bookings</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.bookings?.active || 0}</p>
              <p className="text-xs text-green-600 mt-2">{overview?.bookings?.today || 0} today</p>
            </div>
            <ShoppingCart className="w-12 h-12 text-green-500 opacity-20" />
          </div>
        </div>

        {/* Revenue Card */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Today's Revenue</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.revenue?.today?.toFixed(2) || 0} EGP</p>
              <p className="text-xs text-purple-600 mt-2">Commission: {overview?.revenue?.commission_today?.toFixed(2) || 0} EGP</p>
            </div>
            <TrendingUp className="w-12 h-12 text-purple-500 opacity-20" />
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bookings Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Bookings Trend (7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={bookingsTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="bookings" stroke="#B45309" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Revenue Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Revenue Trend (7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={revenueTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="revenue" fill="#F59E0B" />
              <Bar dataKey="commission" fill="#B45309" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {activities.length > 0 ? (
            activities.map((activity, index) => (
              <div key={index} className="flex items-start gap-4 pb-4 border-b border-gray-200 last:border-b-0">
                <div className="w-2 h-2 rounded-full bg-amber-600 mt-2 flex-shrink-0"></div>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">{activity.title}</p>
                  <p className="text-sm text-gray-600">{activity.description}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(activity.timestamp).toLocaleString()}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  activity.status === 'Active' || activity.status === 'Completed'
                    ? 'bg-green-100 text-green-800'
                    : activity.status === 'Pending'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {activity.status}
                </span>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-8">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  )
}

