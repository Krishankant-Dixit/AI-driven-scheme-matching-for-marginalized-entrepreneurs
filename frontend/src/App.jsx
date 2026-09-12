import { Link, Route, Routes } from "react-router-dom";

import ProfileForm from "./components/ProfileForm";
import RecommendationsPage from "./pages/RecommendationsPage";
import HistoryPage from "./pages/HistoryPage";
import SavedSchemesPage from "./pages/SavedSchemesPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { useAuth } from "./context/AuthContext";
import AdminRoute from "./components/AdminRoute";
import AdminPage from "./pages/AdminPage";
import SchemeDetailsPage from "./pages/SchemeDetailsPage";

function HomePage() {
  return (
    <main className="page-shell">
      <p className="eyebrow">SIH26092 / PHASE 1</p>
      <h1>SchemeMatch</h1>
      <p className="intro">
        A clear path from entrepreneur profile to verified government scheme
        information.
      </p>
      <Link className="primary-link" to="/profile">
        Start a profile
      </Link>
    </main>
  );
}

function ProfilePage() {
  return (
    <main className="profile-shell">
      <div className="profile-heading">
        <Link className="text-link" to="/">SchemeMatch</Link>
        <p className="eyebrow">PHASE 3 / ENTREPRENEUR PROFILE</p>
        <h1>Tell us about your venture.</h1>
        <p className="intro">Required fields are marked. Optional information can be left blank and added later.</p>
      </div>
      <ProfileForm />
    </main>
  );
}

function Navigation() {
  const { user, logout } = useAuth();
  if (!user) return null;
  return <nav className="app-nav"><Link to="/profile">Profile</Link><Link to="/recommendations">Recommendations</Link><Link to="/history">History</Link><Link to="/saved-schemes">Saved schemes</Link><button onClick={logout}>Log out</button></nav>;
}

export default function App() {
  return (
    <><Navigation /><Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/schemes/:schemeId" element={<SchemeDetailsPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/recommendations" element={<RecommendationsPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/saved-schemes" element={<SavedSchemesPage />} />
      </Route>
      <Route element={<AdminRoute />}><Route path="/admin" element={<AdminPage />} /></Route>
    </Routes></>
  );
}
