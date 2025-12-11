import { useEffect } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuthContext, useAccountContext } from 'frontend/contexts';
import routes from 'frontend/constants/routes';
import { AsyncError } from 'frontend/types';

interface RouteGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

export const RouteGuard: React.FC<RouteGuardProps> = ({ 
  children, 
  requireAuth = false 
}) => {
  const { isUserAuthenticated, logout } = useAuthContext();
  const { getAccountDetails } = useAccountContext();
  const location = useLocation();
  const navigate = useNavigate();
  const isAuthenticated = isUserAuthenticated();

  // Fetch account details for authenticated routes
  useEffect(() => {
    if (requireAuth && isAuthenticated) {
      getAccountDetails().catch((err: AsyncError) => {
        toast.error(err.message);
        logout();
        navigate(routes.LOGIN);
      });
    }
  }, [requireAuth, isAuthenticated, getAccountDetails, logout, navigate]);

  if (requireAuth && !isAuthenticated) {
    // Redirect to login if authentication is required but user is not authenticated
    return <Navigate to={routes.LOGIN} state={{ from: location }} replace />;
  }

  if (!requireAuth && isAuthenticated) {
    // Redirect to tasks if user is authenticated but trying to access public routes
    return <Navigate to={routes.TASKS} replace />;
  }

  return <>{children}</>;
};