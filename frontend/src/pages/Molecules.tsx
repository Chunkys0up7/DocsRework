import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Plus, Search, Filter, Download, Layers, GitBranch } from 'lucide-react';
import { moleculesApi, Molecule } from '../lib/api';
import { toast } from 'react-hot-toast';

export default function MoleculesPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOwner, setFilterOwner] = useState('');

  // Fetch molecules using React Query
  const { data: molecules, isLoading, error } = useQuery({
    queryKey: ['molecules', filterOwner],
    queryFn: () => moleculesApi.list({ owner: filterOwner || undefined }),
  });

  // Filter molecules by search term
  const filteredMolecules = molecules?.filter((molecule) =>
    molecule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    molecule.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    molecule.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this molecule?')) {
      try {
        await moleculesApi.delete(id);
        toast.success('Molecule deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to delete molecule');
      }
    }
  };

  if (error) {
    return (
      <div className="alert alert-error">
        <p>Error loading molecules: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-zinc-900">Molecules</h2>
          <p className="mt-2 text-sm text-zinc-600">
            Manage multi-step procedures composed from atomic operations
          </p>
        </div>
        <button className="btn-primary inline-flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Create Molecule
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
                placeholder="Search molecules..."
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

      {/* Molecules Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
              <p className="mt-4 text-sm text-zinc-600">Loading molecules...</p>
            </div>
          ) : filteredMolecules.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-zinc-600">No molecules found</p>
              <p className="mt-2 text-sm text-zinc-500">
                {searchTerm || filterOwner
                  ? 'Try adjusting your filters'
                  : 'Create your first molecule to get started'}
              </p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Version</th>
                  <th>Atoms</th>
                  <th>Risks</th>
                  <th>Controls</th>
                  <th>Tags</th>
                  <th>Owner</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredMolecules.map((molecule) => (
                  <tr key={molecule.id}>
                    <td className="font-mono text-xs">{molecule.id}</td>
                    <td>
                      <div>
                        <p className="font-medium text-zinc-900">{molecule.name}</p>
                        <p className="text-xs text-zinc-500 truncate max-w-xs">
                          {molecule.description}
                        </p>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-neutral">{molecule.version}</span>
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <Layers className="h-3 w-3 text-zinc-400" />
                        <span className="badge badge-info">
                          {molecule.atoms.length}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-warning">
                        {molecule.risks.length}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-success">
                        {molecule.controls.length}
                      </span>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {molecule.tags?.slice(0, 2).map((tag, idx) => (
                          <span key={idx} className="badge badge-neutral text-xs">
                            {tag}
                          </span>
                        ))}
                        {(molecule.tags?.length || 0) > 2 && (
                          <span className="badge badge-neutral text-xs">
                            +{(molecule.tags?.length || 0) - 2}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="text-sm">{molecule.owner}</td>
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
                          onClick={() => handleDelete(molecule.id)}
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
        {filteredMolecules.length > 0 && (
          <div className="card-footer flex items-center justify-between">
            <p className="text-sm text-zinc-600">
              Showing {filteredMolecules.length} of {molecules?.length || 0} molecules
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
