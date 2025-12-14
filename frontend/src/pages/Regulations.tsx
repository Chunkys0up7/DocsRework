import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Plus, Search, Filter, Download, Scale, Globe, FileText } from 'lucide-react';
import { regulationsApi, Regulation } from '../lib/api';
import { toast } from 'react-hot-toast';

export default function RegulationsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterJurisdiction, setFilterJurisdiction] = useState('');
  const [filterCategory, setFilterCategory] = useState('');

  // Fetch regulations using React Query
  const { data: regulations, isLoading, error } = useQuery({
    queryKey: ['regulations', filterJurisdiction, filterCategory],
    queryFn: () => regulationsApi.list({
      jurisdiction: filterJurisdiction || undefined,
      category: filterCategory || undefined
    }),
  });

  // Filter regulations by search term
  const filteredRegulations = regulations?.filter((regulation) =>
    regulation.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    regulation.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    regulation.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    regulation.shortName?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this regulation?')) {
      try:
        await regulationsApi.delete(id);
        toast.success('Regulation deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to delete regulation');
      }
    }
  };

  if (error) {
    return (
      <div className="alert alert-error">
        <p>Error loading regulations: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-zinc-900">Regulations</h2>
          <p className="mt-2 text-sm text-zinc-600">
            Manage regulatory requirements and compliance obligations
          </p>
        </div>
        <button className="btn-primary inline-flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Create Regulation
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
                placeholder="Search regulations..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Jurisdiction Filter */}
            <div className="relative">
              <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
              <select
                className="input pl-10"
                value={filterJurisdiction}
                onChange={(e) => setFilterJurisdiction(e.target.value)}
              >
                <option value="">All Jurisdictions</option>
                <option value="US">United States</option>
                <option value="EU">European Union</option>
                <option value="UK">United Kingdom</option>
                <option value="APAC">Asia Pacific</option>
                <option value="GLOBAL">Global</option>
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
                <option value="banking">Banking</option>
                <option value="data-protection">Data Protection</option>
                <option value="aml">Anti-Money Laundering</option>
                <option value="kyc">Know Your Customer</option>
                <option value="consumer-protection">Consumer Protection</option>
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

      {/* Regulations Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
              <p className="mt-4 text-sm text-zinc-600">Loading regulations...</p>
            </div>
          ) : filteredRegulations.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-zinc-600">No regulations found</p>
              <p className="mt-2 text-sm text-zinc-500">
                {searchTerm || filterJurisdiction || filterCategory
                  ? 'Try adjusting your filters'
                  : 'Create your first regulation to get started'}
              </p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Category</th>
                  <th>Jurisdictions</th>
                  <th>Requirements</th>
                  <th>Controls</th>
                  <th>Effective Date</th>
                  <th>Owner</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRegulations.map((regulation) => (
                  <tr key={regulation.id}>
                    <td className="font-mono text-xs">{regulation.id}</td>
                    <td>
                      <div>
                        <p className="font-medium text-zinc-900">{regulation.name}</p>
                        {regulation.shortName && (
                          <p className="text-xs text-zinc-500">{regulation.shortName}</p>
                        )}
                        <p className="text-xs text-zinc-500 truncate max-w-xs mt-1">
                          {regulation.description}
                        </p>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-neutral capitalize">{regulation.category}</span>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {regulation.jurisdiction.slice(0, 2).map((j, idx) => (
                          <span key={idx} className="badge badge-neutral text-xs">
                            {j}
                          </span>
                        ))}
                        {regulation.jurisdiction.length > 2 && (
                          <span className="badge badge-neutral text-xs">
                            +{regulation.jurisdiction.length - 2}
                          </span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <FileText className="h-3 w-3 text-zinc-400" />
                        <span className="badge badge-info">
                          {regulation.requirements.length}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-success">
                        {regulation.relatedControls.length}
                      </span>
                    </td>
                    <td className="text-sm">
                      {new Date(regulation.effectiveDate).toLocaleDateString()}
                    </td>
                    <td className="text-sm truncate max-w-32">{regulation.owner}</td>
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
                          onClick={() => handleDelete(regulation.id)}
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
        {filteredRegulations.length > 0 && (
          <div className="card-footer flex items-center justify-between">
            <p className="text-sm text-zinc-600">
              Showing {filteredRegulations.length} of {regulations?.length || 0} regulations
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
