export {};

declare global {
  const Config: {
    env: string;
    inspectletKey: string;
  };

  interface Window {
    __insp: Array<Array<string | number>>;
    __inspld: number;
    Config;
  }
}
