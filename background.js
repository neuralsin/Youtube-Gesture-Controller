let ws;

function connectWS() {
  ws = new WebSocket("ws://localhost:8765");
  
  ws.onopen = () => {
    console.log("[WS] Connected");
  };

  ws.onmessage = async (event) => {
    const command = event.data;
    console.log("[WS] Received:", command);

    const tab = (await chrome.tabs.query({ active: true, currentWindow: true }))[0];
    if (tab) {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: performGestureAction,
        args: [command]
      });
    }
  };

  ws.onclose = () => {
    console.log("[WS] Disconnected. Reconnecting in 2s...");
    setTimeout(connectWS, 2000);
  };
}

function performGestureAction(command) {
  const actions = {
    play: () => document.querySelector('video')?.play(),
    pause: () => document.querySelector('video')?.pause(),
    vol_up: () => { const v = document.querySelector('video'); if (v) v.volume = Math.min(v.volume + 0.1, 1); },
    vol_down: () => { const v = document.querySelector('video'); if (v) v.volume = Math.max(v.volume - 0.1, 0); },
    next_video: () => document.querySelector('.ytp-next-button')?.click(),
    prev_video: () => history.back()
  };

  if (actions[command]) actions[command]();
  else console.warn("[Gesture] Unknown command:", command);
}

connectWS();
