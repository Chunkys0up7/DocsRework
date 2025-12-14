import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Plus, Search, Filter, Download, AlertTriangle, Shield } from 'lucide-react';
import { risksApi, Risk } from '../lib/api';
import { toast } from 'react-hot-toast';

export default function RisksPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLevel, setFilterLevel] = useState('');
  const [filterCategory, setFilterCategory] = useState('');

  // Fetch risks using React Query
  const { data: risks, isLoading, error } = useQuery({
    queryKey: ['risks', filterLevel, filterCategory],
    queryFn: () => risksApi.list({
      level: filterLevel || undefined,
      category: filterCategory || undefined
    }),
  });

  // Filter risks by search term
  const filteredRisks = risks?.filter((risk) =>
    risk.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    risk.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    risk.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this risk?')) {
      try {
        await risksApi.delete(id);
        toast.success('Risk deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to delete risk');
      }
    }
  };

  const getRiskLevelBadge = (level: string) => {
    const levelUpper = level.toUpperCase();
    const colorClasses = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-200',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      LOW: 'bg-green-100 text-green-800 border-green-200',
    };
    return (
      <span className={`badge ${colorClasses[levelUpper as keyof typeof colorClasses] || 'badge-neutral'}`}>
        {levelUpper}
      </span>
    );
  };

  if (error) {
    return (
      <div className="alert alert-error">
        <p>Error loading risks: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-zinc-900">Risks</h2>
          <p className="mt-2 text-sm text-zinc-600">
            Manage and monitor risk definitions across all processes
          </p>
        </div>
        <button className="btn-primary inline-flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Create Risk
        </button>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
              <input
                type="text"
                placeholder="Search risks..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Level Filter */}
            <div className="relative">
              <AlertTriangle className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
              <select
                className="input pl-10"
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value)}
              >
                <option value="">All Risk Levels</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            {/* Category Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
              <select
                className="input pl-10"
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                <option value="operational">Operational</option>
                <option value="compliance">Compliance</option>
                <option value="financial">Financial</option>
                <option value="reputational">Reputational</option>
                <option value="strategic">Strategic</option>
              </select>
            </div>

            {/* Export */}
            <button className="btn-outline inline-flex items-center justify-center">
              <Download className="h-4 w-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Risks Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
              <p className="mt-4 text-sm text-zinc-600">Loading risks...</p>
            </div>
          ) : filteredRisks.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-zinc-600">No risks found</p>
              <p className="mt-2 text-sm text-zinc-500">
                {searchTerm || filterLevel || filterCategory
                  ? 'Try adjusting your filters'
                  : 'Create your first risk to get started'}
              </p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Category</th>
                  <th>Inherent Risk</th>
                  <th>Residual Risk</th>
                  <th>Likelihood</th>
                  <th>Impact</th>
                  <th>Controls</th>
                  <th>Owner</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRisks.map((risk) => (
                  <tr key={risk.id}>
                    <td className="font-mono text-xs">{risk.id}</td>
                    <td>
                      <div>
                        <p className="font-medium text-zinc-900">{risk.name}</p>
                        <p className="text-xs text-zinc-500 truncate max-w-xs">
                          {risk.description}
                        </p>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-neutral capitalize">{risk.category}</span>
                    </td>
                    <td>
                      <div className="flex flex-col gap-1">
                        {getRiskLevelBadge(risk.inherentRisk.level)}
                        <span className="text-xs text-zinc-500">
                          Score: {risk.inherentRisk.score}
                        </span>
                      </div>
                    </td>
                    <td>
                      {risk.residualRisk ? (
                        <div className="flex flex-col gap-1">
                          {getRiskLevelBadge(risk.residualRisk.level)}
                          <span className="text-xs text-zinc-500">
                            Score: {risk.residualRisk.score}
                          </span>
                        </div>
                      ) : (
                        <span className="text-xs text-zinc-400">Not calculated</span>
                      )}
                    </td>
                    <td>
                      <span className="badge badge-warning">{risk.likelihood.score}/5</span>
                    </td>
                    <td>
                      <span className="badge badge-error">{risk.impact.score}/5</span>
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <Shield className="h-3 w-3 text-zinc-400" />
                        <span className="badge badge-success">
                          {risk.controls.length}
                        </span>
                      </div>
                    </td>
                    <td className="text-sm truncate max-w-32">{risk.owner}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        <button className="btn-ghost text-xs px-2 py-1">
                          View
                        </button>
                        <button className="btn-ghost text-xs px-2 py-1">
                          Edit
                        </button>
                        <button
                          className="btn-ghost text-xs px-2 py-1 text-error hover:bg-error-light"
                          onClick={() => handleDelete(risk.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination Footer */}
        {filteredRisks.length > 0 && (
          <div className="card-footer flex items-center justify-between">
            <p className="text-sm text-zinc-600">
              Showing {filteredRisks.length} of {risks?.length || 0} risks
            </p>
            <div className="flex items-center gap-2">
              <button className="btn-outline text-sm px-3 py-1" disabled>
                Previous
              </button>
              <button className="btn-outline text-sm px-3 py-1" disabled>
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
