import {useState, useEffect, useCallback} from 'react';
import {Box, Text, useApp, useInput} from 'ink';
import BatteryBar from './components/BatteryBar.js';
import {type UsageData, fetchUsageData} from './utils/usage.js';
import Spinner from 'ink-spinner';

const REFRESH_INTERVAL = 60_000; // 60 seconds

export default function App() {
  const {exit} = useApp();
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await fetchUsageData();
      setUsage(data);
      setError(null);
      setLastRefresh(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  useInput((input, key) => {
    if (input === 'q' || key.escape) {
      exit();
    }
    if (input === 'r') {
      setLoading(true);
      refresh();
    }
  });

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [refresh]);

  if (loading) {
    return (
      <Box>
        <Text color="cyan">
          <Spinner type="dots" />
        </Text>
        <Text> Loading usage data...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box flexDirection="column">
        <Text color="red">Error: {error}</Text>
        <Text dimColor>Press 'r' to retry, 'q' to quit</Text>
      </Box>
    );
  }

  if (!usage) {
    return (
      <Box>
        <Text color="yellow">No usage data available</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column" paddingX={1}>
      <Box marginBottom={1}>
        <Text bold color="cyan">
          ⚡ AI Battery
        </Text>
      </Box>

      <BatteryBar
        label="Session"
        percentUsed={usage.session.percentUsed}
        resetAt={usage.session.resetAt}
      />

      <Box marginTop={1}>
        <BatteryBar
          label="Weekly"
          percentUsed={usage.weekly.percentUsed}
          resetAt={usage.weekly.resetAt}
        />
      </Box>

      {usage.weeklySonnet && (
        <Box marginTop={1}>
          <BatteryBar
            label="Sonnet"
            percentUsed={usage.weeklySonnet.percentUsed}
            resetAt={usage.weeklySonnet.resetAt}
          />
        </Box>
      )}

      <Box marginTop={1}>
        <Text dimColor>
          {lastRefresh && `Updated ${lastRefresh.toLocaleTimeString()} · `}
          Auto-refresh 60s · 'r' refresh · 'q' quit
        </Text>
      </Box>
    </Box>
  );
}
