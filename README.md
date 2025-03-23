# arXivDaily

自动获取 arXiv 的最新文章，通过关键词和 arXiv API

## 说明

直接运行 run.py

即可根据 keywords 获取到从今天凌晨开始，往前推移 pastDays 天的文章，文章数量上限为 total_results。结果会直接输出成 json 格式。

## 未来计划

- [ ] 将配置信息另存为 yaml 文件，从文件中加载配置
- [ ] 关键词检索方式改变，一个主题匹配多个关键词
- [ ] 检索结果保存到 json 文件中
- [ ] 检索结果按照主题名保存，保存格式为 markdown ，用表格展示
- [ ] 支持更多的检索过滤条件，不只是 all
- [ ] 加入翻译 API
- [ ] 自动执行：部署到服务器并开启定时任务 / 使用 Github Action
- [ ] ...