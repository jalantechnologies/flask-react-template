import React from 'react';
import toast from 'react-hot-toast';
import { useNavigate, Link } from 'react-router-dom';

import routes from 'frontend/constants/routes';
import { AsyncError } from 'frontend/types';
import useLoginForm from './login-form.hook';

export const Login: React.FC = () => {
  const navigate = useNavigate();
  
  const onSuccess = () => {
    navigate(routes.TASKS, { replace: true });
  };

  const onError = (error: AsyncError) => {
    toast.error(error.message);
  };

  const { formik, isLoginLoading } = useLoginForm({ onSuccess, onError });

  const getFormikError = (field: 'username' | 'password') =>
    formik.touched[field] ? formik.errors[field] : '';

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome Back</h1>
            <p className="text-gray-600">Sign in to your account to continue</p>
          </div>

          {/* Login Form */}
          <form onSubmit={formik.handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <input
                  id="username"
                  name="username"
                  type="email"
                  data-testid="username"
                  disabled={isLoginLoading}
                  onBlur={formik.handleBlur}
                  onChange={formik.handleChange}
                  placeholder="Enter your email"
                  value={formik.values.username}
                  className={`w-full px-4 py-3 pl-12 border rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-200 ${
                    getFormikError('username')
                      ? 'border-red-300 bg-red-50'
                      : 'border-gray-300 hover:border-gray-400 focus:border-orange-500'
                  } ${isLoginLoading ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                />
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                </div>
              </div>
              {getFormikError('username') && (
                <p className="mt-2 text-sm text-red-600 flex items-center">
                  <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {getFormikError('username')}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type="password"
                  disabled={isLoginLoading}
                  onBlur={formik.handleBlur}
                  onChange={formik.handleChange}
                  placeholder="Enter your password"
                  value={formik.values.password}
                  className={`w-full px-4 py-3 pl-12 border rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-200 ${
                    getFormikError('password')
                      ? 'border-red-300 bg-red-50'
                      : 'border-gray-300 hover:border-gray-400 focus:border-orange-500'
                  } ${isLoginLoading ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                />
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
              </div>
              {getFormikError('password') && (
                <p className="mt-2 text-sm text-red-600 flex items-center">
                  <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {getFormikError('password')}
                </p>
              )}
            </div>

            {/* Forgot Password Link */}
            <div className="flex justify-end">
              <Link
                to={routes.FORGOT_PASSWORD}
                className="text-sm text-orange-600 hover:text-orange-800 hover:underline font-medium"
              >
                Forgot your password?
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoginLoading}
              className={`w-full py-3 px-4 rounded-xl font-semibold text-white transition-all duration-200 ${
                isLoginLoading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transform hover:scale-[1.02] shadow-lg hover:shadow-xl'
              }`}
            >
              {isLoginLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Signing In...
                </div>
              ) : (
                'Sign In'
              )}
            </button>

            {/* Sign Up Link */}
            <div className="text-center pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600">
                Don't have an account?{' '}
                <Link 
                  to={routes.SIGNUP} 
                  className="text-orange-600 hover:text-orange-800 font-semibold hover:underline"
                >
                  Create one now
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
