import React from "react";
import CommentSection from "../../components/CommentSection";

const TaskDetail = () => {
  const taskId = 1; // Replace with dynamic ID as needed

  return (
    <div>
      <h2>Task Detail Page</h2>
      <p>This is where you show the task info.</p>

      <CommentSection taskId={taskId} />
    </div>
  );
};

export default TaskDetail;
