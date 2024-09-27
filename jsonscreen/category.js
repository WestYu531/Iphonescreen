const store = require('app-store-scraper');
const fs = require('fs');
const path = require('path');

// 定义保存 JSON 文件的路径
const saveDirectory = '/Users/westyu/Desktop/cccjson';

// 检查并确保目录存在
if (!fs.existsSync(saveDirectory)) {
  fs.mkdirSync(saveDirectory, { recursive: true });
}

// 获取所有类别的前 200 个应用并保存到对应的 JSON 文件中
async function fetchAppsByCategoryAndSave() {
  // 获取所有类别 (category)
  const categories = store.category;
  
  for (const categoryKey in categories) {
    if (categories.hasOwnProperty(categoryKey)) {
      const categoryId = categories[categoryKey];

      try {
        // 获取当前类别的前200个应用
        const apps = await store.list({
          category: categoryId,  // 使用类别ID
          num: 200  // 获取前200个应用
        });

        // 定义文件名
        const fileName = `${categoryKey}_apps.json`;
        const filePath = path.join(saveDirectory, fileName);

        // 将结果保存到JSON文件
        fs.writeFile(filePath, JSON.stringify(apps, null, 2), (err) => {
          if (err) throw err;
          console.log(`Saved ${categoryKey} apps to ${filePath}`);
        });
      } catch (error) {
        console.error(`Error fetching apps for category ${categoryKey}:`, error);
      }
    }
  }
}

// 调用函数获取数据并保存
fetchAppsByCategoryAndSave();