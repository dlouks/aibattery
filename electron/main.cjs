const {app, Tray, Menu, nativeImage} = require('electron');

let tray = null;
let currentUsage = null;

// Mock data - matches the CLI structure
async function fetchUsageData() {
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

function getStatusColor(percentRemaining) {
  if (percentRemaining < 5) return 'red';
  if (percentRemaining <= 20) return 'yellow';
  return 'green';
}

function getBar(remaining, width = 15) {
  const filled = Math.round((remaining / 100) * width);
  return '█'.repeat(filled) + '░'.repeat(width - filled);
}

function buildMenu() {
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

  const items = [
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

async function refreshUsage() {
  try {
    currentUsage = await fetchUsageData();
    updateTray();
  } catch (error) {
    console.error('Failed to fetch usage:', error);
  }
}

function updateTray() {
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

function createTray() {
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
  if (app.dock) {
    app.dock.hide();
  }

  createTray();
});

app.on('window-all-closed', () => {
  // Keep running - we're a tray app
});
