import React from 'react';
import { useParams } from 'react-router-dom';
import Comments from '../../components/Comments';

const TaskDetails = () => {
    const { taskId } = useParams<{ taskId: string }>();

    if (!taskId) {
        return <div>No task ID provided.</div>;
    }

    return (
        <div style={{ padding: '20px' }}>
            <h2>Task Details for: {taskId}</h2>
            <p>This is where the full task details would be.</p>
            <Comments taskId={taskId} />
        </div>
    );
};

export default TaskDetails;