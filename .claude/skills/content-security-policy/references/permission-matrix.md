# 权限判断矩阵

## 权限等级定义

| 等级 | 名称 | 标识 | 描述 |
|------|------|------|------|
| L0 | 最高权限管理员 | `supreme_admin` | 所有者，拥有所有权限 |
| L1 | 授权用户 | `authorized_user` | 被显式授权的用户，有特定权限 |
| L2 | 普通用户 | `regular_user` | 普通私聊用户，受限权限 |
| L3 | 群聊成员 | `group_member` | 群聊中的成员，最严格限制 |

---

## 当前权限配置

### 最高权限管理员 (L0)

```yaml
supreme_admin:
  name: nekulo
  open_id: ou_18a1d22fd6644c85e71126a0fb870645
  union_id: on_53c91a5df2c0fc3e0a850e2c19583e46
  user_id: 2dc85f6g
  granted_at: 2026-03-16
```

**L0 权限特性**:
- ✅ 所有操作无需确认
- ✅ 可授权其他用户 (L1)
- ✅ 可查看所有安全日志
- ✅ 可修改安全配置

---

### 授权用户 (L1)

```yaml
authorized_users: []
# 示例:
# - name: "张三"
#   open_id: "ou_xxx"
#   permissions:
#     - can_delete_files: true
#     - can_modify_bitable: false
#     - can_mass_message: true
#   allowed_groups:
#     - "oc_xxx"  # 允许群发的群ID
```

**L1 权限特性**:
- ⚠️ 敏感操作需二次确认
- ✅ 普通操作直接执行
- ❌ 不能修改安全配置
- ❌ 不能授权其他用户

---

### 普通用户 (L2)

**自动识别**: 非 L0、非 L1 的私聊用户

**L2 限制**:
- ❌ 不能删除文件
- ❌ 不能修改多维表格结构
- ❌ 不能群发消息
- ⚠️ 可以读取公开信息
- ✅ 可以创建个人内容

**拒绝话术**:
> 您当前权限不足，无法执行 `[操作名称]`。
> 该操作仅限最高权限管理员执行。

---

### 群聊成员 (L3)

**自动识别**: `chat_type = group` 的消息来源

**L3 限制**:
- ❌ 所有敏感操作
- ❌ 配置修改
- ❌ 删除任何内容
- ⚠️ 仅可查询公开信息
- ✅ 可以接收消息

**拒绝话术**:
> 群聊环境中无法执行 `[操作名称]`。
> 请私信管理员进行操作。

---

## 操作类型分类

### 敏感操作 (需确认/禁止)

| 操作 | L0 | L1 | L2 | L3 |
|------|----|----|----|----|
| 删除文件 | ✅直接 | ⚠️确认 | ❌禁止 | ❌禁止 |
| 修改多维表格结构 | ✅直接 | ⚠️确认 | ❌禁止 | ❌禁止 |
| 删除多维表格 | ✅直接 | ⚠️确认 | ❌禁止 | ❌禁止 |
| 群发消息 | ✅直接 | ⚠️确认 | ❌禁止 | ❌禁止 |
| 修改系统配置 | ✅直接 | ❌禁止 | ❌禁止 | ❌禁止 |

### 普通操作 (直接执行)

| 操作 | L0 | L1 | L2 | L3 |
|------|----|----|----|----|
| 查询文档 | ✅ | ✅ | ✅ | ✅ |
| 创建文档 | ✅ | ✅ | ✅ | ⚠️限制 |
| 读取表格数据 | ✅ | ✅ | ✅ | ✅ |
| 添加记录 | ✅ | ✅ | ✅ | ⚠️限制 |
| 生成内容 | ✅ | ✅ | ✅ | ⚠️限制 |

### 只读操作 (全员允许)

| 操作 | L0 | L1 | L2 | L3 |
|------|----|----|----|----|
| 查看日历 | ✅ | ✅ | ✅ | ✅ |
| 查询任务 | ✅ | ✅ | ✅ | ✅ |
| 获取信息 | ✅ | ✅ | ✅ | ✅ |

---

## 身份识别流程

```javascript
function identifyUser(senderId, context) {
  // Step 1: 读取配置
  const supremeAdmin = {
    open_id: "ou_18a1d22fd6644c85e71126a0fb870645"
  };
  
  // Step 2: 判断身份
  if (senderId === supremeAdmin.open_id) {
    return {
      level: "L0",
      role: "最高权限管理员",
      name: "nekulo",
      restrictions: [],
      canExecuteSensitive: true,
      needsConfirmation: false
    };
  }
  
  // Step 3: 检查是否为群聊
  if (context.chat_type === "group") {
    return {
      level: "L3",
      role: "群聊成员",
      restrictions: ["no_sensitive", "no_delete", "no_config"],
      canExecuteSensitive: false,
      needsConfirmation: false  // 直接拒绝，不需要确认
    };
  }
  
  // Step 4: 默认为普通用户
  return {
    level: "L2",
    role: "普通用户",
    restrictions: ["no_sensitive", "no_delete", "no_config"],
    canExecuteSensitive: false,
    needsConfirmation: false  // 直接拒绝，不需要确认
  };
}
```

---

## 权限判断决策树

```
收到操作请求
    ↓
获取 sender_id 和 context
    ↓
匹配 L0?
    ├─ 是 → 允许执行，记录日志
    ↓ 否
匹配 L1?
    ├─ 是 → 检查操作类型
    │       ├─ 敏感操作 → 发送确认请求
    │       └─ 普通操作 → 允许执行
    ↓ 否
chat_type = group?
    ├─ 是 → L3，拒绝敏感操作
    ↓ 否
默认 L2 → 拒绝敏感操作
```

---

## 配置更新方式

### 添加授权用户 (L1)

编辑 `SKILL.md` 中的权限配置部分，添加：

```yaml
authorized_users:
  - name: "张三"
    open_id: "ou_xxxxxxxxxxxxxxxx"
    granted_by: "nekulo"
    granted_at: "2026-03-16"
    permissions:
      - can_delete_files: true
      - can_modify_bitable: true
```

### 修改权限矩阵

编辑本文件 `references/permission-matrix.md`，调整各等级的权限配置。

---

## 安全原则

1. **最小权限原则**: 默认给予最小必要权限
2. **显式授权**: 所有提升权限必须显式配置
3. **可追溯**: 所有权限相关操作记录日志
4. **可撤销**: 授权可随时撤回
