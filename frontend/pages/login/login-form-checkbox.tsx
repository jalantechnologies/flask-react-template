import React from 'react';

const LoginFormCheckbox: React.FC = () => (
  <div className="relative pt-0.5">
    <input type="checkbox" id="formCheckbox" className="taskCheckbox sr-only" />
    <div className="box mr-3 flex size-5 items-center justify-center rounded border border-stroke dark:border-form-strokedark dark:bg-form-input">
      <span className="opacity-0">
        <img
          alt="checkbox tick mark icon"
          className="size-3"
          src="/assets/img/icon/form-checkbox-checkmark.svg"
        />
      </span>
    </div>
  </div>
);

export default LoginFormCheckbox;
