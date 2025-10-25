import { useState, useEffect } from 'react'
import { AlertCircle, TrendingUp, DollarSign, PieChart as PieChartIcon } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Button } from '@/components/ui/button'

export default function FinancialManagement() {
  const [overview, setOverview] = useState(null)
  const [dailyRevenue, setDailyRevenue] = useState([])
  const [commissions, setCommissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  useEffect(() => {
    fetchFinancialData()
  }, [])

  const fetchFinancialData = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      
      // Fetch overview
      const overviewRes = await fetch('/api/financials/overview', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (overviewRes.ok) {
        setOverview(await overviewRes.json())
      }

      // Fetch daily revenue
      const dailyRes = await fetch('/api/financials/daily-revenue?days=30', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (dailyRes.ok) {
        const data = await dailyRes.json()
        setDailyRevenue(data.daily_revenue || [])
      }

      // Fetch commissions
      const commissionsRes = await fetch('/api/financials/commissions?page=1&per_page=10', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (commissionsRes.ok) {
        const data = await commissionsRes.json()
        setCommissions(data.commissions || [])
      }

      setLoading(false)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div></div>
  }

  return (
    <div className="space-y-8">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">Financial Management</h1>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Revenue */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Total Revenue</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.overview?.total_revenue?.toFixed(2) || 0} EGP</p>
              <p className="text-xs text-gray-500 mt-2">This period</p>
            </div>
            <DollarSign className="w-12 h-12 text-green-500 opacity-20" />
          </div>
        </div>

        {/* Total Commission */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-amber-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">App Commission</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.overview?.total_commission?.toFixed(2) || 0} EGP</p>
              <p className="text-xs text-amber-600 mt-2">{overview?.overview?.commission_percentage?.toFixed(2) || 0}% of revenue</p>
            </div>
            <TrendingUp className="w-12 h-12 text-amber-500 opacity-20" />
          </div>
        </div>

        {/* Captain Earnings */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">Captain Earnings</p>
              <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.overview?.total_captain_earnings?.toFixed(2) || 0} EGP</p>
              <p className="text-xs text-blue-600 mt-2">Distributed to captains</p>
            </div>
            <PieChartIcon className="w-12 h-12 text-blue-500 opacity-20" />
          </div>
        </div>

        {/* Payment Methods */}
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-purple-500">
          <div>
            <p className="text-gray-600 text-sm font-medium mb-3">Payment Methods</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Cash:</span>
                <span className="font-medium">{overview?.payment_methods?.cash?.toFixed(2) || 0} EGP</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">InstaPay:</span>
                <span className="font-medium">{overview?.payment_methods?.instapay?.toFixed(2) || 0} EGP</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Revenue Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Daily Revenue (Last 30 Days)</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={dailyRevenue}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="total_revenue" fill="#10B981" name="Revenue" />
            <Bar dataKey="total_commission" fill="#B45309" name="Commission" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Commission Details */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Commission Transactions</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-gray-700">Booking ID</th>
                <th className="px-4 py-3 text-left font-medium text-gray-700">User</th>
                <th className="px-4 py-3 text-left font-medium text-gray-700">Captain</th>
                <th className="px-4 py-3 text-left font-medium text-gray-700">Final Fare</th>
                <th className="px-4 py-3 text-left font-medium text-gray-700">Commission</th>
                <th className="px-4 py-3 text-left font-medium text-gray-700">Captain Earning</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {commissions.length > 0 ? (
                commissions.map((commission) => (
                  <tr key={commission.booking_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">#{commission.booking_id}</td>
                    <td className="px-4 py-3 text-gray-600">{commission.user_name}</td>
                    <td className="px-4 py-3 text-gray-600">{commission.captain_name}</td>
                    <td className="px-4 py-3 font-medium">{commission.final_fare?.toFixed(2)} EGP</td>
                    <td className="px-4 py-3 text-amber-600 font-medium">{commission.app_commission?.toFixed(2)} EGP</td>
                    <td className="px-4 py-3 text-green-600 font-medium">{commission.captain_earning?.toFixed(2)} EGP</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                    No commission data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Export Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Export Financial Data</h3>
        <div className="flex gap-4">
          <Button className="bg-amber-600 hover:bg-amber-700 text-white">
            Export Transactions
          </Button>
          <Button className="bg-amber-600 hover:bg-amber-700 text-white">
            Export Commissions
          </Button>
          <Button className="bg-amber-600 hover:bg-amber-700 text-white">
            Export Revenue Report
          </Button>
        </div>
      </div>
    </div>
  )
}

