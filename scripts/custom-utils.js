const { exec } = require('child_process');

function executionPromise(command) {
  return new Promise((resolve, reject) => {
    const executor = exec(command, (err, stdout, stderr) => {
      if (stdout) resolve(stdout);
    });

    executor.stdout.on('data', console.log);
    executor.stderr.on('data', console.log);
    executor.stderr.on('exit', code => console.log('EXIT', code));
  });
}

function getArguments() {
  return process.argv.slice(2).join(' ');
}

function applyTerminalArguments(command) {
  const args = getArguments();
  return args ? `${ command } ${ args }` : command;
}

module.exports = {
  executionPromise,
  applyTerminalArguments,
  getArguments
};
