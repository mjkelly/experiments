const express = require('express');
const promclient = require('prom-client');

const port = 8080;
const app = express();
const serverName = process.env.SERVER_NAME || 'UNKNOWN';

const counter = new promclient.Counter({
  name: 'hit_counter',
  help: 'Count of hits per endpoint',
  labelNames: ['path']
});

app.get('/', (req, res) => {
  counter.inc({path: '/'});
  res.send(`Hello, I am ${serverName}`);
});

app.get('/health', (req, res) => {
  counter.inc({path: '/health'});
  res.set('Content-type', 'text/plain');
  res.send('ok\n');
});

app.get('/vars', (req, res) => {
  counter.inc({path: '/vars'});
  res.set('Content-type', 'text/plain');
  res.send(promclient.register.metrics());
});

promclient.collectDefaultMetrics({timeout: 5000});
console.log(`starting on ${port}...`);
app.listen(port);
