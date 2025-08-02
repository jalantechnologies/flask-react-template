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

declare module '*.module.css' {
  const classes: { [key: string]: string };
  export default classes;
}
