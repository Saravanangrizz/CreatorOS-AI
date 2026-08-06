import { AuthProvider, useAuth } from "./context/AuthContext";
import { Landing } from "./pages/Landing";
import { Dashboard } from "./pages/Dashboard";

function Shell() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Dashboard /> : <Landing />;
}

export default function App() {
  return (
    <AuthProvider>
      <Shell />
    </AuthProvider>
  );
}
