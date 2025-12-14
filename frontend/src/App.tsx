import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import AtomsPage from './pages/Atoms';
import MoleculesPage from './pages/Molecules';
import WorkflowsPage from './pages/Workflows';
import RisksPage from './pages/Risks';
import ControlsPage from './pages/Controls';
import RegulationsPage from './pages/Regulations';
import AnalyticsPage from './pages/Analytics';
import './index.css';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/atoms" element={<AtomsPage />} />
            <Route path="/molecules" element={<MoleculesPage />} />
            <Route path="/workflows" element={<WorkflowsPage />} />
            <Route path="/risks" element={<RisksPage />} />
            <Route path="/controls" element={<ControlsPage />} />
            <Route path="/regulations" element={<RegulationsPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#ffffff',
            color: '#18181b',
            border: '1px solid #e4e4e7',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          },
          success: {
            iconTheme: {
              primary: '#059669',
              secondary: '#ffffff',
            },
          },
          error: {
            iconTheme: {
              primary: '#dc2626',
              secondary: '#ffffff',
            },
          },
        }}
      />
    </QueryClientProvider>
  );
}

export default App;
