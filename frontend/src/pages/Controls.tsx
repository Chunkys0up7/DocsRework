import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Plus, Search, Filter, Download, Shield, Target, Clock } from 'lucide-react';
import { controlsApi, Control } from '../lib/api';
import { toast } from 'react-hot-toast';

export default function ControlsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterOwner, setFilterOwner] = useState('');

  // Fetch controls using React Query
  const { data: controls, isLoading, error } = useQuery({
    queryKey: ['controls', filterType, filterOwner],
    queryFn: () => controlsApi.list({
      owner: filterOwner || undefined
    }),
  });

  // Filter controls by search term and type
  const filteredControls = controls?.filter((control) => {
    const matchesSearch = control.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      control.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      control.description.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = !filterType || control.controlType === filterType;

    return matchesSearch && matchesType;
  }) || [];

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this control?')) {
      try {
        await controlsApi.delete(id);
        toast.success('Control deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to delete control');
      }
    }
  };

  const getEffectivenessColor = (rating: number) => {
    if (rating >= 90) return 'text-green-700 bg-green-100 border-green-200';
    if (rating >= 75) return 'text-blue-700 bg-blue-100 border-blue-200';
    if (rating >= 60) return 'text-yellow-700 bg-yellow-100 border-yellow-200';
    return 'text-red-700 bg-red-100 border-red-200';
  };

  const getControlTypeBadge = (type: string) => {
    const typeColors = {
      preventive: 'bg-indigo-100 text-indigo-800 border-indigo-200',
      detective: 'bg-blue-100 text-blue-800 border-blue-200',
      corrective: 'bg-green-100 text-green-800 border-green-200',
      compensating: 'bg-purple-100 text-purple-800 border-purple-200',
      directive: 'bg-slate-100 text-slate-800 border-slate-200',
    };
    return typeColors[type.toLowerCase() as keyof typeof typeColors] || 'badge-neutral';
  };

  if (error) {
    return (
      <div className="alert alert-error">
        <p>Error loading controls: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-zinc-900">Controls</h2>
          <p className="mt-2 text-sm text-zinc-600">
            Manage control mechanisms and monitor effectiveness
          </p>
        </div>
        <button className="btn-primary inline-flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Create Control
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
                placeholder="Search controls..."
                className="input pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Type Filter */}
            <div className="relative">
              <Shield className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-400" />
              <select
                className="input pl-10"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="">All Control Types</option>
                <option value="preventive">Preventive</option>
                <option value="detective">Detective</option>
                <option value="corrective">Corrective</option>
                <option value="compensating">Compensating</option>
                <option value="directive">Directive</option>
              </select>
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
                <option value="risk-team@bank.example.com">Risk Team</option>
                <option value="compliance-team@bank.example.com">Compliance Team</option>
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

      {/* Controls Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
              <p className="mt-4 text-sm text-zinc-600">Loading controls...</p>
            </div>
          ) : filteredControls.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-zinc-600">No controls found</p>
              <p className="mt-2 text-sm text-zinc-500">
                {searchTerm || filterType || filterOwner
                  ? 'Try adjusting your filters'
                  : 'Create your first control to get started'}
              </p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Effectiveness</th>
                  <th>Automation</th>
                  <th>Frequency</th>
                  <th>Mitigated Risks</th>
                  <th>Owner</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredControls.map((control) => (
                  <tr key={control.id}>
                    <td className="font-mono text-xs">{control.id}</td>
                    <td>
                      <div>
                        <p className="font-medium text-zinc-900">{control.name}</p>
                        <p className="text-xs text-zinc-500 truncate max-w-xs">
                          {control.description}
                        </p>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${getControlTypeBadge(control.controlType)} capitalize`}>
                        {control.controlType}
                      </span>
                    </td>
                    <td>
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                          <Target className="h-3 w-3 text-zinc-400" />
                          <span className={`badge ${getEffectivenessColor(control.effectiveness.rating)}`}>
                            {control.effectiveness.rating}%
                          </span>
                        </div>
                        <span className="text-xs text-zinc-500">
                          Assessed: {new Date(control.effectiveness.lastAssessed).toLocaleDateString()}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-neutral capitalize">
                        {control.automationLevel}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3 text-zinc-400" />
                        <span className="text-sm capitalize">{control.frequency}</span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-warning">
                        {control.mitigatedRisks.length}
                      </span>
                    </td>
                    <td className="text-sm truncate max-w-32">{control.owner}</td>
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
                          onClick={() => handleDelete(control.id)}
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
        {filteredControls.length > 0 && (
          <div className="card-footer flex items-center justify-between">
            <p className="text-sm text-zinc-600">
              Showing {filteredControls.length} of {controls?.length || 0} controls
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
