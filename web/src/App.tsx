import { AlertTriangle } from 'lucide-react';
import { useApp } from './app/AppContext';
import SplashScreen from './screens/SplashScreen';
import SetupScreen from './screens/SetupScreen';
import HomeScreen from './screens/HomeScreen';
import Button from './components/ui/Button';

export default function App() {
  const { state, checkHealth } = useApp();

  switch (state.phase) {
    case 'loading':
    case 'splash':
      return (
        <SplashScreen
          status={state.backendStatus}
          message={state.backendMessage}
          onRetry={checkHealth}
        />
      );

    case 'setup':
      return <SetupScreen />;

    case 'home':
      return <HomeScreen />;

    case 'error':
      return (
        <div className="h-full flex items-center justify-center p-6">
          <div className="text-center">
            <AlertTriangle size={48} className="text-error mb-4 mx-auto" />
            <h2 className="text-lg font-bold text-cream mb-2">Something went wrong</h2>
            <p className="text-sm text-text-secondary mb-6">{state.errorMessage}</p>
            <Button variant="primary" onClick={checkHealth}>Retry</Button>
          </div>
        </div>
      );

    default:
      return null;
  }
}
