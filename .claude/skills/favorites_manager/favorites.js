/**
 * Favorites Manager - 链接收藏夹管理器
 * 
 * 使用方式：
 * const fm = require('./favorites.js');
 * await fm.addLink({ title: "...", url: "..." });
 */

const fs = require('fs');
const path = require('path');

const BASE_DIR = 'jarvis-memory/html-tools/链接保存';

/**
 * 找到最新的收藏夹 JSON 文件
 */
function findLatestFile() {
  const fullPath = path.resolve(BASE_DIR);
  
  if (!fs.existsSync(fullPath)) {
    throw new Error(`目录不存在: ${fullPath}`);
  }
  
  const files = fs.readdirSync(fullPath)
    .filter(f => f.startsWith('favorites导航_') && f.endsWith('.json'))
    .map(f => ({
      name: f,
      date: f.match(/favorites导航_(\d{4}-\d{2}-\d{2})/)?.[1] || '1900-01-01',
      path: path.join(fullPath, f)
    }))
    .sort((a, b) => b.date.localeCompare(a.date));
  
  if (files.length === 0) {
    // 创建空文件
    const today = new Date().toISOString().split('T')[0];
    const newFile = path.join(fullPath, `favorites导航_${today}.json`);
    fs.writeFileSync(newFile, '[]', 'utf8');
    return newFile;
  }
  
  return files[0].path;
}

/**
 * 读取收藏夹数据
 */
function readData() {
  const file = findLatestFile();
  const content = fs.readFileSync(file, 'utf8');
  
  try {
    const data = JSON.parse(content);
    // 确保是数组格式
    return Array.isArray(data) ? data : data.links || [];
  } catch (e) {
    console.error('解析 JSON 失败:', e);
    return [];
  }
}

/**
 * 保存收藏夹数据
 */
function saveData(links) {
  const today = new Date().toISOString().split('T')[0];
  const fullPath = path.resolve(BASE_DIR);
  const newFile = path.join(fullPath, `favorites导航_${today}.json`);
  
  fs.writeFileSync(newFile, JSON.stringify(links, null, 2), 'utf8');
  return newFile;
}

/**
 * 查找链接
 * @param {Object} criteria - 查找条件
 * @param {string} criteria.keyword - 关键词（搜索标题、URL、别名、描述）
 * @param {string} criteria.category - 分类
 * @param {string} criteria.tag - 标签
 * @param {string} criteria.status - 状态（unread/important/todo）
 */
function findLinks(criteria = {}) {
  const links = readData();
  
  return links.filter(link => {
    // 关键词搜索
    if (criteria.keyword) {
      const keyword = criteria.keyword.toLowerCase();
      const text = `${link.title} ${link.url} ${link.alias || ''} ${link.description || ''}`.toLowerCase();
      if (!text.includes(keyword)) return false;
    }
    
    // 分类匹配
    if (criteria.category !== undefined) {
      if (link.category !== criteria.category) return false;
    }
    
    // 标签匹配（支持字符串或数组）
    if (criteria.tag) {
      const tags = Array.isArray(criteria.tag) ? criteria.tag : [criteria.tag];
      const hasTag = tags.some(t => link.tags.includes(t));
      if (!hasTag) return false;
    }
    
    // 状态匹配
    if (criteria.status) {
      if (link.status !== criteria.status) return false;
    }
    
    // 是否收藏
    if (criteria.starred !== undefined) {
      if (!!link.starred !== criteria.starred) return false;
    }
    
    return true;
  });
}

/**
 * 添加单个链接
 * @param {Object} link - 链接信息
 * @returns {Object} 添加后的链接对象
 */
function addLink(link) {
  const links = readData();
  
  // 检查重复
  const exists = links.find(l => l.url === link.url);
  if (exists) {
    throw new Error(`链接已存在: ${exists.title} (${exists.url})`);
  }
  
  // 创建新链接对象
  const newLink = {
    id: Date.now().toString(),
    scene: 'all',
    category: link.category || '',
    subCategory: link.subCategory || null,
    title: link.title,
    url: link.url,
    description: link.description || '',
    alias: link.alias || '',
    status: link.status || (link.category ? null : 'unread'),
    tags: link.tags || [],
    starred: link.starred || false
  };
  
  links.push(newLink);
  const savedFile = saveData(links);
  
  console.log(`✅ 已添加: ${newLink.title}`);
  console.log(`   分类: ${newLink.category || '未分类（稍后阅读）'}`);
  console.log(`   保存到: ${savedFile}`);
  
  return newLink;
}

/**
 * 批量添加链接
 * @param {Array} newLinks - 链接数组
 */
function batchAddLinks(newLinks) {
  const links = readData();
  const results = [];
  const errors = [];
  
  for (const link of newLinks) {
    try {
      // 检查重复
      const exists = links.find(l => l.url === link.url);
      if (exists) {
        errors.push(`跳过重复: ${link.title}`);
        continue;
      }
      
      const newLink = {
        id: (Date.now() + Math.random()).toString(),
        scene: 'all',
        category: link.category || '',
        subCategory: link.subCategory || null,
        title: link.title,
        url: link.url,
        description: link.description || '',
        alias: link.alias || '',
        status: link.status || (link.category ? null : 'unread'),
        tags: link.tags || [],
        starred: link.starred || false
      };
      
      links.push(newLink);
      results.push(newLink);
    } catch (e) {
      errors.push(`添加失败 ${link.title}: ${e.message}`);
    }
  }
  
  const savedFile = saveData(links);
  
  console.log(`✅ 批量添加完成: ${results.length} 个成功, ${errors.length} 个失败`);
  errors.forEach(e => console.log(`   ⚠️ ${e}`));
  
  return { results, errors, savedFile };
}

/**
 * 更新链接
 * @param {string} id - 链接ID
 * @param {Object} updates - 要更新的字段
 */
function updateLink(id, updates) {
  const links = readData();
  const index = links.findIndex(l => l.id === id);
  
  if (index === -1) {
    throw new Error(`链接不存在: ${id}`);
  }
  
  links[index] = { ...links[index], ...updates };
  const savedFile = saveData(links);
  
  console.log(`✅ 已更新: ${links[index].title}`);
  return links[index];
}

/**
 * 批量更新
 * @param {Function} filterFn - 筛选函数
 * @param {Object} updates - 更新内容
 */
function batchUpdate(filterFn, updates) {
  const links = readData();
  let count = 0;
  
  links.forEach((link, index) => {
    if (filterFn(link)) {
      links[index] = { ...link, ...updates };
      count++;
    }
  });
  
  const savedFile = saveData(links);
  console.log(`✅ 批量更新完成: ${count} 个链接`);
  
  return count;
}

/**
 * 删除链接
 * @param {string} id - 链接ID
 */
function deleteLink(id) {
  const links = readData();
  const index = links.findIndex(l => l.id === id);
  
  if (index === -1) {
    throw new Error(`链接不存在: ${id}`);
  }
  
  const deleted = links.splice(index, 1)[0];
  const savedFile = saveData(links);
  
  console.log(`✅ 已删除: ${deleted.title}`);
  return deleted;
}

/**
 * 获取统计信息
 */
function getStats() {
  const links = readData();
  
  const categories = {};
  const tags = {};
  let unread = 0;
  let starred = 0;
  
  links.forEach(link => {
    // 分类统计
    const cat = link.category || '未分类';
    categories[cat] = (categories[cat] || 0) + 1;
    
    // 标签统计
    link.tags.forEach(tag => {
      tags[tag] = (tags[tag] || 0) + 1;
    });
    
    // 稍后阅读
    if (link.status === 'unread' || !link.category) unread++;
    
    // 收藏
    if (link.starred) starred++;
  });
  
  return {
    total: links.length,
    categories: Object.entries(categories).sort((a, b) => b[1] - a[1]),
    tags: Object.entries(tags).sort((a, b) => b[1] - a[1]).slice(0, 20),
    unread,
    starred
  };
}

/**
 * 智能查找（模糊匹配）
 * @param {string} query - 搜索词
 * @param {number} limit - 返回数量限制
 */
function smartSearch(query, limit = 10) {
  const links = readData();
  const q = query.toLowerCase();
  
  // 计算相关度分数
  const scored = links.map(link => {
    let score = 0;
    const title = link.title.toLowerCase();
    const url = link.url.toLowerCase();
    const desc = (link.description || '').toLowerCase();
    const alias = (link.alias || '').toLowerCase();
    
    // 标题匹配权重最高
    if (title === q) score += 100;
    else if (title.startsWith(q)) score += 80;
    else if (title.includes(q)) score += 60;
    
    // URL匹配
    if (url.includes(q)) score += 40;
    
    // 别名匹配
    if (alias.includes(q)) score += 50;
    
    // 描述匹配
    if (desc.includes(q)) score += 20;
    
    // 标签匹配
    link.tags.forEach(tag => {
      if (tag.toLowerCase().includes(q)) score += 30;
    });
    
    return { link, score };
  });
  
  // 按分数排序，过滤0分的
  return scored
    .filter(s => s.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map(s => s.link);
}

// 导出函数
module.exports = {
  readData,
  saveData,
  findLinks,
  addLink,
  batchAddLinks,
  updateLink,
  batchUpdate,
  deleteLink,
  getStats,
  smartSearch,
  findLatestFile
};

// 如果直接运行此文件，执行测试
if (require.main === module) {
  console.log('📊 Favorites Manager 测试运行\n');
  
  const stats = getStats();
  console.log('统计信息:');
  console.log(`  总链接: ${stats.total}`);
  console.log(`  稍后阅读/未分类: ${stats.unread}`);
  console.log(`  收藏: ${stats.starred}`);
  console.log(`  分类数: ${stats.categories.length}`);
  console.log('\n热门分类:');
  stats.categories.slice(0, 5).forEach(([name, count]) => {
    console.log(`  - ${name}: ${count}`);
  });
}
