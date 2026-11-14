// Local Chrome DevTools helper for recording the supplied artwork and UI checks.
import {spawn} from 'node:child_process';
import {mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';

export async function browser(port = 9234) {
  const profile = resolve(`.test-tmp/chrome-home-${port}`);
  await mkdir(profile, {recursive: true});
  const process = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', [
    '--headless=new', '--no-first-run', '--no-default-browser-check',
    '--autoplay-policy=no-user-gesture-required', `--remote-debugging-port=${port}`,
    `--user-data-dir=${profile}`, 'about:blank',
  ], {windowsHide: true, stdio: 'ignore'});
  let tabs;
  for (let i = 0; i < 80; i++) {
    try { tabs = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; }
    catch { await new Promise(r => setTimeout(r, 150)); }
  }
  if (!tabs) throw new Error('Chrome did not start');
  const ws = new WebSocket(tabs.find(t => t.type === 'page').webSocketDebuggerUrl);
  const keepAlive = setInterval(() => {}, 1000);
  await new Promise(r => ws.addEventListener('open', r, {once: true}));
  let id = 0;
  const pending = new Map();
  ws.addEventListener('message', e => {
    const msg = JSON.parse(e.data);
    if (msg.method === 'Runtime.exceptionThrown') console.error(JSON.stringify(msg.params));
    if (msg.id && pending.has(msg.id)) {
      const {resolve, reject} = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
    }
  });
  const call = (method, params = {}) => new Promise((resolve, reject) => {
    pending.set(++id, {resolve, reject}); ws.send(JSON.stringify({id, method, params}));
  });
  const evaluate = async expression => {
    const result = await call('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
    if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
  };
  await call('Runtime.enable');
  return {call, evaluate, close: async () => {
    await call('Browser.close').catch(() => {}); ws.close(); process.kill(); clearInterval(keepAlive);
  }};
}
