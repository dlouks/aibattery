import {useState, useEffect} from 'react';
import {Box, Text, useApp, useInput} from 'ink';
import BatteryBar from './components/BatteryBar.js';
import {type UsageData, fetchUsageData} from './utils/usage.js';
import Spinner from 'ink-spinner';

export default function App() {
  const {exit} = useApp();
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useInput((input, key) => {
    if (input === 'q' || key.escape) {
      exit();
    }
    if (input === 'r') {
      setLoading(true);
      fetchUsageData()
        .then(setUsage)
        .catch(e => setError(e.message))
        .finally(() => setLoading(false));
    }
  });

  useEffect(() => {
    fetchUsageData()
      .then(setUsage)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

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
          ⚡ Claude Battery
        </Text>
      </Box>

      <BatteryBar
        label="Session"
        percentUsed={usage.session.percentUsed}
        resetInfo={usage.session.resetInfo}
      />

      <Box marginTop={1}>
        <BatteryBar
          label="Weekly"
          percentUsed={usage.weekly.percentUsed}
          resetInfo={usage.weekly.resetInfo}
        />
      </Box>

      {usage.weeklySonnet && (
        <Box marginTop={1}>
          <BatteryBar
            label="Sonnet"
            percentUsed={usage.weeklySonnet.percentUsed}
            resetInfo={usage.weeklySonnet.resetInfo}
          />
        </Box>
      )}

      <Box marginTop={1}>
        <Text dimColor>Press 'r' to refresh, 'q' to quit</Text>
      </Box>
    </Box>
  );
}
