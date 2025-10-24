import { useState } from 'react';

type UseTimerProps = {
  delayInMilliseconds: number;
};

type UseTimerType = {
  isResendEnabled: boolean;
  remaininingSecondsStr: string;
  startTimer: () => void;
  stopTimer: () => void;
};

const useTimer = ({ delayInMilliseconds }: UseTimerProps): UseTimerType => {
  const millisecondsInSecond = 1_000;
  const [remainingTime, setRemainingTime] = useState(delayInMilliseconds);
  const [timerEnd, setTimerEnd] = useState(true);
  let timeoutId: NodeJS.Timeout;
  let intervalId: NodeJS.Timeout;
  let started: boolean = false;

  const onTick = () => {
    setRemainingTime((oldTime) => oldTime - millisecondsInSecond);
  };

  const onEnd = () => {
    setTimerEnd(true);
  };

  const stopTimer = () => {
    started = false;
    clearInterval(intervalId);
    clearTimeout(timeoutId);
  };

  const startTimer = () => {
    if (!started) {
      setTimerEnd(false);
      started = true;

      timeoutId = setTimeout(() => {
        started = false;
        onEnd();
        stopTimer();
      }, delayInMilliseconds);

      intervalId = setInterval(onTick, millisecondsInSecond);
      setRemainingTime(delayInMilliseconds);
    }
  };

  const isResendEnabled =
    timerEnd || (remainingTime <= millisecondsInSecond && !started);

  const remaininingSeconds = remainingTime / millisecondsInSecond - 1;
  const remaininingSecondsStr =
    remaininingSeconds > 9 ? `${remaininingSeconds}` : `0${remaininingSeconds}`;

  return {
    isResendEnabled,
    remaininingSecondsStr,
    startTimer,
    stopTimer,
  };
};

export default useTimer;
