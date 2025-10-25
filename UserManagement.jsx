import { useState, useEffect } from 'react'
import { Search, AlertCircle, Eye, Lock, Unlock } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [selectedUser, setSelectedUser] = useState(null)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    fetchUsers()
  }, [page, statusFilter])

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      let url = `/api/users?page=${page}&per_page=10`
      
      if (statusFilter) {
        url += `&status=${statusFilter}`
      }
      if (searchTerm) {
        url += `&search=${searchTerm}`
      }

      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (res.ok) {
        const data = await res.json()
        setUsers(data.users)
        setTotalPages(data.pages)
      } else {
        setError('Failed to fetch users')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    setPage(1)
    fetchUsers()
  }

  const handleStatusChange = async (userId, newStatus) => {
    try {
      const token = localStorage.getItem('admin_token')
      const res = await fetch(`/api/users/${userId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: newStatus })
      })

      if (res.ok) {
        fetchUsers()
        setShowModal(false)
      } else {
        setError('Failed to update user status')
      }
    } catch (err) {
      setError(err.message)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'bg-green-100 text-green-800'
      case 'Deactivated':
        return 'bg-orange-100 text-orange-800'
      case 'Blocked':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600"></div></div>
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-800">User Management</h1>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, email, or phone..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value)
              setPage(1)
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
          >
            <option value="">All Status</option>
            <option value="Active">Active</option>
            <option value="Deactivated">Deactivated</option>
            <option value="Blocked">Blocked</option>
          </select>
          <Button type="submit" className="bg-amber-600 hover:bg-amber-700">
            Search
          </Button>
        </form>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bookings</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Spent</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {users.length > 0 ? (
              users.map((user) => (
                <tr key={user.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{user.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{user.phone_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{user.statistics?.total_bookings || 0}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{user.statistics?.total_spent?.toFixed(2) || 0} EGP</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(user.status)}`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => {
                        setSelectedUser(user)
                        setShowModal(true)
                      }}
                      className="text-amber-600 hover:text-amber-800 font-medium"
                    >
                      <Eye className="w-4 h-4 inline" /> View
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                  No users found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">Page {page} of {totalPages}</p>
        <div className="flex gap-2">
          <Button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 disabled:opacity-50"
          >
            Previous
          </Button>
          <Button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 disabled:opacity-50"
          >
            Next
          </Button>
        </div>
      </div>

      {/* Modal */}
      {showModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">{selectedUser.name}</h2>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-600">Email</p>
                  <p className="font-medium text-gray-800">{selectedUser.email}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Phone</p>
                  <p className="font-medium text-gray-800">{selectedUser.phone_number}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Bookings</p>
                  <p className="font-medium text-gray-800">{selectedUser.statistics?.total_bookings || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Total Spent</p>
                  <p className="font-medium text-gray-800">{selectedUser.statistics?.total_spent?.toFixed(2) || 0} EGP</p>
                </div>
              </div>

              <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold text-gray-800 mb-3">Change Status</h3>
                <div className="flex gap-2">
                  <Button
                    onClick={() => handleStatusChange(selectedUser.user_id, 'Active')}
                    className={`flex-1 ${selectedUser.status === 'Active' ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-300 hover:bg-gray-400'} text-white`}
                  >
                    <Unlock className="w-4 h-4 mr-2" /> Activate
                  </Button>
                  <Button
                    onClick={() => handleStatusChange(selectedUser.user_id, 'Deactivated')}
                    className={`flex-1 ${selectedUser.status === 'Deactivated' ? 'bg-orange-600 hover:bg-orange-700' : 'bg-gray-300 hover:bg-gray-400'} text-white`}
                  >
                    <Lock className="w-4 h-4 mr-2" /> Deactivate
                  </Button>
                  <Button
                    onClick={() => handleStatusChange(selectedUser.user_id, 'Blocked')}
                    className={`flex-1 ${selectedUser.status === 'Blocked' ? 'bg-red-600 hover:bg-red-700' : 'bg-gray-300 hover:bg-gray-400'} text-white`}
                  >
                    <Lock className="w-4 h-4 mr-2" /> Block
                  </Button>
                </div>
              </div>

              <button
                onClick={() => setShowModal(false)}
                className="w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

