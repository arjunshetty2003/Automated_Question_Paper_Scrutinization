import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/common/Header';
import Login from './components/common/Login';
import Register from './components/common/Register';
import ProtectedRoute from './components/common/ProtectedRoute';
import AdminDashboard from './components/admin/AdminDashboard';
import SubjectManagement from './components/admin/SubjectManagement';
import TeacherDashboard from './components/teacher/TeacherDashboard';
import QuestionPaperValidator from './components/teacher/QuestionPaperValidator';
import LoadingSpinner from './components/common/LoadingSpinner';

function AppContent() {
  const { loading, isAuthenticated, isAdmin } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      {isAuthenticated && <Header />}
      <main className={isAuthenticated ? 'pt-0' : ''}>
        <Routes>
          {/* Public routes */}
          <Route 
            path="/login" 
            element={!isAuthenticated ? <Login /> : <Navigate to={isAdmin ? "/admin" : "/dashboard"} replace />} 
          />
          <Route 
            path="/register" 
            element={!isAuthenticated ? <Register /> : <Navigate to={isAdmin ? "/admin" : "/dashboard"} replace />} 
          />
          
          {/* Protected admin routes */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute adminOnly>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/subjects"
            element={
              <ProtectedRoute adminOnly>
                <SubjectManagement />
              </ProtectedRoute>
            }
          />
          
          {/* Protected teacher routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <TeacherDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/validate"
            element={
              <ProtectedRoute>
                <QuestionPaperValidator />
              </ProtectedRoute>
            }
          />
          
          {/* Default redirect */}
          <Route 
            path="/" 
            element={
              isAuthenticated ? (
                <Navigate to={isAdmin ? "/admin" : "/dashboard"} replace />
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
