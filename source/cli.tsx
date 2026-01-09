#!/usr/bin/env node
import {render} from 'ink';
import meow from 'meow';
import App from './App.js';
import {fetchUsageData} from './utils/usage.js';

const cli = meow(
  `
  Usage
    $ aibattery [options]

  Options
    --simple, -s   Simple output (no interactive UI)
    --json, -j     JSON output
    --help, -h     Show help
    --version, -v  Show version

  Description
    Battery-style indicator for Claude API usage.
    Shows remaining capacity with color-coded alerts:
      Green  = >20% remaining
      Yellow = ≤20% remaining
      Red    = <5% remaining
`,
  {
    importMeta: import.meta,
    flags: {
      help: {type: 'boolean', shortFlag: 'h'},
      version: {type: 'boolean', shortFlag: 'v'},
      simple: {type: 'boolean', shortFlag: 's'},
      json: {type: 'boolean', shortFlag: 'j'},
    },
  },
);

function getRelativeTime(isoString: string | undefined): string {
  if (!isoString) return '';
  const resetDate = new Date(isoString);
  const now = new Date();
  const diffMs = resetDate.getTime() - now.getTime();

  if (diffMs <= 0) return 'now';

  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `in ${diffMins} minute${diffMins !== 1 ? 's' : ''}`;
  if (diffHours < 24) return `in ${diffHours} hour${diffHours !== 1 ? 's' : ''}`;
  return `in ${diffDays} day${diffDays !== 1 ? 's' : ''}`;
}

async function simpleOutput() {
  const usage = await fetchUsageData();

  const getBatteryChar = (remaining: number) => {
    if (remaining < 5) return '🪫';
    if (remaining <= 20) return '🔋';
    return '🔋';
  };

  const getBar = (remaining: number, width = 20) => {
    const filled = Math.round((remaining / 100) * width);
    return '█'.repeat(filled) + '░'.repeat(width - filled);
  };

  const sessionRemaining = 100 - usage.session.percentUsed;
  const weeklyRemaining = 100 - usage.weekly.percentUsed;

  console.log('\n⚡ Claude Battery\n');
  console.log(`Session  ${getBatteryChar(sessionRemaining)} ${getBar(sessionRemaining)} ${sessionRemaining}% remaining`);
  console.log(`         Resets ${getRelativeTime(usage.session.resetAt)}\n`);
  console.log(`Weekly   ${getBatteryChar(weeklyRemaining)} ${getBar(weeklyRemaining)} ${weeklyRemaining}% remaining`);
  console.log(`         Resets ${getRelativeTime(usage.weekly.resetAt)}\n`);

  if (usage.weeklySonnet) {
    const sonnetRemaining = 100 - usage.weeklySonnet.percentUsed;
    console.log(`Sonnet   ${getBatteryChar(sonnetRemaining)} ${getBar(sonnetRemaining)} ${sonnetRemaining}% remaining`);
    console.log(`         Resets ${getRelativeTime(usage.weeklySonnet.resetAt)}\n`);
  }
}

async function jsonOutput() {
  const usage = await fetchUsageData();
  console.log(JSON.stringify({
    session: { remaining: 100 - usage.session.percentUsed, ...usage.session },
    weekly: { remaining: 100 - usage.weekly.percentUsed, ...usage.weekly },
    weeklySonnet: usage.weeklySonnet
      ? { remaining: 100 - usage.weeklySonnet.percentUsed, ...usage.weeklySonnet }
      : null,
  }, null, 2));
}

const isTTY = process.stdin.isTTY && process.stdout.isTTY;

if (cli.flags.json) {
  jsonOutput();
} else if (cli.flags.simple || !isTTY) {
  // Use simple output if requested or if not in interactive terminal
  simpleOutput();
} else {
  const {waitUntilExit} = render(<App />);
  waitUntilExit();
}
