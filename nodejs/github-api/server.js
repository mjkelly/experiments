// Sample use of the GitHub REST API v3.
// (And I am attempting to learn a little Node.)
const fs = require('fs');

const express = require('express');
const promclient = require('prom-client');
const request = require('request-promise-native');

const port = 8080;
const tokenFile = 'github-token';
const app = express();

let token = fs.readFileSync(tokenFile);
if (!token) {
  throw new Error('Could not read token from token file');
}
token = String(token).trim();
console.log('Read token: [' + token + ']');

const githubOpts = {
  headers: {
    'User-Agent': 'request-promise-native github-api.js',
    Authorization: 'token ' + token,
    Accept: 'application/vnd.github.v3+json'
  },
  json: true
};

// Handlers

app.get('/', (req, res) => {
  console.log('using token ' + token);
  res.set('Content-type', 'text/plain');
  request(Object.assign({uri: 'https://api.github.com'}, githubOpts))
    .then(resp => {
      res.send(`Got: ${JSON.stringify(resp)}`);
    }).catch(error => {
      res.send(`Error: ${error}`);
    });
});

app.get('/myrepos', (req, res) => {
  res.set('Content-type', 'text/plain');
  request(Object.assign({uri: 'https://api.github.com/user/repos'}, githubOpts))
    .then(resp => {
      for (const repo of resp) {
        res.write('Repo: ' + repo.full_name + '\n');
      }
      res.write('Done.\n');
      res.end();
    }).catch(error => {
      res.send(`Error: ${error}`);
    });
});

app.get('/vars', (req, res) => {
  res.set('Content-type', 'text/plain');
  res.send(promclient.register.metrics());
});

// End of handlers

promclient.collectDefaultMetrics({timeout: 5000});
console.log(`starting on ${port}...`);
app.listen(port);
