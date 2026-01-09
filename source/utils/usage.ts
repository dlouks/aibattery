import {readFileSync} from 'fs';
import {join, dirname} from 'path';
import {fileURLToPath} from 'url';

export type UsageMetric = {
  percentUsed: number;
  resetAt?: string; // ISO timestamp
};

export type UsageData = {
  session: UsageMetric;
  weekly: UsageMetric;
  weeklySonnet?: UsageMetric;
};

type UsageDataFile = {
  lastUpdated: string;
  claude: {
    session: UsageMetric;
    weekly: UsageMetric;
    weeklySonnet?: UsageMetric;
  };
};

// Get the directory where this script is located
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to the usage data file (in project root)
const USAGE_DATA_PATH = join(__dirname, '..', '..', 'usage-data.json');

export async function fetchUsageData(): Promise<UsageData> {
  try {
    const data = readFileSync(USAGE_DATA_PATH, 'utf-8');
    const parsed: UsageDataFile = JSON.parse(data);
    return parsed.claude;
  } catch {
    // Fallback to mock data if file doesn't exist
    const now = new Date();

    const sessionReset = new Date(now);
    sessionReset.setDate(sessionReset.getDate() + 1);
    sessionReset.setHours(1, 0, 0, 0);

    const weeklyReset = new Date(now);
    weeklyReset.setDate(weeklyReset.getDate() + 7);
    weeklyReset.setHours(6, 0, 0, 0);

    return {
      session: {percentUsed: 50, resetAt: sessionReset.toISOString()},
      weekly: {percentUsed: 50, resetAt: weeklyReset.toISOString()},
      weeklySonnet: {percentUsed: 0, resetAt: weeklyReset.toISOString()},
    };
  }
}
