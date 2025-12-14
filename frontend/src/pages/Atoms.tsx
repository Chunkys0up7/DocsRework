import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Plus, Search, Filter, Download } from 'lucide-react';
import { atomsApi, Atom } from '../lib/api';
import { toast } from 'react-hot-toast';

export default function AtomsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOwner, setFilterOwner] = useState('');

  // Fetch atoms using React Query
  const { data: atoms, isLoading, error } = useQuery({
    queryKey: ['atoms', filterOwner],
    queryFn: () => atomsApi.list({ owner: filterOwner || undefined }),
  });

  // Filter atoms by search term
  const filteredAtoms = atoms?.filter((atom) =>
    atom.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    atom.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    atom.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this atom?')) {
      try {
        await atomsApi.delete(id);
        toast.success('Atom deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to delete atom');
      }
    }
  };

  if (error) {
    return (
      <div className="alert alert-error">
        <p>Error loading atoms: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-zinc-900">Atoms</h2>
          <p className="mt-2 text-sm text-zinc-600">
            Manage atomic operations in your knowledge graph
          </p>
        </div>
        <button className="btn-primary inline-flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Create Atom
        </button>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
              <input
                type="text"
                placeholder="Search atoms..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Owner Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
              <select
                className="input pl-10"
                value={filterOwner}
                onChange={(e) => setFilterOwner(e.target.value)}
              >
                <option value="">All Owners</option>
                <option value="kyc-team@bank.example.com">KYC Team</option>
                <option value="risk-team@bank.example.com">Risk Team</option>
                <option value="operations-team@bank.example.com">Operations Team</option>
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

      {/* Atoms Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
              <p className="mt-4 text-sm text-zinc-600">Loading atoms...</p>
            </div>
          ) : filteredAtoms.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-zinc-600">No atoms found</p>
              <p className="mt-2 text-sm text-zinc-500">
                {searchTerm || filterOwner
                  ? 'Try adjusting your filters'
                  : 'Create your first atom to get started'}
              </p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Version</th>
                  <th>Owner</th>
                  <th>Risks</th>
                  <th>Controls</th>
                  <th>Tags</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredAtoms.map((atom) => (
                  <tr key={atom.id}>
                    <td className="font-mono text-xs">{atom.id}</td>
                    <td>
                      <div>
                        <p className="font-medium text-zinc-900">{atom.name}</p>
                        <p className="text-xs text-zinc-500 truncate max-w-xs">
                          {atom.description}
                        </p>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-neutral">{atom.version}</span>
                    </td>
                    <td className="text-sm">{atom.owner}</td>
                    <td>
                      <span className="badge badge-warning">
                        {atom.risks.length}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-success">
                        {atom.controls.length}
                      </span>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {atom.tags?.slice(0, 2).map((tag, idx) => (
                          <span key={idx} className="badge badge-neutral text-xs">
                            {tag}
                          </span>
                        ))}
                        {(atom.tags?.length || 0) > 2 && (
                          <span className="badge badge-neutral text-xs">
                            +{(atom.tags?.length || 0) - 2}
                          </span>
                        )}
                      </div>
                    </td>
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
                          onClick={() => handleDelete(atom.id)}
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
        {filteredAtoms.length > 0 && (
          <div className="card-footer flex items-center justify-between">
            <p className="text-sm text-zinc-600">
              Showing {filteredAtoms.length} of {atoms?.length || 0} atoms
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
