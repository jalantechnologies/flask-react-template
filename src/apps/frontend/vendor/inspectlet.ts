const InspectLet = (): void => {
  window.__insp = window.__insp || [];
  window.__insp.push(['wid', window.Config.inspectletKey as string]);
  const ldinsp = (): void => {
    if (typeof window.__inspld !== 'undefined') return;
    window.__inspld = 1;
    const insp = document.createElement('script');
    insp.type = 'text/javascript';
    insp.async = true;
    insp.id = 'inspsync';
    insp.src = `${document.location.protocol === 'https:' ? 'https' : 'http'}://cdn.inspectlet.com/inspectlet.js?wid=${String(window.Config.inspectletKey)}&r=${Math.floor(new Date().getTime() / 3600000)}`;
    const x = document.getElementsByTagName('script')[0];
    if (x === undefined) {
      document.getElementsByTagName('head')[0].appendChild(insp);
    } else {
      x.parentNode!.insertBefore(insp, x);
    }
  };
  setTimeout(ldinsp, 0);
};

export default InspectLet;
