# 敏感信息检测模式库

## IPv4 地址

### 检测正则
```regex
\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b
```

### 示例
| 原始 | 脱敏后 |
|------|--------|
| `192.168.1.1` | `x.x.x.x` |
| `10.0.0.1` | `x.x.x.x` |
| `115.191.60.79` | `x.x.x.x` |

---

## IPv6 地址

### 检测正则
```regex
(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}
```

### 示例
| 原始 | 脱敏后 |
|------|--------|
| `2001:0db8:85a3::8a2e` | `[IPv6地址]` |
| `fe80::1` | `[IPv6地址]` |

---

## API 密钥

### OpenAI API Key
```regex
sk-[a-zA-Z0-9]{48}
```
脱敏: `sk-...[密钥]`

### 阿里云 Access Key
```regex
AKLT[a-zA-Z0-9]{16,}
```
脱敏: `AKLT...[密钥]`

### 通用 API Key (32位)
```regex
\b[a-f0-9]{32}\b
```
脱敏: `...[API密钥]`

### 微信 AppID
```regex
wx[a-f0-9]{16}
```
脱敏: `wx...[AppID]`

---

## Access Token

### JWT Token
```regex
eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*
```
脱敏: `[JWT Token]`

### 飞书 User Access Token
```regex
u-[a-zA-Z0-9]{16,}
```
脱敏: `[Access Token]`

### 飞书 Tenant Access Token
```regex
t-[a-zA-Z0-9]{16,}
```
脱敏: `[Tenant Token]`

---

## 服务器路径

### Linux 敏感路径
```regex
/(root|home/[^/]+|etc|var/log)/[\w/.-]+
```
脱敏: `/path/to/...`

### Windows 敏感路径
```regex
[A-Za-z]:\\(?:Users|Windows|Program Files|ProgramData)\\[^\n]*
```
脱敏: `C:\path\to\...`

### 示例
| 原始 | 脱敏后 |
|------|--------|
| `/root/.openclaw/config.json` | `/path/to/config.json` |
| `/home/admin/.ssh/id_rsa` | `/path/to/id_rsa` |
| `C:\Users\nekulo\Documents\secret.txt` | `C:\path\to\secret.txt` |

---

## 数据库连接字符串

### 检测正则
```regex
(mysql|postgresql|mongodb|redis)://[^\s\"']+
```
脱敏: `[数据库连接字符串]`

---

## 密码

### 显式密码字段
```regex
(password|passwd|pwd)\s*[=:]\s*["']?[^\s"'\n]+["']?
```
脱敏: `password: [已隐藏]`

---

## 脱敏执行规则

1. **扫描优先级**: Token > API Key > IP > 路径 > 密码
2. **脱敏深度**: 完全替换，不留原始特征
3. **日志处理**: 写入日志前先脱敏
4. **文档输出**: 生成文档前扫描并脱敏
5. **用户确认**: 如涉及敏感信息，提示用户确认是否继续
