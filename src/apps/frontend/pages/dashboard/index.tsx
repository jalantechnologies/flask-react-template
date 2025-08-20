import React from 'react';
import { Link } from 'react-router-dom';

import Button from 'frontend/components/button';
import VerticalStackLayout from 'frontend/components/layouts/vertical-stack-layout';
import routes from 'frontend/constants/routes';
import { ButtonKind } from 'frontend/types';

const Dashboard: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <VerticalStackLayout gap={8}>
        {/* Welcome Section */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome to Task Manager
          </h1>
          <p className="text-lg text-gray-600">
            Stay organized and manage your tasks efficiently
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-4">📋</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Manage Tasks
              </h3>
              <p className="text-gray-600 mb-4">
                Create, edit, and organize your tasks
              </p>
              <Link to={routes.TASKS}>
                <Button kind={ButtonKind.PRIMARY}>View Tasks</Button>
              </Link>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-4">✅</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Stay Productive
              </h3>
              <p className="text-gray-600 mb-4">
                Track your progress and completion
              </p>
              <Link to={routes.TASKS}>
                <Button kind={ButtonKind.PRIMARY}>Create Task</Button>
              </Link>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Track Progress
              </h3>
              <p className="text-gray-600 mb-4">
                Monitor your task completion rates
              </p>
              <Link to={routes.TASKS}>
                <Button kind={ButtonKind.PRIMARY}>View Analytics</Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="bg-gray-50 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start space-x-3">
              <div className="text-green-500 text-xl">✓</div>
              <div>
                <h4 className="font-semibold text-gray-900">
                  Create & Edit Tasks
                </h4>
                <p className="text-gray-600">
                  Easily create new tasks and edit existing ones with a simple
                  form interface
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="text-green-500 text-xl">✓</div>
              <div>
                <h4 className="font-semibold text-gray-900">Task Management</h4>
                <p className="text-gray-600">
                  View all your tasks in a clean, organized list with pagination
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="text-green-500 text-xl">✓</div>
              <div>
                <h4 className="font-semibold text-gray-900">Quick Actions</h4>
                <p className="text-gray-600">
                  Edit or delete tasks directly from the task list interface
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="text-green-500 text-xl">✓</div>
              <div>
                <h4 className="font-semibold text-gray-900">
                  Responsive Design
                </h4>
                <p className="text-gray-600">
                  Access your tasks from any device with our mobile-friendly
                  interface
                </p>
              </div>
            </div>
          </div>
        </div>
      </VerticalStackLayout>
    </div>
  );
};

export default Dashboard;
