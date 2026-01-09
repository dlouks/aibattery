export type UsageMetric = {
  percentUsed: number;
  resetInfo?: string;
};

export type UsageData = {
  session: UsageMetric;
  weekly: UsageMetric;
  weeklySonnet?: UsageMetric;
};

// TODO: Replace with real usage data source
// Options:
// 1. Parse Claude CLI's local storage/config
// 2. Call Anthropic usage API (requires API key)
// 3. Read from a local config file that user updates

export async function fetchUsageData(): Promise<UsageData> {
  // Mock data for now - matches the screenshot structure
  // In production, this would fetch from Anthropic API or parse local Claude data

  return {
    session: {
      percentUsed: 15,
      resetInfo: '1am (America/Chicago)',
    },
    weekly: {
      percentUsed: 11,
      resetInfo: 'Jan 15, 6am (America/Chicago)',
    },
    weeklySonnet: {
      percentUsed: 0,
      resetInfo: 'Jan 15, 6am (America/Chicago)',
    },
  };
}
