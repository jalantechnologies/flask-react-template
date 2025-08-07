import React from 'react';

interface Task {
  id: string;
  title: string;
  description: string;
  account_id: string;
}

interface TaskListProps {
  tasks: Task[];
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onEdit, onDelete }) => {
  if (tasks.length === 0) {
    return (
      <div className="rounded-sm border border-stroke bg-white px-5 py-6 shadow-default dark:border-strokedark dark:bg-boxdark">
        <div className="text-center text-gray-500">
          <p>No tasks found. Create your first task!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark">
      <div className="px-4 py-6 md:px-6 xl:px-7.5">
        <h4 className="text-xl font-semibold text-black dark:text-white">
          Tasks
        </h4>
      </div>

      <div className="grid grid-cols-6 border-t border-stroke px-4 py-4.5 dark:border-strokedark sm:grid-cols-8 md:px-6 2xl:px-7.5">
        <div className="col-span-3 flex items-center">
          <p className="font-medium">Title</p>
        </div>
        <div className="col-span-3 hidden items-center sm:flex">
          <p className="font-medium">Description</p>
        </div>
        <div className="col-span-2 flex items-center">
          <p className="font-medium">Actions</p>
        </div>
      </div>

      {tasks.map((task, index) => (
        <div
          className="grid grid-cols-6 border-t border-stroke px-4 py-4.5 dark:border-strokedark sm:grid-cols-8 md:px-6 2xl:px-7.5"
          key={task.id}
        >
          <div className="col-span-3 flex items-center">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-center">
              <p className="text-sm text-black dark:text-white">
                {task.title}
              </p>
            </div>
          </div>
          <div className="col-span-3 hidden items-center sm:flex">
            <p className="text-sm text-black dark:text-white">
              {task.description.length > 50 
                ? `${task.description.substring(0, 50)}...` 
                : task.description}
            </p>
          </div>
          <div className="col-span-2 flex items-center gap-2">
            <button
              className="inline-flex items-center justify-center rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-white hover:bg-primary/90"
              onClick={() => onEdit(task)}
            >
              Edit
            </button>
            <button
              className="inline-flex items-center justify-center rounded-md bg-red-500 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-600"
              onClick={() => onDelete(task.id)}
            >
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TaskList;
