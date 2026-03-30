/**
 * 安全事件日志记录器
 * 
 * 用法: node security-logger.js <event_type> <user_id> <operation> <target> <decision> [reason]
 * 
 * 示例:
 * node security-logger.js sensitive_operation ou_xxx feishu_drive_file.delete file_xxx confirmed "L0 user"
 */

const fs = require('fs');
const path = require('path');

// 日志目录
const LOG_DIR = path.join(process.env.USERPROFILE || process.env.HOME, '.openclaw', 'security-logs');

// 确保日志目录存在
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

/**
 * 记录安全事件
 */
function logSecurityEvent(eventData) {
  const timestamp = new Date().toISOString();
  const date = timestamp.split('T')[0];
  const logFile = path.join(LOG_DIR, `security-events-${date}.log`);
  
  const logEntry = {
    timestamp,
    ...eventData
  };
  
  const logLine = JSON.stringify(logEntry) + '\n';
  
  fs.appendFileSync(logFile, logLine, 'utf8');
  console.log(`[Security Log] Event recorded: ${eventData.event_type}`);
}

/**
 * 从命令行参数记录
 */
function logFromArgs() {
  const args = process.argv.slice(2);
  
  if (args.length < 5) {
    console.error('Usage: node security-logger.js <event_type> <user_id> <operation> <target> <decision> [reason]');
    process.exit(1);
  }
  
  const [eventType, userId, operation, target, decision, ...reasonParts] = args;
  const reason = reasonParts.join(' ') || '';
  
  // 识别用户等级
  const supremeAdminId = 'ou_18a1d22fd6644c85e71126a0fb870645';
  const userLevel = userId === supremeAdminId ? 'L0' : 'L2';
  
  logSecurityEvent({
    event_type: eventType,
    user_id: userId,
    user_level: userLevel,
    operation,
    target,
    decision,
    reason
  });
}

/**
 * 获取今日日志摘要
 */
function getTodaySummary() {
  const date = new Date().toISOString().split('T')[0];
  const logFile = path.join(LOG_DIR, `security-events-${date}.log`);
  
  if (!fs.existsSync(logFile)) {
    console.log('No security events today.');
    return;
  }
  
  const logs = fs.readFileSync(logFile, 'utf8')
    .split('\n')
    .filter(line => line.trim())
    .map(line => JSON.parse(line));
  
  console.log(`\n=== Security Events Summary for ${date} ===\n`);
  console.log(`Total events: ${logs.length}`);
  
  const eventTypes = {};
  const decisions = {};
  
  logs.forEach(log => {
    eventTypes[log.event_type] = (eventTypes[log.event_type] || 0) + 1;
    decisions[log.decision] = (decisions[log.decision] || 0) + 1;
  });
  
  console.log('\nBy Event Type:');
  Object.entries(eventTypes).forEach(([type, count]) => {
    console.log(`  ${type}: ${count}`);
  });
  
  console.log('\nBy Decision:');
  Object.entries(decisions).forEach(([decision, count]) => {
    console.log(`  ${decision}: ${count}`);
  });
}

// 主逻辑
const command = process.argv[2];

if (command === '--summary' || command === '-s') {
  getTodaySummary();
} else if (command === '--help' || command === '-h') {
  console.log(`
Security Logger - 安全事件日志记录器

Usage:
  node security-logger.js <event_type> <user_id> <operation> <target> <decision> [reason]
  node security-logger.js --summary
  node security-logger.js --help

Parameters:
  event_type: sensitive_operation | permission_denied | data_desensitized | danger_blocked
  user_id:    用户 OpenID (ou_xxx)
  operation:  操作工具和方法
  target:     操作目标
  decision:   allowed | denied | confirmed | blocked
  reason:     决策原因 (可选)

Examples:
  node security-logger.js sensitive_operation ou_xxx feishu_drive_file.delete file_xxx confirmed "L0 user"
  node security-logger.js danger_blocked ou_xxx exec "rm -rf /" blocked "P0 command"
  
Options:
  --summary, -s   显示今日日志摘要
  --help, -h      显示帮助信息

Log Location:
  ~/.openclaw/security-logs/security-events-YYYY-MM-DD.log
`);
} else {
  logFromArgs();
}
