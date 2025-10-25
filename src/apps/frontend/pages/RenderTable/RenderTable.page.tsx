import React from 'react';
import { useNavigate } from 'react-router-dom';
/* eslint-disable */
import { Button } from 'frontend/components';
import TaskService from 'frontend/services/task.service';
import { ApiResponse } from 'frontend/types';
import { Task } from 'frontend/types/tasks';

export default function NotFound(): React.ReactElement {
  const navigate = useNavigate();
  const [taskData, setTaskData] = React.useState<Task[]>([]);
  const tc = new TaskService();
  const [taskId, setTaskId] = React.useState<string>('');
  const [trigger, setTrigger] = React.useState<boolean>(false);

  React.useEffect(() => {
    const tc = new TaskService();
    const fetchTasks = async () => {
      try {
        const response: ApiResponse<Task[]> = await tc.getTasks();
        setTaskData(response.data || []);
      } catch (err) {
        console.error('Error fetching tasks:', err);
      }
    };
    if (trigger == false) {
      fetchTasks();
      setTrigger(true);
    }
    console.log(taskData, 'all the tasks return by api');
  }, [trigger]);

  const updateFormField = (
    event: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const tid = event.target.value;
    console.log('TAjasjasasjajsasak ID', tid);
    setTaskId(tid);
  };

  return (
    <div data-testid="TaskTable">
      <Button
        onClick={() => {
          navigate('/form-values');
        }}
      >
        Create Task
      </Button>
      <form
        className="task-entry-form"
        onSubmit={async (e) => {
          e.preventDefault();
          await tc.deleteTasks(taskId);
          setTrigger(false);
        }}
      >
        <div className="input-section">
          <label htmlFor="title" className="field-label">
            Task ID *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={taskId}
            onChange={updateFormField}
            className="text-input"
            required
            minLength={3}
          />
        </div>
        <div className="button-section">
          <button
            type="submit"
            className="submit-button"
            // eslint-disable-next-line @typescript-eslint/no-misused-promises
            // onClick={() => {handleSubmit()}
          >
            Delete Id
          </button>
        </div>
      </form>

      <table style={{ gap: '10px' }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {taskData.map((task) => (
            <tr key={task.id}>
              <td>{task.id}</td>
              <td>{task.title}</td>
              <td>{task.description}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
