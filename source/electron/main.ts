import electron, {type Tray as TrayType, type Menu as MenuType} from 'electron';
import {fetchUsageData, type UsageData} from '../utils/usage.js';

const {app, Tray, Menu, nativeImage} = electron;

let tray: TrayType | null = null;
let currentUsage: UsageData | null = null;

function getStatusColor(percentRemaining: number): 'green' | 'yellow' | 'red' {
  if (percentRemaining < 5) return 'red';
  if (percentRemaining <= 20) return 'yellow';
  return 'green';
}

function getBar(remaining: number, width = 15): string {
  const filled = Math.round((remaining / 100) * width);
  return '█'.repeat(filled) + '░'.repeat(width - filled);
}

function buildMenu(): MenuType {
  if (!currentUsage) {
    return Menu.buildFromTemplate([
      {label: '⚡ Claude Battery', enabled: false},
      {type: 'separator'},
      {label: 'Loading...', enabled: false},
      {type: 'separator'},
      {label: 'Refresh', click: refreshUsage},
      {label: 'Quit', click: () => app.quit()},
    ]);
  }

  const sessionRemaining = 100 - currentUsage.session.percentUsed;
  const weeklyRemaining = 100 - currentUsage.weekly.percentUsed;

  const items: Electron.MenuItemConstructorOptions[] = [
    {label: '⚡ Claude Battery', enabled: false},
    {type: 'separator'},
    {
      label: `Session: ${getBar(sessionRemaining)} ${sessionRemaining}%`,
      enabled: false,
    },
    {
      label: `   Resets ${currentUsage.session.resetInfo}`,
      enabled: false,
    },
    {type: 'separator'},
    {
      label: `Weekly:  ${getBar(weeklyRemaining)} ${weeklyRemaining}%`,
      enabled: false,
    },
    {
      label: `   Resets ${currentUsage.weekly.resetInfo}`,
      enabled: false,
    },
  ];

  if (currentUsage.weeklySonnet) {
    const sonnetRemaining = 100 - currentUsage.weeklySonnet.percentUsed;
    items.push(
      {type: 'separator'},
      {
        label: `Sonnet:  ${getBar(sonnetRemaining)} ${sonnetRemaining}%`,
        enabled: false,
      },
      {
        label: `   Resets ${currentUsage.weeklySonnet.resetInfo}`,
        enabled: false,
      },
    );
  }

  items.push(
    {type: 'separator'},
    {label: 'Refresh', click: refreshUsage},
    {label: 'Quit', click: () => app.quit()},
  );

  return Menu.buildFromTemplate(items);
}

async function refreshUsage(): Promise<void> {
  try {
    currentUsage = await fetchUsageData();
    updateTray();
  } catch (error) {
    console.error('Failed to fetch usage:', error);
  }
}

function updateTray(): void {
  if (!tray) return;

  const lowestRemaining = currentUsage
    ? Math.min(
        100 - currentUsage.session.percentUsed,
        100 - currentUsage.weekly.percentUsed,
      )
    : 100;

  // Update title (shows next to icon on macOS)
  const color = getStatusColor(lowestRemaining);
  const emoji = color === 'red' ? '🪫' : '🔋';
  tray.setTitle(`${emoji} ${lowestRemaining}%`);

  // Update menu
  tray.setContextMenu(buildMenu());
}

function createTray(): void {
  // Create initial tray with placeholder
  const icon = nativeImage.createEmpty();
  tray = new Tray(icon);
  tray.setTitle('🔋 --');

  // Initial load
  refreshUsage();

  // Refresh every 5 minutes
  setInterval(refreshUsage, 5 * 60 * 1000);
}

app.whenReady().then(() => {
  // Hide dock icon (menu bar app only)
  app.dock?.hide();

  createTray();
});

app.on('window-all-closed', () => {
  // Keep running - we're a tray app
});
