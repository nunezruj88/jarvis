const clock = document.querySelector('#clock');
const time = new Intl.DateTimeFormat('es', { timeStyle: 'medium' });
function tick() {
  const now = new Date();
  clock.dateTime = now.toISOString();
  clock.textContent = time.format(now);
}
tick();
setInterval(tick, 1000);

const messages = document.querySelector('#messages');
const input = document.querySelector('#input');
const status = document.querySelector('#status');
const buttons = document.querySelectorAll('.hud-main button');
const storageKey = 'jarvis-local-conversation';
const session = localStorage.getItem(storageKey) || crypto.randomUUID();
localStorage.setItem(storageKey, session);

async function request(path, method = 'GET', body) {
  const response = await fetch(path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-Jarvis-Conversation': session,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) {
    throw new Error(typeof result.detail === 'string' ? result.detail : 'No se pudo completar la petición.');
  }
  return result;
}

function append(role, content) {
  const message = document.createElement('article');
  message.className = 'message ' + (role === 'user' ? 'user' : 'assistant');
  const speaker = document.createElement('span');
  speaker.className = 'speaker';
  speaker.textContent = role === 'user' ? 'Tú' : 'JARVIS';
  const text = document.createElement('p');
  text.textContent = content;
  message.append(speaker, text);
  messages.append(message);
  messages.scrollTop = messages.scrollHeight;
}

let busy = false;
async function run(task, pending = '') {
  if (busy) return;
  busy = true;
  buttons.forEach(button => { button.disabled = true; });
  status.textContent = pending;
  try {
    await task();
    status.textContent = '';
  } catch (error) {
    status.textContent = error.message;
  } finally {
    buttons.forEach(button => { button.disabled = false; });
    busy = false;
  }
}

async function send(text) {
  await run(async () => {
    const { reply } = await request('/api/chat', 'POST', { text });
    append('user', text);
    append('assistant', reply);
    if (input.value.trim() === text) input.value = '';
    input.focus();
  }, 'Procesando…');
}

document.querySelector('#chat').addEventListener('submit', event => {
  event.preventDefault();
  const text = input.value.trim();
  if (text) void send(text);
});
input.addEventListener('keydown', event => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    document.querySelector('#chat').requestSubmit();
  }
});
document.querySelectorAll('[data-prompt]').forEach(button => {
  button.addEventListener('click', () => void send(button.dataset.prompt));
});
document.querySelector('#clear').addEventListener('click', () => void run(async () => {
  await request('/api/history', 'DELETE');
  messages.replaceChildren();
  input.focus();
}));
void run(async () => {
  const { messages: saved } = await request('/api/history');
  saved.forEach(message => append(message.role, message.content));
}, 'Cargando historial…');
