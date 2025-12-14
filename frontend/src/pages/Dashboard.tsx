import { Box, GitBranch, Workflow, AlertTriangle, Shield, TrendingUp } from 'lucide-react';

// Mock data for dashboard metrics
const metrics = [
  {
    name: 'Total Atoms',
    value: '127',
    change: '+12%',
    changeType: 'increase' as const,
    icon: Box,
  },
  {
    name: 'Active Workflows',
    value: '34',
    change: '+8%',
    changeType: 'increase' as const,
    icon: Workflow,
  },
  {
    name: 'High Risks',
    value: '8',
    change: '-3%',
    changeType: 'decrease' as const,
    icon: AlertTriangle,
  },
  {
    name: 'Control Effectiveness',
    value: '94%',
    change: '+2%',
    changeType: 'increase' as const,
    icon: Shield,
  },
];

const recentActivity = [
  {
    id: 1,
    type: 'atom',
    action: 'created',
    name: 'verify-customer-identity',
    version: 'v1.0.0',
    timestamp: '2 hours ago',
    user: 'john.doe@bank.example.com',
  },
  {
    id: 2,
    type: 'workflow',
    action: 'updated',
    name: 'retail-account-opening',
    version: 'v2.1.0',
    timestamp: '4 hours ago',
    user: 'jane.smith@bank.example.com',
  },
  {
    id: 3,
    type: 'risk',
    action: 'mitigated',
    name: 'identity-fraud',
    version: 'v1.0.0',
    timestamp: '1 day ago',
    user: 'risk-team@bank.example.com',
  },
];

export default function Dashboard() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-semibold text-zinc-900">Dashboard</h2>
        <p className="mt-2 text-sm text-zinc-600">
          Overview of your knowledge graph and recent activity
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <div key={metric.name} className="card">
              <div className="card-body">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-zinc-600">
                      {metric.name}
                    </p>
                    <p className="mt-2 text-3xl font-semibold text-zinc-900">
                      {metric.value}
                    </p>
                  </div>
                  <div className="p-3 bg-indigo-50 rounded-lg">
                    <Icon className="h-6 w-6 text-indigo-600" />
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  <TrendingUp
                    className={`h-4 w-4 mr-1 ${
                      metric.changeType === 'increase'
                        ? 'text-success'
                        : 'text-error'
                    }`}
                  />
                  <span
                    className={
                      metric.changeType === 'increase'
                        ? 'text-success'
                        : 'text-error'
                    }
                  >
                    {metric.change}
                  </span>
                  <span className="ml-1 text-zinc-500">from last month</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-zinc-900">
              Recent Activity
            </h3>
          </div>
          <div className="card-body p-0">
            <div className="divide-y divide-zinc-200">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="px-6 py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className="badge badge-neutral">
                          {activity.type}
                        </span>
                        <span className="text-sm text-zinc-900 font-medium">
                          {activity.name}
                        </span>
                        <span className="text-xs text-zinc-500">
                          {activity.version}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-zinc-600">
                        {activity.action} by {activity.user}
                      </p>
                    </div>
                    <span className="text-xs text-zinc-500 whitespace-nowrap ml-4">
                      {activity.timestamp}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="card-footer">
            <button className="btn-ghost text-sm">View all activity</button>
          </div>
        </div>

        {/* Compliance Status */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-zinc-900">
              Compliance Status
            </h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-zinc-700">
                    KYC/AML Compliance
                  </span>
                  <span className="text-sm font-semibold text-success">
                    98%
                  </span>
                </div>
                <div className="w-full bg-zinc-200 rounded-full h-2">
                  <div
                    className="bg-success h-2 rounded-full"
                    style={{ width: '98%' }}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-zinc-700">
                    GDPR Compliance
                  </span>
                  <span className="text-sm font-semibold text-success">
                    95%
                  </span>
                </div>
                <div className="w-full bg-zinc-200 rounded-full h-2">
                  <div
                    className="bg-success h-2 rounded-full"
                    style={{ width: '95%' }}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-zinc-700">
                    SOX Compliance
                  </span>
                  <span className="text-sm font-semibold text-warning">
                    87%
                  </span>
                </div>
                <div className="w-full bg-zinc-200 rounded-full h-2">
                  <div
                    className="bg-warning h-2 rounded-full"
                    style={{ width: '87%' }}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-zinc-700">
                    PSD2 Compliance
                  </span>
                  <span className="text-sm font-semibold text-success">
                    92%
                  </span>
                </div>
                <div className="w-full bg-zinc-200 rounded-full h-2">
                  <div
                    className="bg-success h-2 rounded-full"
                    style={{ width: '92%' }}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Heat Map */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-zinc-900">
            Risk Heat Map
          </h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-5 gap-2">
            {[5, 4, 3, 2, 1].map((impact) => (
              <div key={impact} className="contents">
                {[1, 2, 3, 4, 5].map((likelihood) => {
                  const riskScore = impact * likelihood;
                  let colorClass = 'bg-success-light';

                  if (riskScore >= 17) colorClass = 'bg-error-light border-error';
                  else if (riskScore >= 10) colorClass = 'bg-warning-light border-warning';
                  else if (riskScore >= 5) colorClass = 'bg-info-light border-info';

                  return (
                    <div
                      key={`${impact}-${likelihood}`}
                      className={`h-16 rounded border flex items-center justify-center text-sm font-medium ${colorClass}`}
                    >
                      {riskScore}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between text-sm text-zinc-600">
            <span>Likelihood</span>
            <span>Impact</span>
          </div>
        </div>
      </div>
    </div>
  );
}
