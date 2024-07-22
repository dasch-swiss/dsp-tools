import exec from 'k6/x/exec';
import { Trend, Counter } from 'k6/metrics';
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

const commandDurationTrend = new Trend('exec_command_duration', true);
const commandsCounter = new Counter('exec_commands');

const testDataDir = `${__ENV.ROOT_DIR}/../testdata/excel2json/excel2json_files/`;
const testOutputDir = `${__ENV.RUN_DIR}/excel2json/`;

export const options = {
  // A string specifying the total duration of the test run.
  duration: '60s',
  // Exemplary threshold. The actual value we're aiming for will
  // depend on the environment used for the automated tests.
  thresholds: {
    exec_command_duration: ['p(95)<10000'], // 95% of executions should be below 10000ms
  },
}

export function setup() {
  console.log(`Remove output directory (${testOutputDir})`);
  exec.command('rm', ['-rf', testOutputDir]);

  console.log(`Recreate output directory (${testOutputDir})`);
  exec.command('mkdir', ['-p', testOutputDir]);
}

export default function () {
  const command = `dsp-tools excel2json --suppress-update-prompt "${testDataDir}" "${testOutputDir}/${uuidv4()}.json" 2>&1`;

  const start = Date.now();

  console.log(exec.command('bash', ['-c', command]));

  const elapsed = Date.now() - start;

  commandDurationTrend.add(elapsed);
  commandsCounter.add(1);
}
