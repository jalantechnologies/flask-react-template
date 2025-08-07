import * as React from 'react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => (
  <div>
    <h2>Welcome to your Dashboard</h2>
    <p>This is a link to a sample task page. Click it to see your comments section!</p>
    <Link to="/tasks/temp-task-1">Go to Sample Task</Link>
  </div>
);

export default Dashboard;