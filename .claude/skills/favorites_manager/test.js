/**
 * Favorites Manager 测试脚本
 * 运行：node test.js
 */

const fm = require('./favorites.js');

console.log('🧪 Favorites Manager 测试\n');
console.log('=' .repeat(50));

try {
  // 1. 读取数据
  console.log('\n1️⃣ 读取数据');
  const links = fm.readData();
  console.log(`   ✅ 读取成功，共 ${links.length} 个链接`);
  
  // 2. 统计信息
  console.log('\n2️⃣ 统计信息');
  const stats = fm.getStats();
  console.log(`   📊 总计: ${stats.total}`);
  console.log(`   ⏰ 待整理: ${stats.unread}`);
  console.log(`   ⭐ 收藏: ${stats.starred}`);
  console.log(`   📁 分类: ${stats.categories.length} 个`);
  
  if (stats.categories.length > 0) {
    console.log('   📈 前5个分类:');
    stats.categories.slice(0, 5).forEach(([name, count]) => {
      console.log(`      - ${name}: ${count}`);
    });
  }
  
  // 3. 查找测试
  console.log('\n3️⃣ 查找测试');
  if (links.length > 0) {
    const firstLink = links[0];
    const results = fm.findLinks({ keyword: firstLink.title.slice(0, 5) });
    console.log(`   🔍 搜索 "${firstLink.title.slice(0, 5)}" 找到 ${results.length} 个结果`);
  }
  
  // 4. 智能搜索测试
  console.log('\n4️⃣ 智能搜索');
  if (links.length > 0) {
    const keyword = links[0].title.split(' ')[0] || 'a';
    const smart = fm.smartSearch(keyword, 5);
    console.log(`   🔮 智能搜索 "${keyword}" 找到 ${smart.length} 个结果`);
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('✅ 所有测试通过！\n');
  
} catch (error) {
  console.error('\n❌ 测试失败:', error.message);
  console.error(error.stack);
  process.exit(1);
}
