#!/usr/bin/env node
/**
 * Timer script for Clawdbot
 *
 * Usage: node timer.js [duration] [label]
 *
 * Duration formats:
 *   30s  - 30 seconds
 *   5m   - 5 minutes
 *   1h   - 1 hour
 *   5    - 5 minutes (default unit)
 *   5:30 - 5 minutes 30 seconds
 *   1:30:00 - 1 hour 30 minutes
 */

const { spawn, execSync } = require('child_process');
const { writeFileSync, unlinkSync } = require('fs');
const { join } = require('path');
const { tmpdir } = require('os');

// Parse duration string to milliseconds
function parseDuration(input) {
  if (!input) {
    throw new Error('Duration is required');
  }

  const str = input.trim().toLowerCase();

  // HH:MM:SS or MM:SS format
  if (str.includes(':')) {
    const parts = str.split(':').map(p => parseInt(p, 10));
    if (parts.some(isNaN)) {
      throw new Error(`Invalid time format: ${input}`);
    }

    if (parts.length === 2) {
      // MM:SS
      const [minutes, seconds] = parts;
      return (minutes * 60 + seconds) * 1000;
    } else if (parts.length === 3) {
      // HH:MM:SS
      const [hours, minutes, seconds] = parts;
      return (hours * 3600 + minutes * 60 + seconds) * 1000;
    }
    throw new Error(`Invalid time format: ${input}`);
  }

  // Ns, Nm, Nh format
  const match = str.match(/^(\d+(?:\.\d+)?)\s*(s|sec|seconds?|m|min|minutes?|h|hr|hours?)?$/i);
  if (!match) {
    throw new Error(`Invalid duration format: ${input}`);
  }

  const value = parseFloat(match[1]);
  const unit = (match[2] || 'm').toLowerCase();

  let multiplier;
  if (unit.startsWith('s')) {
    multiplier = 1000;
  } else if (unit.startsWith('m')) {
    multiplier = 60 * 1000;
  } else if (unit.startsWith('h')) {
    multiplier = 60 * 60 * 1000;
  } else {
    multiplier = 60 * 1000; // default to minutes
  }

  return Math.round(value * multiplier);
}

// Format milliseconds to human-readable string
function formatDuration(ms) {
  const totalSeconds = Math.round(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const parts = [];
  if (hours > 0) parts.push(`${hours}h`);
  if (minutes > 0) parts.push(`${minutes}m`);
  if (seconds > 0 || parts.length === 0) parts.push(`${seconds}s`);

  return parts.join(' ');
}

// Format remaining time for display
function formatRemaining(ms) {
  const totalSeconds = Math.ceil(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

// Show system notification (cross-platform)
function showSystemNotification(title, message) {
  const platform = process.platform;

  try {
    if (platform === 'win32') {
      // Windows: Use BurntToast module (native Toast notifications)
      const psScript = `
        Import-Module BurntToast
        New-BurntToastNotification -Text '${title}', '${message}'
        Start-Sleep -Milliseconds 500
      `;
      const tempPs1 = join(tmpdir(), `jarvis-timer-${Date.now()}.ps1`);
      const utf8Bom = Buffer.from([0xEF, 0xBB, 0xBF]);
      const content = Buffer.concat([utf8Bom, Buffer.from(psScript, 'utf8')]);
      writeFileSync(tempPs1, content);

      // 使用execSync在当前session中执行，确保通知能显示
      try {
        execSync(`powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "${tempPs1}"`, {
          stdio: 'ignore',
          timeout: 5000
        });
      } catch (e) {
        // 忽略超时或错误，不影响计时器继续
      }
    } else if (platform === 'darwin') {
      spawn('osascript', ['-e', `display notification "${message}" with title "${title}"`], {
        stdio: 'ignore',
        detached: true
      }).unref();
    } else {
      spawn('notify-send', [title, message], {
        stdio: 'ignore',
        detached: true
      }).unref();
    }
  } catch (e) {
    // Notification not available, continue silently
  }
}

// Play sound notification (cross-platform)
function playNotificationSound(options = {}) {
  const { silent = false } = options;
  if (silent) return;

  const platform = process.platform;

  try {
    let soundCommand;

    if (platform === 'win32') {
      // Windows: Use PowerShell to play system notification sound
      soundCommand = spawn('powershell', ['-c', '(New-Object Media.SoundPlayer "C:\\Windows\\Media\\notify.wav").PlaySync()'], {
        stdio: 'ignore',
        detached: true
      });
    } else if (platform === 'darwin') {
      // macOS: Use afplay
      soundCommand = spawn('afplay', ['/System/Library/Sounds/Glass.aiff'], {
        stdio: 'ignore',
        detached: true
      });
    } else {
      // Linux: Try paplay (PulseAudio) or aplay (ALSA)
      soundCommand = spawn('paplay', ['/usr/share/sounds/freedesktop/stereo/complete.oga'], {
        stdio: 'ignore',
        detached: true
      });
    }

    soundCommand.unref();
  } catch (e) {
    // Sound not available, continue silently
  }
}

// Main timer function
async function runTimer(durationMs, label, options = {}) {
  const startTime = Date.now();
  const endTime = startTime + durationMs;

  console.log(`⏱️ Timer started: ${formatDuration(durationMs)}`);
  if (label) {
    console.log(`📝 Label: ${label}`);
  }
  console.log(`⏰ Will complete at: ${new Date(endTime).toLocaleTimeString()}`);
  if (options.silent) {
    console.log(`🔇 Silent mode (no sound)`);
  }
  console.log('');

  // Progress update interval (every 10 seconds for timers > 1 minute, else every second)
  const updateInterval = durationMs > 60000 ? 10000 : 1000;
  let lastUpdate = startTime;

  return new Promise((resolve) => {
    const checkTimer = () => {
      const now = Date.now();
      const remaining = endTime - now;

      if (remaining <= 0) {
        // Timer complete!
        console.log('');
        console.log('═'.repeat(50));
        if (label) {
          console.log(`⏰ Timer complete! ${label}`);
        } else {
          console.log(`⏰ Timer complete!`);
        }
        console.log('═'.repeat(50));

        // Show system notification
        showSystemNotification('⏰ Timer Complete!', label || 'Your timer has finished.');

        // Play sound (unless silent)
        playNotificationSound(options);

        resolve();
        return;
      }

      // Show progress update
      if (now - lastUpdate >= updateInterval) {
        console.log(`⏳ Remaining: ${formatRemaining(remaining)}`);
        lastUpdate = now;
      }

      // Check again in 100ms for accuracy
      setTimeout(checkTimer, 100);
    };

    checkTimer();
  });
}

// Main execution
async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Timer - Set a countdown timer with notification

Usage: node timer.js [duration] [options] [label]

Duration formats:
  30s       30 seconds
  5m        5 minutes
  1h        1 hour
  5         5 minutes (default unit)
  5:30      5 minutes 30 seconds
  1:30:00   1 hour 30 minutes

Options:
  --silent, -s    Disable sound notification

Examples:
  node timer.js 5m                          # 5 minute timer
  node timer.js 30s "Check email"           # 30 second timer with label
  node timer.js 1h "Meeting time"           # 1 hour timer with label
  node timer.js 2:30                        # 2 minutes 30 seconds
  node timer.js 5m -s "Quiet timer"         # Silent timer (no sound)
`);
    process.exit(0);
  }

  try {
    // Parse options
    const silentIndex = args.findIndex(arg => arg === '--silent' || arg === '-s');
    const silent = silentIndex !== -1;
    if (silent) {
      args.splice(silentIndex, 1);
    }

    const durationMs = parseDuration(args[0]);
    const label = args.slice(1).join(' ') || null;

    if (durationMs <= 0) {
      throw new Error('Duration must be positive');
    }

    if (durationMs > 24 * 60 * 60 * 1000) {
      throw new Error('Duration cannot exceed 24 hours');
    }

    await runTimer(durationMs, label, { silent });
    process.exit(0);
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    process.exit(1);
  }
}

main();
