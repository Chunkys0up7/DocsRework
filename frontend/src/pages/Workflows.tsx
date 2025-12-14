import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Plus, Search, Filter, Download, GitMerge, PlayCircle } from 'lucide-react';
import { workflowsApi, Workflow } from '../lib/api';
import { toast } from 'react-hot-toast';

export default function WorkflowsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOwner, setFilterOwner] = useState('');

  // Fetch workflows using React Query
  const { data: workflows, isLoading, error } = useQuery({
    queryKey: ['workflows', filterOwner],
    queryFn: () => workflowsApi.list({ owner: filterOwner || undefined }),
  });

  // Filter workflows by search term
  const filteredWorkflows = workflows?.filter((workflow) =>
    workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    workflow.description.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this workflow?')) {
      try {
        await workflowsApi.delete(id);
        toast.success('Workflow deleted successfully');
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Failed to delete workflow');
      }
    }
  };

  if (error) {
    return (
      <div className="alert alert-error">
        <p>Error loading workflows: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-semibold text-zinc-900">Workflows</h2>
          <p className="mt-2 text-sm text-zinc-600">
            Manage end-to-end business processes and orchestration
          </p>
        </div>
        <button className="btn-primary inline-flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Create Workflow
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
                placeholder="Search workflows..."
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

      {/* Workflows Table */}
      <div className="card">
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="p-12 text-center">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
              <p className="mt-4 text-sm text-zinc-600">Loading workflows...</p>
            </div>
          ) : filteredWorkflows.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-zinc-600">No workflows found</p>
              <p className="mt-2 text-sm text-zinc-500">
                {searchTerm || filterOwner
                  ? 'Try adjusting your filters'
                  : 'Create your first workflow to get started'}
              </p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Version</th>
                  <th>Components</th>
                  <th>Risks</th>
                  <th>Controls</th>
                  <th>Tags</th>
                  <th>Owner</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredWorkflows.map((workflow) => (
                  <tr key={workflow.id}>
                    <td className="font-mono text-xs">{workflow.id}</td>
                    <td>
                      <div>
                        <p className="font-medium text-zinc-900">{workflow.name}</p>
                        <p className="text-xs text-zinc-500 truncate max-w-xs">
                          {workflow.description}
                        </p>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-neutral">{workflow.version}</span>
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <GitMerge className="h-3 w-3 text-zinc-400" />
                        <span className="badge badge-info">
                          {workflow.components.length}
                        </span>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-warning">
                        {workflow.risks.length}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-success">
                        {workflow.controls.length}
                      </span>
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {workflow.tags?.slice(0, 2).map((tag, idx) => (
                          <span key={idx} className="badge badge-neutral text-xs">
                            {tag}
                          </span>
                        ))}
                        {(workflow.tags?.length || 0) > 2 && (
                          <span className="badge badge-neutral text-xs">
                            +{(workflow.tags?.length || 0) - 2}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="text-sm">{workflow.owner}</td>
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
                          onClick={() => handleDelete(workflow.id)}
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
        {filteredWorkflows.length > 0 && (
          <div className="card-footer flex items-center justify-between">
            <p className="text-sm text-zinc-600">
              Showing {filteredWorkflows.length} of {workflows?.length || 0} workflows
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
