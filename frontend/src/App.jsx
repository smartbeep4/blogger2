import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import PostList from "./components/posts/PostList";

// Header component with navigation
const Header = () => {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="header">
      <div className="container header-content">
        <Link to="/" className="logo">Blogger2</Link>
        <nav className="nav-links">
          {isAuthenticated ? (
            <>
              <Link to="/dashboard">Dashboard</Link>
              <Link to="/posts/new">New Post</Link>
              <span className="nav-user">Hi, {user?.display_name || user?.username}</span>
              <button onClick={logout} className="btn btn-outline">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login">Login</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

// Layout wrapper
const Layout = ({ children }) => (
  <>
    <Header />
    <main className="main-content">
      {children}
    </main>
  </>
);

// Home page with post list
const Home = () => (
  <div className="container mt-3">
    <h1 className="mb-3">Latest Posts</h1>
    <PostList />
  </div>
);
const Login = () => (
  <div className="container mt-3">
    <h1>Login</h1>
  </div>
);
const Register = () => (
  <div className="container mt-3">
    <h1>Register</h1>
  </div>
);
const Dashboard = () => (
  <div className="container mt-3">
    <h1>Dashboard</h1>
  </div>
);
const PostDetail = () => (
  <div className="container mt-3">
    <h1>Post Detail</h1>
  </div>
);
const CreatePost = () => (
  <div className="container mt-3">
    <h1>Create Post</h1>
  </div>
);
const EditPost = () => (
  <div className="container mt-3">
    <h1>Edit Post</h1>
  </div>
);
const Profile = () => (
  <div className="container mt-3">
    <h1>Profile</h1>
  </div>
);
const Analytics = () => (
  <div className="container mt-3">
    <h1>Analytics</h1>
  </div>
);
const UserManagement = () => (
  <div className="container mt-3">
    <h1>User Management</h1>
  </div>
);

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem("access_token");
  return token ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/posts/:slug" element={<PostDetail />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/posts/new"
              element={
                <ProtectedRoute>
                  <CreatePost />
                </ProtectedRoute>
              }
            />
            <Route
              path="/posts/:id/edit"
              element={
                <ProtectedRoute>
                  <EditPost />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Profile />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute>
                  <Analytics />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <ProtectedRoute>
                  <UserManagement />
                </ProtectedRoute>
              }
            />

            {/* 404 */}
            <Route
              path="*"
              element={
                <div className="container mt-3">
                  <h1>404 - Page Not Found</h1>
                </div>
              }
            />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
