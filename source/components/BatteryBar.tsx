import {Box, Text} from 'ink';

type Props = {
  label: string;
  percentUsed: number;
  resetInfo?: string;
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

export default function BatteryBar({
  label,
  percentUsed,
  resetInfo,
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
      {resetInfo && (
        <Box marginLeft={11}>
          <Text dimColor>Resets {resetInfo}</Text>
        </Box>
      )}
    </Box>
  );
}
