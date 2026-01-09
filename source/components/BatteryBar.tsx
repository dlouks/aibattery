import {Box, Text} from 'ink';

type Props = {
  label: string;
  percentUsed: number;
  resetAt?: string;
  width?: number;
};

function getBatteryColor(percentRemaining: number): string {
  if (percentRemaining < 5) return 'red';
  if (percentRemaining <= 20) return 'yellow';
  return 'green';
}

function getBatteryIcon(percentRemaining: number): string {
  if (percentRemaining < 5) return '🪫';
  if (percentRemaining <= 20) return '🔋';
  return '🔋';
}

function getRelativeTime(isoString: string | undefined): string | null {
  if (!isoString) return null;
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

export default function BatteryBar({
  label,
  percentUsed,
  resetAt,
  width = 30,
}: Props) {
  const percentRemaining = Math.max(0, Math.min(100, 100 - percentUsed));
  const filledWidth = Math.round((percentRemaining / 100) * width);
  const emptyWidth = width - filledWidth;

  const color = getBatteryColor(percentRemaining);
  const icon = getBatteryIcon(percentRemaining);

  const filledBar = '█'.repeat(filledWidth);
  const emptyBar = '░'.repeat(emptyWidth);

  return (
    <Box flexDirection="column">
      <Box>
        <Text bold>{label.padEnd(8)}</Text>
        <Text> </Text>
        <Text>{icon} </Text>
        <Text color={color}>{filledBar}</Text>
        <Text dimColor>{emptyBar}</Text>
        <Text> </Text>
        <Text color={color} bold>
          {percentRemaining.toFixed(0)}%
        </Text>
        <Text dimColor> remaining</Text>
      </Box>
      {resetAt && getRelativeTime(resetAt) && (
        <Box marginLeft={11}>
          <Text dimColor>Resets {getRelativeTime(resetAt)}</Text>
        </Box>
      )}
    </Box>
  );
}
